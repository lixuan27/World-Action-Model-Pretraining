"""Serif, vector-first scientific figures with explicit evidence provenance."""
from pathlib import Path
import json
import hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator, FuncFormatter, NullFormatter
from matplotlib.lines import Line2D

P=Path(__file__).resolve().parents[1]; F=P/'Figures'
plt.rcParams.update({'font.family':'serif','font.serif':['DejaVu Serif'],
    'mathtext.fontset':'dejavuserif','font.size':8.8,'axes.titlesize':9.2,
    'axes.labelsize':8.4,'xtick.labelsize':8,'ytick.labelsize':8,
    'legend.fontsize':8,'pdf.fonttype':42,'ps.fonttype':42,
    'axes.spines.top':False,'axes.spines.right':False,
    'axes.edgecolor':'#9BA9B1','axes.labelcolor':'#243A49',
    'text.color':'#243A49','axes.titleweight':'bold','savefig.facecolor':'white'})
BLUE='#527B96'; SAND='#AA885F'; ROSE='#AA737F'; INK='#243A49'; GREY='#9AA4AD'
qa=[]

def style(ax):
    ax.set_facecolor('#F8FAFB'); ax.grid(axis='y',color='#DDE5EA',lw=.55)
    ax.set_axisbelow(True);ax.tick_params(length=2.5,width=.6,pad=3)

def save(fig,key):
    fig.canvas.draw()
    # Fail if any visible text extends beyond the actual exported canvas.
    renderer=fig.canvas.get_renderer(); outside=[]
    for text in fig.findobj(matplotlib.text.Text):
        if not text.get_visible() or not text.get_text():continue
        b=text.get_window_extent(renderer)
        if b.x0 < -2 or b.y0 < -2 or b.x1 > fig.bbox.width+2 or b.y1 > fig.bbox.height+2:
            off_axis=False
            for ax in fig.axes:
                for axis,lims in [(ax.xaxis,ax.get_xlim()),(ax.yaxis,ax.get_ylim())]:
                    for tick in axis.get_major_ticks()+axis.get_minor_ticks():
                        if text in [tick.label1,tick.label2] and not min(lims)<=tick.get_loc()<=max(lims):off_axis=True
            if off_axis:continue
            outside.append(text.get_text())
    if outside:raise RuntimeError(f'{key}: out-of-canvas text {outside}')
    fig.savefig(F/f'{key}.pdf',metadata={'CreationDate':None})
    fig.savefig(F/f'{key}.png',dpi=200)
    qa.append({'figure':key,'font':'DejaVu Serif','format':'vector PDF','text_bounds':'PASS'})
    plt.close(fig)

inv=json.loads((P/'artifacts/data_inventory.json').read_text())
boundaries=inv['recipe_boundaries']

# 2. Preserve raw outliers; do not smooth across the recipe / masking boundary.
logs={r:[json.loads(x) for x in (P/f'artifacts/measurements/{r}.jsonl').read_text().splitlines()]
      for r in ['jam_base_v1','e0_libero_bi']}
last=logs['jam_base_v1'][-1]['step']
(P/'Tables/evidence_macros.tex').write_text(r'\newcommand{\FoundationSteps}{'+f'{last:,}'+'}\n')
fig,axes=plt.subplots(2,3,figsize=(6.5,3.4));fig.subplots_adjust(left=.12,right=.965,bottom=.13,top=.84,hspace=.53,wspace=.36)
for row,run in enumerate(logs):
    data=logs[run];x=np.array([r['step'] for r in data])
    for col,(key,color) in enumerate(zip(['world','action','consequence'],[BLUE,SAND,ROSE])):
        ax=axes[row,col];style(ax)
        y=np.array([r['loss/'+key] if r.get('frac/'+key+'_supervised',1)>0 else np.nan for r in data])
        smooth=[]
        for i in range(len(y)):
            start=max(0,i-10)
            if run=='jam_base_v1':
                prior=[q for q in boundaries if x[i]>q]
                if prior:start=max(start,int(np.searchsorted(x,max(prior),side='right')))
            z=y[start:i+1];smooth.append(np.nanmean(z) if np.isfinite(z).any() else np.nan)
        ax.plot(x,y,color=color,alpha=.30,lw=.6);ax.plot(x,smooth,color=color,lw=1.45)
        ax.set_yscale('log');ax.yaxis.set_minor_formatter(NullFormatter());
        if key=='world':
            ticks=[.1,.2,.3] if row==0 else [.05,.1,.2,.4];ax.set_yticks(ticks,[f'{t:g}' for t in ticks])
        ax.set_xlim(0,last if row==0 else 20000)
        if row==0:
            ax.set_title(key.capitalize(),color=color,pad=7)
            for q in boundaries:ax.axvline(q,color=INK,lw=.7,ls=':')
            ax.set_xticks([0,4000,last],['0','4k',f'{last/1000:.1f}k'])
        else:ax.set_xticks([0,10000,20000],['0','10k','20k'])
        if col==0:ax.set_ylabel('Foundation loss' if row==0 else 'Adaptation loss',labelpad=3)
        if row==1:ax.set_xlabel('Optimizer updates',labelpad=2)
