"""Serif, vector-first scientific figures with explicit evidence provenance."""
from pathlib import Path
import json
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

# 1. Admission and actual source sampling are different quantities.
inv=json.loads((P/'artifacts/data_inventory.json').read_text())
fig=plt.figure(figsize=(6.5,2.30));gs=fig.add_gridspec(1,2,width_ratios=[1.45,1],left=.18,right=.99,bottom=.18,top=.78,wspace=.40)
a=fig.add_subplot(gs[0]);b=fig.add_subplot(gs[1]);style(a)
ids=list(inv['source_counts']);names=['DROID','Bridge V2','EgoDex','RoboMIND Franka','RoboMIND UR5e']
old=inv['previous_stage']['probabilities']+[0,0];new=[inv['probabilities'][k] for k in ids];y=np.arange(5)
a.barh(y-.15,np.array(old)*100,height=.27,color='#D2DFE8',label='Initial mixture')
a.barh(y+.15,np.array(new)*100,height=.27,color=BLUE,label='After 8.4k updates')
for yy,v in zip(y,new):a.text(v*100+1,yy+.15,f'{v*100:.1f}%',va='center',fontsize=8.1)
a.set_yticks(y,names);a.invert_yaxis();a.set_xlim(0,62);a.set_xticks([0,20,40,60]);a.set_xlabel('Source sampling probability (%)')
a.set_title('A. Consumed by training',loc='left',pad=28)
a.legend(loc='lower left',bbox_to_anchor=(-.02,1.015),ncol=1,frameon=False,handlelength=1.2,borderaxespad=0,labelspacing=.25)
b.set_axis_off();b.set_title('B. Next admissions',loc='left',pad=28)
stages=[('Ego4D','Merged',BLUE),('RoboMIND AgileX','Encoding',SAND),('InternData-A1','Acquiring',GREY),('RoboCOIN','Encoding',SAND),('EPIC-KITCHENS','Acquiring',GREY)]
for yy,(nm,state,color) in zip(np.linspace(.88,.08,5),stages):
    b.text(0,yy,nm,va='center',fontsize=8.0,transform=b.transAxes)
    b.text(1.03,yy,state,va='center',ha='right',fontsize=8.0,color=color,transform=b.transAxes)
fig.text(.985,.032,'Snapshot: 8 September 2026',ha='right',fontsize=8,color='#6F7E87')
save(fig,'data_mixture')

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
            if run=='jam_base_v1' and x[i]>8400:start=max(start,int(np.searchsorted(x,8400,side='right')))
            z=y[start:i+1];smooth.append(np.nanmean(z) if np.isfinite(z).any() else np.nan)
        ax.plot(x,y,color=color,alpha=.30,lw=.6);ax.plot(x,smooth,color=color,lw=1.45)
        ax.set_yscale('log');ax.yaxis.set_minor_formatter(NullFormatter());
        if key=='world':
            ticks=[.15,.2,.3] if row==0 else [.05,.1,.2,.4];ax.set_yticks(ticks,[f'{t:g}' for t in ticks])
        ax.set_xlim(0,last if row==0 else 20000)
        if row==0:
            ax.set_title(key.capitalize(),color=color,pad=7)
            ax.axvline(8400,color=INK,lw=.7,ls=':')
            ax.set_xticks([0,4000,last],['0','4k',f'{last/1000:g}k'])
        else:ax.set_xticks([0,10000,20000],['0','10k','20k'])
        if col==0:ax.set_ylabel('Foundation loss' if row==0 else 'Adaptation loss',labelpad=3)
        if row==1:ax.set_xlabel('Optimizer updates',labelpad=2)
fig.text(.105,.972,'Raw batches and local averages',fontsize=9.2,weight='bold',va='top')
fig.text(.99,.972,'Measured training records',fontsize=8.1,color='#677B89',ha='right',va='top')
save(fig,'training')

# Compact foundation prefix for the main-text training panel.
fig,axes=plt.subplots(1,3,figsize=(6.5,1.88));fig.subplots_adjust(left=.105,right=.965,bottom=.29,top=.76,wspace=.38)
data=logs['jam_base_v1'];x=np.array([r['step'] for r in data])
for ax,key,color in zip(axes,['world','action','consequence'],[BLUE,SAND,ROSE]):
    style(ax); y=np.array([r['loss/'+key] if r.get('frac/'+key+'_supervised',1)>0 else np.nan for r in data]);smooth=[]
    for i in range(len(y)):
        start=max(0,i-10)
        if x[i]>8400:start=max(start,int(np.searchsorted(x,8400,side='right')))
        z=y[start:i+1];smooth.append(np.nanmean(z) if np.isfinite(z).any() else np.nan)
    ax.plot(x,y,color=color,lw=.55,alpha=.28);ax.plot(x,smooth,color=color,lw=1.25)
    ax.set_yscale('log');ax.yaxis.set_minor_formatter(NullFormatter());
    if key=='world':ax.set_yticks([.15,.2,.3],['0.15','0.20','0.30'])
    ax.axvline(8400,color=INK,lw=.7,ls=':')
    ax.set_xlim(0,last);ax.set_xticks([0,4000,last],['0','4k',f'{last/1000:g}k'])
    ax.set_title(key.capitalize(),loc='left',color=color,pad=7);ax.set_xlabel('Updates',labelpad=2)
axes[0].set_ylabel('Training loss',labelpad=3)
save(fig,'foundation')

