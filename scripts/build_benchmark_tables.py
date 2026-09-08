"""Compact benchmark summaries; preserve source rows and audit all aggregation."""
from pathlib import Path
import json
from decimal import Decimal, ROUND_HALF_UP

P=Path(__file__).resolve().parents[1]
export=json.loads((P/'artifacts/source_reports/benchmark_export.json').read_text())
tables={x['id']:x for x in export['simulation']}
pro=json.loads((P/'artifacts/external_libero_pro.json').read_text())
audit=[]

def name(s):
    if s.startswith('OpenWAM'):return r'R1'
    return {'π₀':r'$\pi_0$','π₀.₅':r'$\pi_{0.5}$','StarVLA-α':r'StarVLA-$\alpha$',
            'Cosmos-Policy':'Cosmos Policy'}.get(s,s)

def fmt(s,best=False):
    if s in ['—','-',None]:return r'\nr'
    return r'\textbf{'+s+'}' if best else s

def panel(t,indices,headers,title,include_jam=False,model_width='1.43in'):
    n=len(indices)+1
    rows=[r'\begin{tabularx}{\linewidth}{@{}p{'+model_width+'}'+('C'*len(indices))+r'@{}}',
          r'\toprule',r'\panelrow{'+str(n)+'}{'+title+'}',
          'Model & '+' & '.join(headers)+r' \\',r'\midrule']
    maxima=[]
    for i in indices:
        vals=[Decimal(r['cells'][i]['text']) for g in t['groups'] for r in g['rows'] if r['cells'][i]['text'] not in ['—','-']]
        maxima.append(max(vals))
    for gi,g in enumerate(t['groups']):
        if gi:rows.append(r'\midrule')
        for r in g['rows']:
            cells=[r['cells'][i]['text'] for i in indices]
            rendered=[fmt(s,s not in ['—','-'] and Decimal(s)==mx) for s,mx in zip(cells,maxima)]
            rows.append(name(r['model'])+' & '+' & '.join(rendered)+r' \\')
            audit.append({'table':t['id'],'model':r['model'],'indices':indices,'source_cells':cells})
    if include_jam:
        rows += [r'\midrule',r'\jamshade\textbf{JAM} & \multicolumn{'+str(n-1)+r'}{c}{\pendingresult} \\']
    rows += [r'\bottomrule',r'\end{tabularx}']
    return '\n'.join(rows)

def write(key,panels,caption,size=9.2,source=True):
    out=[r'\begin{table}[H]',r'\centering',r'\begingroup\fontsize{'+str(size)+'}{'+str(size+1.3)+r'}\selectfont',
         r'\setlength{\tabcolsep}{2.5pt}\renewcommand{\arraystretch}{'+('1.0' if key in ['bimanual','mobile'] else '1.08')+'}',
         '\n\\vspace{3pt}\n'.join(panels),r'\endgroup',r'\caption{'+caption+(' '+(r'Source: \refsource{}. Bold marks column maxima; blue rows await JAM evaluation.' if key in ['bimanual','mobile'] else r'Source: \refsource{}. \benchmarknote') if source else '')+'}',
         r'\label{tab:'+key+'}',r'\end{table}']
    (P/'Tables'/f'{key}.tex').write_text('\n'.join(out)+'\n')

specs=[
 ('libero','LIBERO',['Spatial','Object','Goal','Long','Mean'],
  r'\textbf{LIBERO task success.} The four suites measure spatial, object, goal, and long-horizon control.'),
 ('libero_plus','LIBERO-Plus',['Camera','Robot','Language','Light','Backgr.','Noise','Layout','Mean'],
  r'\textbf{LIBERO-Plus robustness.} Success percentages across seven perturbation axes; the mean retains the source aggregation.')]
for key,title,headers,caption in specs:
    write(key,[panel(tables[key],list(range(len(headers))),headers,title,True)],caption)

