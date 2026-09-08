#!/usr/bin/env python3
"""Evidence and manuscript checks. Run after build_artifacts.py and compilation."""
from pathlib import Path
import json,re,hashlib,statistics,sys
from decimal import Decimal, ROUND_HALF_UP
from html.parser import HTMLParser
from pypdf import PdfReader
P=Path(__file__).resolve().parents[1]
errors=[]
def check(ok,msg):
 if not ok:errors.append(msg)
files=[P/'main.tex']+list((P/'Sections').glob('*.tex'))+list((P/'Figures').glob('*.tex'))+list((P/'Tables').glob('*.tex'))
text='\n'.join(f.read_text() for f in files)
labels=re.findall(r'\\label\{([^}]+)\}',text)
check(len(labels)==len(set(labels)),'Duplicate labels')
refs=re.findall(r'\\(?:ref|cref|Cref)\{([^}]+)\}',text)
check(set(refs)<=set(labels),'Undefined source references: '+str(set(refs)-set(labels)))
sections=[]
for n in range(1,7):
 f=next((P/'Sections').glob(f'{n}_*.tex'));sections.extend(re.findall(r'\\section\{([^}]+)\}',f.read_text()))
check(len(sections)==6,'Exactly six main sections required')
for name,want in [('1_Introduction.tex',(4,5)),('2_RelatedWork.tex',(3,3))]:
 s=(P/'Sections'/name).read_text();s=re.sub(r'\\section\{[^}]+\}','',s).strip();para=[p for p in re.split(r'\n\s*\n',s) if p.strip()]
 check(want[0]<=len(para)<=want[1],f'{name}: {len(para)} paragraphs')
 check('\\subsection' not in s,f'{name}: subsection found')
 if name.startswith('1_'):check(not re.search(r'\d|\$|\\begin\{(?:equation|table)\}',re.sub(r'\\cite\w*\{[^}]*\}','',s)), 'Intro contains a number or math')
s=(P/'Sections/5_Experiments.tex').read_text()
check('$' not in s and not re.search(r'\\begin\{(?:equation|align)',s),'Experiments contains formulas')
setup=s.split(r'\subsection{Experimental setup}',1)[1].split(r'\subsection{',1)[0].strip()
setup_paragraphs=[p for p in re.split(r'\n\s*\n',setup) if p.strip()]
check(len(setup_paragraphs)==2, 'Experimental setup must have exactly two paragraphs')
check(not (P/'Tables/data.tex').exists() and 'tab:data}' not in text, 'Old dataset inventory table remains')
benchmarks=['libero_plus','libero_pro','vlabench','bimanual','mobile']
for name in benchmarks+['libero','joint_analysis','data_scaling']:
 table=(P/'Tables'/f'{name}.tex').read_text()
 check(r'\begin{tabularx}{\linewidth}' in table,'Table must fill text width: '+name)
 check(r'\jamshade' in table and r'\panelrow' in table,'Table lacks JAM highlighting or hierarchy: '+name)
 if name in benchmarks+['libero']:
  check(table.count(r'\jamshade')==(2 if name in ['bimanual','mobile'] else 1),'Benchmark requires one JAM row: '+name)
  check(r'\pendingresult' in table and r'\target{' not in table,'Benchmark JAM row must await a measured artifact: '+name)
for name in benchmarks:check(s.count(r'\input{Tables/'+name+'}')==1,'Missing or repeated main benchmark: '+name)
check(s.index(r'\input{Tables/mobile}')<s.index(r'\label{fig:training}'),'Training dynamics must follow all main benchmark tables')
check('fig:mixture' not in text and 'fig:foundation' not in text,'Removed figures remain referenced')
check(not (P/'Figures/data_mixture.pdf').exists(),'Removed mixture figure remains')
check('Next admission' not in text,'Dataset roadmap remains in manuscript')
check('Model & Goal & Spatial & Long & Object & Total' in (P/'Tables/libero_pro.tex').read_text(),'PRO summary columns')
check('Model & SR & PS & IS' in (P/'Tables/vlabench.tex').read_text(),'VLABench overall columns')
check('JAM direct' not in text,'Ambiguous direct label remains')
check('Without embodied pretraining' in (P/'Tables/joint_analysis.tex').read_text(),'Initialization control missing')
# URLs retain exact provenance. Naming rules apply to displayed prose.
prose=re.sub(r'https?://[^}\s]+','',text)
prose=re.sub(r'%[^\n]*','',prose)
for bad in ['OpenWAM','EVA','—','---','“','”','"','TODO','TBD']:
 check(bad not in prose,f'Forbidden display text: {bad}')