fig.text(.105,.972,'Raw batches and local averages',fontsize=9.2,weight='bold',va='top')
fig.text(.99,.972,'Measured training records',fontsize=8.1,color='#677B89',ha='right',va='top')
save(fig,'training')

# 3. Compare representation readout and its gain over the video initialization.
# Keep all sampled depths and the simple consequence floor. Input sensitivity
# answers a separate question and is preserved in the appendix figure below.
root=P/'artifacts/measurements/analysis'
fig=plt.figure(figsize=(6.5,3.05))
axes=[fig.add_axes([.095,.405,.365,.405]),fig.add_axes([.605,.405,.365,.405])]
gains=[fig.add_axes([.095,.135,.365,.16]),fig.add_axes([.605,.135,.365,.16])]
series=[('JAM',BLUE,'base_v1_m5100',''),('Video prior',SAND,'floors','_bare_prior'),('Random init.',GREY,'floors','_random_init')]
records={};source_hashes={}
for label,color,folder,suffix in series:
    reports={}
    for dataset in ['droid','egodex']:
        path=root/folder/f'probes_{dataset}{suffix}.json'
        reports[dataset]=json.loads(path.read_text())
        source_hashes[str(path.relative_to(P))]=hashlib.sha256(path.read_bytes()).hexdigest()
    xx=sorted(map(int,reports['droid']['layers']))
    assert xx==sorted(map(int,reports['egodex']['layers']))
    action=[reports['droid']['layers'][str(i)]['actions'] for i in xx]
    ade=np.array([reports['egodex']['layers'][str(i)]['consequence']['metrics']['ade'] for i in xx])
    r2=np.array([r['r2'] for r in action])
    records[label]={'action_r2':r2.tolist(),'consequence_ade':ade.tolist()}
    zorder=4 if label=='JAM' else 2
    for ax,values in zip(axes,[r2,ade]):
        ax.plot(xx,values,color=color,marker='o' if label=='JAM' else 's',
                lw=1.8 if label=='JAM' else 1.1,ms=3.6 if label=='JAM' else 2.7,
                markeredgewidth=.65,mfc=color if label=='JAM' else 'white',zorder=zorder)
    axes[0].fill_between(xx,[r['r2_ci'][0] for r in action],[r['r2_ci'][1] for r in action],color=color,alpha=.15,lw=0)
    if label=='JAM':floor=reports['egodex']['targets']['consequence']['floors']['copy_first']['ade']
axes[1].axhline(floor,color=ROSE,ls=(0,(2,2)),lw=1.2,zorder=1)
axes[0].set_ylabel('Action $R^2$ ↑',labelpad=4)
axes[1].set_ylabel('Consequence ADE ↓',labelpad=5)
axes[0].set_ylim(0,.85);axes[0].set_yticks([0,.2,.4,.6,.8])
axes[1].set_ylim(.098,.162);axes[1].set_yticks([.10,.12,.14,.16])
axes[1].yaxis.set_major_formatter(FuncFormatter(lambda v,pos:f'{v:.2f}'))
for ax in axes:
    style(ax);ax.set_xticks(xx);ax.tick_params(labelbottom=False)
    ax.set_xlim(3,31)
action_gain=np.array(records['JAM']['action_r2'])-np.array(records['Video prior']['action_r2'])
prior_ade=np.array(records['Video prior']['consequence_ade'])
ade_reduction=100*(prior_ade-np.array(records['JAM']['consequence_ade']))/prior_ade
for ax,values,title in zip(gains,[action_gain,ade_reduction],['$R^2$ gain over video prior ↑','ADE reduction vs video prior (%) ↑']):
    style(ax);ax.set_facecolor('#F0F5F8')
    ax.bar(xx,values,width=2.5,color=BLUE,alpha=.85,zorder=3)
    ax.axhline(0,color=INK,lw=.7)
    ax.set_title(title,loc='left',fontsize=8.2,weight='normal',pad=5)
    ax.set_xticks(xx);ax.set_xlim(3,31);ax.set_xlabel('World layer',labelpad=3)
gains[0].set_ylim(0,.66);gains[0].set_yticks([0,.3,.6])
gains[1].set_ylim(0,22);gains[1].set_yticks([0,10,20])
fig.text(.095,.98,'A  Motor-action readout · DROID',va='top',fontsize=9.2,weight='bold')
fig.text(.605,.98,'B  Visual consequence · EgoDex',va='top',fontsize=9.2,weight='bold')
handles=[Line2D([],[],color=c,marker='o' if l=='JAM' else 's',lw=1.5,
                mfc=c if l=='JAM' else 'white',ms=3.2,label=l) for l,c,_,_ in series]
