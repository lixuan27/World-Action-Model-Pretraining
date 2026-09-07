#!/usr/bin/env python3
"""Regenerate manuscript tables and vector figures from explicitly typed evidence."""
from pathlib import Path
import json, math, statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
P=Path(__file__).resolve().parents[1]
T=P/'Tables';F=P/'Figures'
def dump(n,d): (P/n).write_text(json.dumps(d,indent=2)+'\n')
def target(x): return r'\target{'+str(x)+'}'
def table(name,label,columns,rows,caption,planned=False,width=None):
    n=len(columns);fmt=width or ('l'+'r'*(n-1))
    body='\n'.join(' & '.join(row)+r' \\' for row in rows)
    result=r'\begin{table}[t]'+'\n'+r'\centering\small'+'\n'+r'\begin{tabular}{'+fmt+'}\n'+r'\toprule'+'\n'+' & '.join(columns)+r' \\'+ '\n'+r'\midrule'+'\n'+body+'\n'+r'\bottomrule'+'\n'+r'\end{tabular}'+'\n'+r'\caption{'+caption+(' '+r'\targetnote' if planned else '')+'}\n'+r'\label{'+label+'}\n'+r'\end{table}'+'\n'
    if planned:result='% PLANNED-VALUE: every JAM score in this table is a layout target.\n'+result
    (T/name).write_text(result)
logs={r:[json.loads(l) for l in (P/f'artifacts/measurements/{r}.jsonl').read_text().splitlines()] for r in ['jam_base_v1','e0_libero_bi']}
step=logs['jam_base_v1'][-1]['step']
(T/'evidence_macros.tex').write_text(r'\newcommand{\FoundationSteps}{'+f'{step:,}'+'}\n')
summary=json.load(open(P/'artifacts/measurements/e0_libero_bi_summary.json'))
print('Summary keys:',list(summary))
# The original summary is retained; the presentation is regenerated from its values.
metrics=summary.get('metrics',summary)
print('Metric structure:',list(metrics)[:8])
rows=[]
for k in ['world','action','consequence','total']:
 m=summary['loss/'+k];rows.append([k.capitalize(),f'{m["first"]:.4f}',f'{m["final_mean_last10pct"]:.4f}'])
table('optimization.tex','tab:optimization',['Objective','First logged batch','Final-window mean'],rows,r'\textbf{Measured joint optimization.} LIBERO direct adaptation, 20,000 updates. The final column averages the last 10\% of logged points using the archived training summary. These are training losses. All values come from \texttt{e0\_libero\_bi\_summary.json}; the initialization contains public video weights and a fresh agent.')
counts=[1674648,454690,738550];p=[n**.7 for n in counts];p=[x/sum(p) for x in p]
rows=[[n,f'{ct:,}',f'{pr*100:.1f}\\%',sup] for n,ct,pr,sup in zip(['DROID','BridgeData V2','EgoDex'],counts,p,['World + action','World + action','World + consequence'])]
table('data.tex','tab:data',['Active source','Training windows','Sampling','Supervision'],rows,r'\textbf{Which data contributes which signal?} Active cached windows after the episode holdout, as recorded in the project ledger. Probabilities apply temperature 0.7 to window counts; window duration follows each source\textquotesingle s native frame rate. The recipe is shared by the archived foundation-training segment. Additional acquired sources remain outside this table.',width='lrrl')
dump('artifacts/data_inventory.json',{'status':'recorded_inventory','source':'docs/experiment_ledger.md, 2026-09-07 snapshot','source_counts':dict(zip(['droid','bridge','egodex'],counts)),'temperature':.7,'probabilities':p})
ref=json.load(open(P/'artifacts/external_reference.json'));r1={r['table']:r for r in ref['rows']}
def external(t,c): return r1[t]['cells'][r1[t]['columns'].index(c)]['text']
# All target numbers are design-only values, kept separate from measured evidence.
plans={
'main':{'columns':['LIBERO avg.','RoboTwin Full avg.','VLABench avg. SR','RoboCasa target tasks'], 'rows':{'Direct adaptation':[97.2,74.5,24.8,12.4],'JAM pretraining + adaptation':[99.4,94.6,59.8,39.6]}},
'coupling':{'columns':['LIBERO success','LIBERO-Plus success','Action probe R-squared'],'rows':{'World-only pretraining':[94.0,42.0,.30],'Action-only pretraining':[95.0,45.0,.32],'Independent multitask':[96.1,47.6,.38],'Auxiliary, detached world features':[96.8,49.4,.40],'World-to-agent, attached':[97.0,51.7,.46],'JAM, reciprocal and attached':[97.2,53.8,.52]}},
'composition':{'columns':['LIBERO success','LIBERO-Plus success','Held-out consequence ADE'],'rows':{'Robot data':[98.4,74.2,.12],'Robot + human video':[98.9,82.6,.10],'Robot + human video and consequences':[99.4,90.2,.08]}},
'ood':{'columns':['Direct adaptation','JAM pretraining + adaptation'],'rows':{'Visual and layout shift: LIBERO-Plus':[53.8,90.2],'Initial-state shift: LIBERO-PRO':[26.0,46.8],'Task-instruction shift: LIBERO-PRO':[6.0,12.6],'Environment shift: RoboTwin randomized':[14.2,62.4],'Category shift: VLABench':[16.0,39.0],'Embodiment transfer: held-out platform':[28.0,42.0]}},
'mechanism':{'columns':['Comparison A','Comparison B'],'rows':{'World action probe, R-squared':[.40,.52],'World consequence probe, ADE':[.12,.08],'Paired action intervention, ADE':[.18,.10],'World prediction, perceptual distance':[.24,.20],'Predicted-consequence condition, ADE':[.10,.13]}},
'scaling':{'fractions':[.125,.25,.5,1.0],'subset_success':[62.0,72.0,83.0,90.2],'updates':[5000,15000,30000,45000,60000],'milestone_success':[54.0,67.0,78.0,85.0,90.2]}}
plans={'status':'planned','marker':'PLANNED-VALUE','meaning':'Layout design values awaiting measurement; not predictions, preregistered outcomes, or scientific evidence.','tables':plans}
plan_file=P/'experiments/layout_targets.json'
if plan_file.exists():
    plans=json.loads(plan_file.read_text())
    assert plans['status']=='planned', 'Layout generator only accepts explicitly planned data'
