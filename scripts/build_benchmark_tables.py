"""One complete table per benchmark; preserve every published baseline cell."""
from pathlib import Path
import json
from decimal import Decimal

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

def panel(t,indices,headers,title,include_jam=False):
    n=len(indices)+1
    rows=[r'\begin{tabularx}{\linewidth}{@{}p{1.43in}'+('C'*len(indices))+r'@{}}',
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
         r'\setlength{\tabcolsep}{2.5pt}\renewcommand{\arraystretch}{1.08}',
         '\n\\vspace{3pt}\n'.join(panels),r'\endgroup',r'\caption{'+caption+(' '+r'Source: \refsource{}. \benchmarknote' if source else '')+'}',
         r'\label{tab:'+key+'}',r'\end{table}']
    (P/'Tables'/f'{key}.tex').write_text('\n'.join(out)+'\n')

specs=[
 ('libero','LIBERO',['Spatial','Object','Goal','Long','Mean'],
  r'\textbf{LIBERO task success.} The four suites measure spatial, object, goal, and long-horizon control.'),
 ('libero_plus','LIBERO-Plus',['Camera','Robot','Language','Light','Backgr.','Noise','Layout','Mean'],
  r'\textbf{LIBERO-Plus robustness.} Success percentages across all seven perturbation axes; the reported mean retains the source aggregation.'),
 ('robotwin','RoboTwin2.0-Full',['Clean','Randomized','Mean'],
  r'\textbf{RoboTwin2.0-Full bimanual control.} Success percentages after adaptation on the Full training mixture. Clean-to-randomized adaptation is a separate protocol.'),
 ('robocasa_365','RoboCasa365',['Atomic','Composite seen','Composite unseen','Mean'],
  r'\textbf{RoboCasa365 household manipulation.} The full-suite protocol separates atomic skills from seen and unseen compositions.')]
for key,title,headers,caption in specs:
    write(key,[panel(tables[key],list(range(len(headers))),headers,title,True)],caption)

t=tables['vlabench'];panels=[]
for j,(metric,abbr) in enumerate([('Task success','SR'),('Progress score','PS'),('Intention score','IS')]):
    panels.append(panel(t,list(range(j,18,3)),['In-dist.','Category','Common-sense','Instruction','Texture','Mean'],
                        chr(65+j)+'. '+metric+' ('+abbr+')',j==2))
write('vlabench',panels,
      r'\textbf{VLABench semantic and visual generalization.} SR, PS, and IS retain the benchmark\textquotesingle s task-success, progress, and intention metrics across five settings. All values use the source\textquotesingle s percentage scale.')

t=tables['robodojo'];panels=[]
for j,metric in enumerate(['Task success (SR)','Task score']):
    panels.append(panel(t,list(range(j,14,2)),['Standard','Random','Precision','Long','Memory','Open','Mean'],
                        chr(65+j)+'. '+metric,j==1))
write('robodojo',panels,
      r'\textbf{RoboDojo capability profile.} Standard and Random denote the two generalization settings; Long denotes long-horizon tasks. Success and partial task score follow the source scale.',size=9.0)

# LIBERO-PRO is absent from the requested website. Its own maintainers publish
# a four-suite, five-perturbation leaderboard; keep their totals and missingness.
panels=[]
for section in range(2):
    total=section==1;n=12 if total else 11
    groupnames=pro['suites'][section*2:section*2+2]
    lines=[r'\begin{tabularx}{\linewidth}{@{}p{.92in}'+('C'*(n-1))+r'@{}}',r'\toprule',
           r'\panelrow{'+str(n)+'}{'+('A. Goal and spatial control' if not total else 'B. Long-horizon and object control')+'}',
           r'Model & \multicolumn{5}{c}{'+groupnames[0]+r'} & \multicolumn{5}{c}{'+groupnames[1]+'}'+(' & Total' if total else '')+r' \\',
           r'\cmidrule(lr){2-6}\cmidrule(lr){7-11}',
           ' & '+' & '.join(['Obj.','Pos.','Sem.','Task','Env.']*2)+(' & Rep.' if total else '')+r' \\',r'\midrule']
    for r in pro['rows']:
        vals=r['percent_cells'][section*10:section*10+10]+([r['percent_cells'][-1]] if total else [])
        pretty=[fmt(None if v is None else f'{Decimal(v):.0f}') for v in vals]
        label={'Pi0':r'$\pi_0$','Pi0.5':r'$\pi_{0.5}$','Molmoact':'MolmoAct','x-VLA':'X-VLA'}.get(r['model'],r['model'])
        lines.append(label+' & '+' & '.join(pretty)+r' \\')
    if total:lines += [r'\midrule',r'\jamshade\textbf{JAM} & \multicolumn{11}{c}{\pendingresult} \\']
    lines += [r'\bottomrule',r'\end{tabularx}'];panels.append('\n'.join(lines))
write('libero_pro',panels,
      r'\textbf{LIBERO-PRO perturbation tests.} The \prosource{} reports normalized success, displayed here as percentages. Obj., Pos., Sem., and Env. denote object, position, semantic, and environment shifts. Reported totals are copied, including the differing coverage: MolmoAct, NORA, and X-VLA omit environment tests. \nr{} means unreported. The reference website has no PRO table. Pale blue identifies JAM; its results await evaluation.',size=8.7,source=False)

(P/'artifacts/rendered_baseline_cells.json').write_text(json.dumps(audit,indent=2)+'\n')
print('Built seven benchmark-specific tables with complete source baseline rows.')