# The incomplete metric request defaults to the three overall VLABench metrics.
write('vlabench',[panel(tables['vlabench'],[15,16,17],['SR','PS','IS'],'VLABench',True)],
      r'\textbf{VLABench overall performance.} SR, PS, and IS denote task success, progress score, and intention score. Values retain the source-reported overall percentage scale.')

def pair(left,right):
    return (r'\begin{minipage}[t]{.51\linewidth}\vspace{0pt}'+'\n'+left+'\n'+r'\end{minipage}\hfill'+
            '\n'+r'\begin{minipage}[t]{.47\linewidth}\vspace{0pt}'+'\n'+right+'\n'+r'\end{minipage}')

left=panel(tables['robotwin'],[0,1,2],['Clean','Rand.','Mean'],'A. RoboTwin2.0-Full',True,'1.25in')
right=panel(tables['robodojo'],[12,13],['SR','Score'],'B. RoboDojo',True,'1.40in')
write('bimanual',[pair(left,right)],
      r'\textbf{Bimanual manipulation.} RoboTwin2.0-Full reports clean and randomized success; RoboDojo reports overall success rate (SR) and task score.',size=8.4)

left=panel(tables['robocasa_365'],[0,1,2,3],['Atomic','Seen','Unseen','Mean'],'A. RoboCasa365',True,'1.20in')
right=panel(tables['ebench'],[6,7],['SR','Score'],'B. EBench',True,'1.40in')
write('mobile',[pair(left,right)],
      r'\textbf{Mobile manipulation.} RoboCasa365 separates atomic skills from seen and unseen compositions. EBench reports overall success rate (SR) and task score.',size=8.4)

# Requested suite summaries are derived from the published perturbation rates.
# Total remains the source value; no missing condition is replaced with zero.
lines=[r'\begin{tabularx}{\linewidth}{@{}p{1.43in}CCCCC@{}}',r'\toprule',
       r'\panelrow{6}{LIBERO-PRO}',r'Model & Goal & Spatial & Long & Object & Total \\',r'\midrule']
derived=[]
for r in pro['rows']:
    suites=[];details=[]
    for i,suite in enumerate(pro['suites']):
        source_values=r['percent_cells'][5*i:5*i+5]
        valid=[Decimal(v) for v in source_values if v is not None]
        mean=sum(valid)/len(valid);display=f'{mean.quantize(Decimal("0.1"),rounding=ROUND_HALF_UP):.1f}'
        suites.append(display);details.append({'suite':suite,'source_indices':list(range(5*i,5*i+5)),
                   'n_reported':len(valid),'macro_mean_percent':str(mean),'display':display})
    total=f'{Decimal(r["percent_cells"][-1]):.1f}'
    label={'Pi0':r'$\pi_0$','Pi0.5':r'$\pi_{0.5}$','Molmoact':'MolmoAct','x-VLA':'X-VLA'}.get(r['model'],r['model'])
    incomplete=any(d['n_reported']<5 for d in details)
    if incomplete:label+=r'\textsuperscript{*}'
    lines.append(label+' & '+' & '.join(suites+[total])+r' \\')
    derived.append({'model':r['model'],'suites':details,'reported_total_percent':r['percent_cells'][-1],'display_total':total})
lines += [r'\midrule',r'\jamshade\textbf{JAM} & \multicolumn{5}{c}{\pendingresult} \\',r'\bottomrule',r'\end{tabularx}']
write('libero_pro',['\n'.join(lines)],
      r'\textbf{LIBERO-PRO suite performance.} Suite values are macro-averages of published perturbation percentages; Total is copied from the \prosource{}. \textsuperscript{*}Averages cover four reported perturbations, with environment tests unreported. The blue JAM row awaits evaluation.',source=False)
(P/'artifacts/libero_pro_aggregation.json').write_text(json.dumps({'method':'Unweighted mean of reported perturbation percentages, rounded half up to one decimal; source-reported Total retained','rows':derived},indent=2)+'\n')
(P/'artifacts/rendered_baseline_cells.json').write_text(json.dumps(audit,indent=2)+'\n')
print('Built compact single-arm, bimanual and mobile benchmark tables.')
