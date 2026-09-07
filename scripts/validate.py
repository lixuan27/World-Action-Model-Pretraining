#!/usr/bin/env python3
"""Evidence and manuscript checks. Run after build_artifacts.py and compilation."""
from pathlib import Path
import json,re,hashlib,statistics,sys
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
for name in ['main_results','coupling','composition','ood','mechanism']:
 s=(P/'Tables'/f'{name}.tex').read_text();check('PLANNED-VALUE' in s and '\\targetnote' in s and '\\target{' in s,'Unmarked targets '+name)
if (P/'main.log').exists():
 log=(P/'main.log').read_text(errors='replace')
 for bad in ['undefined references','undefined citations','Citation `','Overfull \\hbox','Overfull \\vbox','Missing character:']:
  check(bad not in log,'Compile log: '+bad)
if errors:
 print('\n'.join('FAIL: '+e for e in errors));sys.exit(1)
print(f'PASS: {len(sections)} main sections; {len(labels)} unique labels; {len(cites)} verified citation keys; evidence hashes, summary means, and target markers valid.')