handles.append(Line2D([],[],color=ROSE,ls=(0,(2,2)),lw=1.2,label='Copy-first (B)'))
fig.legend(handles=handles,loc='upper center',bbox_to_anchor=(.53,.921),ncol=4,
           frameon=False,columnspacing=1.3,handlelength=1.8,fontsize=8)
save(fig,'representation')
comparison={'checkpoint_update':5100,'layers':xx,'source_sha256':source_hashes,
            'readouts':records,'copy_first_consequence_ade':floor,
            'jam_action_r2_gain_vs_video_prior':action_gain.tolist(),
            'jam_consequence_ade_reduction_percent_vs_video_prior':ade_reduction.tolist(),
            'jam_beats_copy_first_layers':[layer for layer,ade in zip(xx,records['JAM']['consequence_ade']) if ade<floor],
            'gain_uncertainty':'Point estimates; joint bootstrap samples are unavailable.',
            'scope':'Frozen-world ridge readout; partially visible future; window splits may share episodes.'}
(P/'artifacts/representation_comparison.json').write_text(json.dumps(comparison,indent=2)+'\n')

# Preserve the inconclusive action-input intervention in a separate display.
cf=json.loads((root/'base_v1_m5100/counterfactual_libero.json').read_text())
fig,ax=plt.subplots(figsize=(6.5,1.85));fig.subplots_adjust(left=.225,right=.94,bottom=.30,top=.84)
for i,(key,lab) in enumerate([('donor','Donor action'),('hold','Hold action'),('shuffled_time','Time shuffle')]):
    v=cf['conditions'][key]['sensitivity_vs_true'];val=v['delta']*1000;lo,hi=np.array(v['ci'])*1000
    ax.errorbar(val,i,xerr=[[val-lo],[hi-val]],fmt='o',color=BLUE,ms=4.2,capsize=3,lw=1.5)
style(ax);ax.grid(False);ax.grid(axis='x',color='#DDE5EA',lw=.55)
ax.axvline(0,color=INK,lw=.9);ax.set_xlim(-2.1,2.1);ax.set_xticks([-2,-1,0,1,2])
ax.set_yticks([0,1,2],['Donor action','Hold action','Time shuffle']);ax.set_ylim(2.45,-.45)
ax.set_xlabel('Consequence error change from the recorded action (×10⁻³)',labelpad=5)
fig.text(.225,.98,'LIBERO · 300 windows',va='top',fontsize=9.2,weight='bold')
fig.text(.94,.98,'Paired 95% intervals include zero',va='top',ha='right',fontsize=8.2,color='#677B89')
save(fig,'action_sensitivity')

# 4. Retain the scaling protocol, with no unmeasured outcomes on the axes.
plans=json.loads((P/'experiments/pending_studies.json').read_text())['tables'];s=plans['scaling'];scale=list(plans['scale_controls']['rows'].values())
fig,axes=plt.subplots(1,3,figsize=(6.5,2.45));fig.subplots_adjust(left=.08,right=.985,bottom=.22,top=.70,wspace=.34)
sets=[(s['fractions'],s['subset_success'],'A. Data diversity','Corpus fraction'),
      (s['updates'],s['milestone_success'],'B. Training duration','Optimizer updates'),
      ([x[0] for x in scale[:3]],[x[1] for x in scale[:3]],'C. Agent capacity','Agent width')]
for ax,(xx,yy,title,xlab) in zip(axes,sets):
    assert len(xx)==len(yy) and all(y is None for y in yy), 'Pending scaling outcomes require measurement provenance.'
    style(ax)
    pad=(max(xx)-min(xx))*.06
    ax.set_xlim(min(xx)-pad,max(xx)+pad)
    ax.set_title(title,loc='left');ax.set_xlabel(xlab);ax.set_ylim(0,100);ax.set_yticks([0,50,100])
axes[0].set_ylabel('Success (%)');axes[0].set_xticks(s['fractions'],['1/8','1/4','1/2','Full'])
axes[1].set_xticks([5000,30000,60000],['5k','30k','60k']);axes[2].set_xticks([768,1024,1280])
fig.text(.08,.975,'LIBERO-Plus scaling protocol',fontsize=9.1,color=INK,weight='bold',va='top')
fig.text(.08,.865,'LIBERO-Plus; one factor varies in each panel while the remaining budgets are fixed.',fontsize=8,va='top')
assert all(len(ax.lines)==0 and len(ax.collections)==0 for ax in axes)
save(fig,'scaling_pending')
qa[-1].update({'status':'awaiting_measurement','plotted_result_points':0,'plotted_result_curves':0})
(P/'artifacts/figure_qa.json').write_text(json.dumps(qa,indent=2)+'\n')
print('Built three measured serif figures and one empty scaling protocol display.')