bib=(P/'jam.bib').read_text();keys=set(re.findall(r'@\w+\{([^,]+)',bib));cites=set()
for group in re.findall(r'\\cite\w*\{([^}]+)\}',text):cites.update(group.split(','))
check(cites<=keys,'Missing citations '+str(cites-keys))
for row in json.load(open(P/'artifacts/provenance.json'))['files']:
 if 'published' in row:check(hashlib.sha256((P/row['published']).read_bytes()).hexdigest()==row['published_sha256'],'Evidence hash mismatch '+row['published'])
summary=json.load(open(P/'artifacts/measurements/e0_libero_bi_summary.json'))
d=[json.loads(l) for l in (P/'artifacts/measurements/e0_libero_bi.jsonl').read_text().splitlines()]
check(len(d)==summary['n_log_points'] and d[-1]['step']==summary['steps'],'Training summary shape mismatch')
for k in ['world','action','consequence','total']:
 key='loss/'+k;mean=statistics.mean(r[key] for r in d[-max(1,len(d)//10):]);check(abs(mean-summary[key]['final_mean_last10pct'])<1e-7,'Summary mean mismatch '+key)
plan=json.load(open(P/'experiments/layout_targets.json'));check(plan['status']=='planned','Layout target status changed')
for name in ['joint_analysis','data_scaling']:
 s=(P/'Tables'/f'{name}.tex').read_text();check('PLANNED-VALUE' in s and '\\targetnote' in s and '\\target{' in s,'Unmarked targets '+name)

# Verify source rows and each rendered cell from the pinned archive every run.
external=json.load(open(P/'artifacts/external_baselines.json'))
raw=(P/'artifacts/source_reports/benchmark_export.json').read_bytes();source=json.loads(raw)
check(hashlib.sha256(raw).hexdigest()==external['source_sha256'],'External archive hash mismatch')
external_count=0
for row in external['rows']:
 node=source
 for key in row['source_pointer'].split('/')[1:]:node=node[int(key)] if isinstance(node,list) else node[key]
 check([c['text'] for c in node['cells']]==[c['text'] for c in row['cells']],'External row mismatch: '+row['source_pointer'])
 check(node['model']==row['original_model'],'Original baseline label mismatch')
 external_count+=1
st={x['id']:x for x in source['simulation']};seen=set();cell_count=0
for row in json.load(open(P/'artifacts/rendered_baseline_cells.json')):
 original=next(r for g in st[row['table']]['groups'] for r in g['rows'] if r['model']==row['model'])
 check(row['source_cells']==[original['cells'][i]['text'] for i in row['indices']],'Rendered-cell audit mismatch')
 seen.add((row['table'],row['model']));cell_count+=len(row['indices'])
# All source baselines in all six selected export benchmarks must be shown.
expected={(key,r['model']) for key in ['libero','libero_plus','vlabench','robotwin','robocasa_365','robodojo','ebench'] for g in st[key]['groups'] for r in g['rows']}
check(seen==expected,'Missing benchmark baseline rows')
pro=json.load(open(P/'artifacts/external_libero_pro.json'))
excerpt=(P/pro['local_source']).read_bytes()
check(hashlib.sha256(excerpt).hexdigest()==pro['excerpt_sha256'],'PRO source excerpt hash mismatch')
class Rows(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=[];self.cell=None
 def handle_starttag(self,tag,attrs):
  if tag=='tr':self.row=[]
  if tag in ['td','th']:self.cell=''
 def handle_data(self,data):
  if self.cell is not None:self.cell+=data
 def handle_endtag(self,tag):
  if tag in ['td','th'] and self.cell is not None:self.row.append(self.cell.strip());self.cell=None
  if tag=='tr':self.rows.append(self.row)
parsed=Rows();parsed.feed(excerpt.decode())
for row in pro['rows']:
 orig=next(r for r in parsed.rows if r and r[0]==row['model'])
 check(orig[1:]==row['source_cells'],'PRO source cells mismatch: '+row['model'])
 check(len(row['percent_cells'])==21,'PRO result shape')
 for src,pct in zip(row['source_cells'],row['percent_cells']):
  check((pct is None and src=='-') or (pct is not None and Decimal(pct)==Decimal(src)*100),'PRO percentage conversion')

aggregation=json.load(open(P/'artifacts/libero_pro_aggregation.json'))
for row in aggregation['rows']:
 original=next(r for r in pro['rows'] if r['model']==row['model'])
 for i,entry in enumerate(row['suites']):
  values=[Decimal(v) for v in original['percent_cells'][i*5:i*5+5] if v is not None]
  mean=sum(values)/len(values)
  check(Decimal(entry['macro_mean_percent'])==mean,'PRO macro mean '+row['model'])
  check(entry['display']==f'{mean.quantize(Decimal("0.1"),rounding=ROUND_HALF_UP):.1f}','PRO rounding '+row['model'])
  check(entry['n_reported']==len(values),'PRO missingness')
 check(Decimal(row['display_total'])==Decimal(original['percent_cells'][-1]),'PRO reported Total changed')

inv=json.load(open(P/'artifacts/data_inventory.json'));counts=inv['source_counts'];den=sum(n**inv['temperature'] for n in counts.values())
check(len(counts)==7 and inv['active_from_update']==10500,'Consumed-mixture stage changed')
for k,n in counts.items():check(abs(inv['probabilities'][k]-n**inv['temperature']/den)<1e-12,'Mixture probability '+k)
check(inv['temporal_audit']['egodex_train_hz']==10,'EgoDex training timing')
foundation=[json.loads(x) for x in (P/'artifacts/measurements/jam_base_v1.jsonl').read_text().splitlines()]
check(foundation[-1]['step']==10501,'Foundation snapshot mismatch')
check('10,501' in (P/'Tables/evidence_macros.tex').read_text(),'Foundation macro mismatch')
for n in ['droid','egodex']:
 d=json.load(open(P/f'artifacts/measurements/analysis/base_v1_m5100/probes_{n}.json'))
 check(d['config']['s_world']==.5 and d['config']['s_action']==1,'Probe visibility differs from caption')
 check(d['config']['n_boot']==1000 and d['config']['max_windows']==4000,'Probe sampling differs from caption')
 check(set(d['layers'])=={'5','10','15','20','25','29'},'Probe layer sweep differs')
cf=json.load(open(P/'artifacts/measurements/analysis/base_v1_m5100/counterfactual_libero.json'))
for key in ['donor','hold','shuffled_time']:
 lo,hi=cf['conditions'][key]['sensitivity_vs_true']['ci'];check(lo<=0<=hi,'Sensitivity statement must be reviewed')
check(cf['n_windows']==300,'Sensitivity sample count')
comparison=json.load(open(P/'artifacts/representation_comparison.json'))
layers=comparison['layers']
check(layers==[5,10,15,20,25,29],'Derived comparison must include every sampled depth')
for source,digest in comparison['source_sha256'].items():
 check(hashlib.sha256((P/source).read_bytes()).hexdigest()==digest,'Representation source hash '+source)
for label,folder,suffix in [('JAM','base_v1_m5100',''),('Video prior','floors','_bare_prior'),('Random init.','floors','_random_init')]:
 action=json.load(open(P/f'artifacts/measurements/analysis/{folder}/probes_droid{suffix}.json'))
 consequence=json.load(open(P/f'artifacts/measurements/analysis/{folder}/probes_egodex{suffix}.json'))
 check(comparison['readouts'][label]['action_r2']==[action['layers'][str(i)]['actions']['r2'] for i in layers],'Action readout '+label)
 check(comparison['readouts'][label]['consequence_ade']==[consequence['layers'][str(i)]['consequence']['metrics']['ade'] for i in layers],'Consequence readout '+label)
 if label=='JAM':check(comparison['copy_first_consequence_ade']==consequence['targets']['consequence']['floors']['copy_first']['ade'],'Copy-first floor')
jam=comparison['readouts']['JAM'];prior=comparison['readouts']['Video prior']
for i in range(len(layers)):
 check(abs(comparison['jam_action_r2_gain_vs_video_prior'][i]-(jam['action_r2'][i]-prior['action_r2'][i]))<1e-12,'Action gain derivation')
 check(abs(comparison['jam_consequence_ade_reduction_percent_vs_video_prior'][i]-100*(prior['consequence_ade'][i]-jam['consequence_ade'][i])/prior['consequence_ade'][i])<1e-12,'Consequence gain derivation')
check(comparison['jam_beats_copy_first_layers']==[layers[i] for i,v in enumerate(jam['consequence_ade']) if v<comparison['copy_first_consequence_ade']],'Copy-first comparison')
qa=json.load(open(P/'artifacts/figure_qa.json'))
check(len(qa)==4 and {x['figure'] for x in qa}=={'training','representation','action_sensitivity','scaling_targets'} and all(x['font']=='DejaVu Serif' and x['text_bounds']=='PASS' for x in qa),'Figure typography or bounds audit')
verify_external='--verify-external' in sys.argv
if verify_external:
 try:
  import urllib.request
  for manifest in [external,pro]:
   with urllib.request.urlopen(manifest['source_url'],timeout=30) as response:remote=response.read()
   check(hashlib.sha256(remote).hexdigest()==manifest['source_sha256'],'Remote source hash differs: '+manifest['source_url'])
 except Exception as exc:check(False,'External verification failed: '+str(exc))
aux=(P/'main.aux').read_text() if (P/'main.aux').exists() else ''
end=re.search(r'\\newlabel\{page:mainend\}\{\{[^}]*\}\{(\d+)\}',aux)
check(end is not None, 'Compile before validation: main-page label unavailable')
main_pages=int(end.group(1)) if end else 0
check(0<main_pages<=12, f'Main text is {main_pages} pages; maximum is 12')
if (P/'main.pdf').exists():
 pdf=PdfReader(P/'main.pdf')
 check('Learning an interaction through its commands' in pdf.pages[0].extract_text(),'Teaser is missing from the homepage')
 check('Conclusion' in pdf.pages[main_pages-1].extract_text(),'Main-page endpoint does not contain Conclusion')
 check('References' in pdf.pages[main_pages].extract_text(),'References must start after main text')
else:check(False,'Compiled PDF missing')
if (P/'main.log').exists():
 log=(P/'main.log').read_text(errors='replace')
 for bad in ['undefined references','undefined citations','Citation `','Overfull \\hbox','Overfull \\vbox','Missing character:']:
  check(bad not in log,'Compile log: '+bad)
if errors:
 print('\n'.join('FAIL: '+e for e in errors));sys.exit(1)
print(f'PASS: {main_pages} main pages (maximum 12); {len(setup_paragraphs)} setup paragraphs; {len(sections)} main sections; {len(labels)} unique labels; {len(cites)} verified citation keys; evidence hashes, summary means, and target markers valid.')

print(f'PASS: {external_count} archived export rows; {len(seen)} displayed export baselines; {cell_count} source cells; six official PRO rows; seven-source mixture and measured probe settings verified.')
if verify_external:print('PASS: both external source hashes reverified online.')