# 3. Plot every sampled layer, rather than selecting the layer with best test R2.
root=P/'artifacts/measurements/analysis'
fig,axes=plt.subplots(1,3,figsize=(6.5,2.95));fig.subplots_adjust(left=.085,right=.985,bottom=.29,top=.73,wspace=.48)
series=[('JAM, update 5,100',BLUE,'base_v1_m5100',''),('Video prior',SAND,'floors','_bare_prior'),('Random world',GREY,'floors','_random_init')]
for label,color,folder,suffix in series:
    d=json.loads((root/folder/f'probes_droid{suffix}.json').read_text());xx=list(map(int,d['layers']));rr=[d['layers'][str(i)]['actions'] for i in xx]
    axes[0].plot(xx,[r['r2'] for r in rr],'-o',color=color,lw=1.4,ms=3)
    axes[0].fill_between(xx,[r['r2_ci'][0] for r in rr],[r['r2_ci'][1] for r in rr],color=color,alpha=.13,lw=0)
    d=json.loads((root/folder/f'probes_egodex{suffix}.json').read_text());rr=[d['layers'][str(i)]['consequence'] for i in xx]
    axes[1].plot(xx,[r['metrics']['ade'] for r in rr],'-o',color=color,lw=1.4,ms=3)
    if suffix=='':floor=d['targets']['consequence']['floors']['copy_first']['ade']
axes[1].axhline(floor,color=ROSE,ls=':',lw=1.2)
axes[0].set_title('A. Action readout\nDROID',loc='left');axes[0].set_ylabel('R-squared')
axes[1].set_title('B. Consequence readout\nEgoDex',loc='left');axes[1].set_ylabel('Displacement error')
for ax in axes[:2]:
    style(ax);ax.set_xticks([5,15,29]);ax.set_xlabel('World layer');ax.yaxis.set_major_locator(MaxNLocator(4))
axes[0].set_ylim(0,.85)
cf=json.loads((root/'base_v1_m5100/counterfactual_libero.json').read_text())
for i,(key,lab) in enumerate([('donor','Donor'),('hold','Hold'),('shuffled_time','Time shuffle')]):
    v=cf['conditions'][key]['sensitivity_vs_true'];val=v['delta']*1000;lo,hi=np.array(v['ci'])*1000
    axes[2].errorbar(i,val,yerr=[[val-lo],[hi-val]],fmt='o',color=BLUE,ms=4,capsize=3,lw=1.3)
style(axes[2]);axes[2].axhline(0,color=INK,lw=.9);axes[2].set_xticks([0,1,2],['Donor','Hold','Shuffle']);axes[2].set_xlim(-.5,2.5)
axes[2].set_title('C. Action sensitivity\nLIBERO',loc='left');axes[2].set_ylabel('Change in error (×0.001)');axes[2].set_xlabel('Action-input change');axes[2].set_ylim(-2.05,2.05)
handles=[Line2D([],[],color=c,marker='o',lw=1.4,ms=3,label=l) for l,c,_,_ in series]
handles.append(Line2D([],[],color=ROSE,ls=':',lw=1.2,label='Copy-first floor'))
fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.53,.035),ncol=2,frameon=False,columnspacing=1.8,handlelength=1.6)
fig.text(.085,.985,'World-feature diagnostics at a fixed milestone',va='top',fontsize=9.5,weight='bold')
fig.text(.085,.905,'Partially noised future observations; generated action and consequence inputs are noise.',va='top',fontsize=8)
save(fig,'representation')

# 4. Planned scaling displays remain visibly separate from all measurements.
plans=json.loads((P/'experiments/layout_targets.json').read_text())['tables'];s=plans['scaling'];scale=list(plans['scale_controls']['rows'].values())
fig,axes=plt.subplots(1,3,figsize=(6.5,2.45));fig.subplots_adjust(left=.08,right=.985,bottom=.22,top=.70,wspace=.34)
sets=[(s['fractions'],s['subset_success'],'A. Data diversity','Corpus fraction'),
      (s['updates'],s['milestone_success'],'B. Training duration','Optimizer updates'),
      ([x[0] for x in scale[:3]],[x[1] for x in scale[:3]],'C. Agent capacity','Agent width')]
for ax,(xx,yy,title,xlab),c in zip(axes,sets,[BLUE,SAND,ROSE]):
    style(ax);ax.plot(xx,yy,'o--',color=c,mfc='white',mew=1.2,lw=1.3,ms=4)
    ax.set_title(title,loc='left');ax.set_xlabel(xlab);ax.set_ylim(45,100);ax.set_yticks([50,70,90])
axes[0].set_ylabel('Target success (%)');axes[0].set_xticks(s['fractions'],['1/8','1/4','1/2','Full'])
axes[1].set_xticks([5000,30000,60000],['5k','30k','60k']);axes[2].set_xticks([768,1024,1280])
fig.text(.08,.975,'PLANNED DISPLAY  |  Values await measurement',fontsize=9.1,color='#995037',weight='bold',va='top')
fig.text(.08,.865,'LIBERO-Plus; one factor varies in each panel while the remaining budgets are fixed.',fontsize=8,va='top')
save(fig,'scaling_targets')
(P/'artifacts/figure_qa.json').write_text(json.dumps(qa,indent=2)+'\n')
print('Built five serif vector figures with measured / planned separation.')