else:
    dump('experiments/layout_targets.json',plans)
pn=plans['tables']
rows=[[r'\multicolumn{5}{l}{\emph{External results, verbatim from R1; source protocols}}'],['R1',external('libero','Avg'),external('robotwin','Avg'),external('vlabench','Avg · SR'),external('robocasa_365','Avg')],[r'\midrule\multicolumn{5}{l}{\emph{Planned paired comparison; JAM values are layout targets}}']]
rows += [[k]+[target(x) for x in v] for k,v in pn['main']['rows'].items()]
table('main_results.tex','tab:main',['Initialization','LIBERO','RoboTwin','VLABench','RoboCasa365'],rows,r'\textbf{Does embodied pretraining improve downstream control?} Success percentages. The R1 row reproduces the source averages of \refsource{} exactly; these are measurements of that external system. JAM rows are planned layout targets. The external RoboCasa365 value is a full source average, whereas the current JAM protocol targets 50 tasks; protocol alignment is required for a direct comparison. The reference row therefore supplies context rather than a matched ranking.',True)
rows=[[k]+[target(x) for x in v] for k,v in pn['coupling']['rows'].items()]
table('coupling.tex','tab:coupling',['Pretraining computation','LIBERO','LIBERO-Plus','Action probe'],rows,r'\textbf{What does reciprocal learning add?} Planned comparison after the same downstream adaptation. The first two columns are success percentages; the probe reports R-squared. All arms receive matched clean conditions and data. Auxiliary supervision reads detached world features; the attached one-way arm permits action gradients into the world stream. Reciprocal coupling adds agent information to world queries. Appendix~\ref{app:controls} specifies the condition-matching requirement.',True)
rows=[[k]+[target(x) for x in v] for k,v in pn['composition']['rows'].items()]
table('composition.tex','tab:composition',['Pretraining data','LIBERO','LIBERO-Plus','Consequence ADE'],rows,r'\textbf{What does human motion supervision contribute?} Planned data-composition comparison with matched robot exposure. The human-video arm masks the consequence objective. The final arm includes projected hand-motion targets. Success is in percent; average displacement error (ADE) uses image-normalized coordinates on the same held-out episode list. A companion compute-matched run and a label-density sweep separate supervision from additional updates.',True)
rows=[[k]+[target(x) for x in v] for k,v in pn['ood']['rows'].items()]
table('ood.tex','tab:ood',['Shift and evaluation','Direct','Pretrained'],rows,r'\textbf{Where does pretraining transfer?} Planned success percentages under paired evaluation resets. RoboTwin reports the randomized test partition after clean-only adaptation, distinct from Full-mixture training. Held-out embodiment transfer requires an explicitly excluded platform, a frozen pretraining split, and the same downstream demonstration budget for both initializations. Each row is a separate protocol rather than a shared aggregate.',True)
rows=[[k]+[target(x) for x in v] for k,v in pn['mechanism']['rows'].items()]
table('mechanism.tex','tab:mechanism',['Diagnostic','Comparison A','Comparison B'],rows,r'\textbf{Which interaction information is represented?} Layout targets. Rows 1--3 compare detached auxiliary supervision (A) with reciprocal coupling (B). Row 4 compares action conditioning (A) with action plus observed consequence conditioning (B). Row 5 compares observed (A) with predicted (B) consequences, retaining a possible degradation in the planned display. ADE denotes average displacement error. Probes fully corrupt generated inputs; interventions pair alternative commands with simulator rollouts from the same initial state.',True)
rows=[[k,target(v[1])] for k,v in pn['scale_controls']['rows'].items()]
table('scale_controls.tex','tab:scalecontrols',['Planned capacity or annotation setting','LIBERO-Plus success'],rows,r'\textbf{Which scale axis matters?} Layout targets in percent. Agent-width comparisons keep the video backbone, head geometry, depth, data, and update budget fixed and report the resulting compute separately. Annotation-density comparisons keep all video windows and robot exposure fixed while masking action labels at the episode level. The full-label setting is the shared reference for the density sweep. These settings require dedicated source configurations before execution.',True)
# Exact external values, reorganized by scientific question rather than source ordering.
rr=[]
for t,c,label in [('libero','Avg','Task control: LIBERO'),('robotwin','Avg','Bimanual control: RoboTwin Full'),('libero_plus','Avg','Perturbations: LIBERO-Plus'),('robotwin_c2r','Randomized','Clean-to-randomized: randomized only'),('robotwin_c2r','Avg','Clean-to-randomized: source mean'),('vlabench','Avg · SR','Language and task transfer: VLABench'),('robocasa_365','Avg','Household tasks: RoboCasa365'),('robodojo','Avg · SR','Manipulation coverage: RoboDojo'),('ebench','Overall · SR','Mobile manipulation: EBench'),('robocasa_gr1','SR (%)','Humanoid setup: RoboCasa-GR1')]:rr.append([label,external(t,c)])
table('reference.tex','tab:reference',['External evaluation','Reported success (percent)'],rr,r'\textbf{External reference anchors.} All cells are reproduced verbatim from \refsource{}, with the source\textquotesingle s own training and evaluation protocols. In particular, 69.0 is the clean-to-randomized average of clean and randomized performance; its randomized-only score is 48.7. The machine-readable source pointer for every value is retained in \texttt{artifacts/external\_reference.json}. These values describe the external system only.')
plt.rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
colors=['#698698','#B39471','#B5838A'];fig,axes=plt.subplots(1,3,figsize=(7.4,2.35),layout='constrained')
for ax,key,col in zip(axes,['world','action','consequence'],colors):
 d=logs['e0_libero_bi'];x=[r['step'] for r in d];y=[r['loss/'+key] for r in d];sm=[statistics.mean(y[max(0,i-10):i+1]) for i in range(len(y))]
 ax.plot(x,y,c=col,alpha=.25,lw=.5);ax.plot(x,sm,c=col,lw=1.5);ax.set_yscale('log');ax.set_title(key.capitalize(),fontsize=11);ax.set_xlabel('Optimizer updates');ax.set_xticks([0,10000,20000],['0','10k','20k']);ax.grid(alpha=.13);ax.set_ylabel('Training loss' if key=='world' else '')
fig.savefig(F/'training.pdf',bbox_inches='tight');plt.close(fig)
s=pn['scaling'];fig,axes=plt.subplots(1,2,figsize=(7.4,2.5),layout='constrained')
for ax,x,y,xlab in [(axes[0],s['fractions'],s['subset_success'],'Fraction of active corpus'),(axes[1],s['updates'],s['milestone_success'],'Pretraining updates')]:
 ax.plot(x,y,'o--',c='#995037',mfc='white',lw=1.2);ax.set_ylim(35,100);ax.set_ylabel('LIBERO-Plus success (%)');ax.set_xlabel(xlab);ax.grid(alpha=.15);ax.text(.04,.94,'LAYOUT TARGETS\nAwaiting measurements',transform=ax.transAxes,va='top',fontsize=9,color='#995037')
axes[0].set_xticks(s['fractions'],['1/8','1/4','1/2','Full']);axes[1].set_xticks([5000,30000,60000],['5k','30k','60k']);fig.savefig(F/'scaling_targets.pdf',bbox_inches='tight');plt.close(fig)
print('Regenerated evidence tables, layout targets, and vector plots.')
