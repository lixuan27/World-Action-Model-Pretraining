from table_utils import *
# 3. Combine mechanism controls and readouts in one hierarchy.
short = ['World only', 'Action only', 'Independent', 'Auxiliary', 'One-way', r'\textbf{JAM joint}']
flags = [('Off', 'Off', 'Off'), ('Off', 'Off', 'Off'), ('Off', 'Off', 'Off'), ('Off', 'On', 'Off'), ('Off', 'On', 'On'), ('On', 'On', 'On')]
rows = []
for i, ((_, vals), name, fl) in enumerate(zip(pn['coupling']['rows'].items(), short, flags)):
    rows.append([(r'\jamshade{}' if i == 5 else '') + name] + list(fl) + [target(x) for x in vals] + [target(display['coupling_consequence_ade'][i])])
a = panel('A. Information exchange and gradient routing',
          ['Variant', r'W reads A', r'A reads W', 'Gradient', 'LIBERO', 'Plus', 'A probe', 'C error'], rows)
initrows=[]
for i, ((_, scores), label) in enumerate(zip(pn['main']['rows'].items(), ['Without embodied pretraining',r'\jamshade\textbf{JAM pretraining}'])):
    initrows.append([label, target(scores[0]), target(pn['ood']['rows']['Visual and layout shift: LIBERO-Plus'][i])])
b=panel('A. Initialization at matched adaptation budget', ['Initialization','LIBERO','Plus'],initrows)
a=a.replace('A. Information exchange','B. Information exchange')
table('joint_analysis.tex','tab:joint',[b,a],
      r'\textbf{Which part of pretraining changes the representation?} Panel A isolates embodied pretraining from task adaptation. Panel B holds source exposure and clean conditions fixed. W and A denote world and action; Gradient denotes action-loss access to world parameters. A probe reports R-squared; C error is consequence average displacement error (ADE). All entries in this controlled study await measurement.')

# 4. Data ingredients, capacity and annotation density share one matched-budget study.
rows = []
for i, ((_, vals), human, consequence) in enumerate(zip(pn['composition']['rows'].items(), ['Off', 'On', 'On'], ['Off', 'Off', 'On'])):
    rows.append([(r'\jamshade\textbf{JAM mixture}' if i == 2 else ['Robot', '+ human video'][i]), 'Matched', human, consequence] + [target(x) for x in vals])
a = panel('A. Which supervision source contributes?', ['Mixture', 'Robot budget', 'Human', 'Human C', 'LIBERO', 'Plus', 'C error'], rows)
rows = []
for i, (_, vals) in enumerate(pn['scale_controls']['rows'].items()):
    axis = 'Agent width' if i < 3 else 'Action labels'
    setting = str(vals[0]) + (r'\%' if i >= 3 else '')
    rows.append([(r'\jamshade{}' if i in [1, 5] else '') + axis, setting, 'Full', '60k', target(vals[1])])
    if i == 2: rows.append(r'\midrule')
b = panel('B. Capacity and supervision density', ['Axis', 'Setting', 'Corpus', 'Updates', 'Plus'], rows)
table('data_scaling.tex', 'tab:data_scaling', [a, b],
      r'\textbf{Which data and scale choices support action grounding?} Panel A matches robot exposure; Panel B fixes the backbone, corpus, and update budget. Success is in percent and C error is image-normalized ADE. Blue rows identify reference settings.')
