from table_utils import *
# 3. Combine mechanism controls and readouts in one hierarchy.
short = ['World only', 'Action only', 'Independent', 'Auxiliary', 'One-way', r'\textbf{JAM joint}']
flags = [('Off', 'Off', 'Off'), ('Off', 'Off', 'Off'), ('Off', 'Off', 'Off'), ('Off', 'On', 'Off'), ('Off', 'On', 'On'), ('On', 'On', 'On')]
rows = []
for i, ((_, vals), name, fl) in enumerate(zip(pn['coupling']['rows'].items(), short, flags)):
    rows.append([(r'\jamshade{}' if i == 5 else '') + name] + list(fl) + [pending(x) for x in vals])
a = panel('A. Information exchange and gradient routing',
          ['Variant', r'W reads A', r'A reads W', 'Gradient', 'LIBERO', 'Plus', 'A probe', 'C error'], rows)
initrows=[]
for (_, scores), label in zip(pn['initialization']['rows'].items(), ['Without embodied pretraining',r'\jamshade\textbf{JAM pretraining}']):
    initrows.append([label] + [pending(x) for x in scores])
b=panel('A. Initialization at matched adaptation budget', ['Initialization','LIBERO','Plus'],initrows)
a=a.replace('A. Information exchange','B. Information exchange')
table('joint_analysis.tex','tab:joint',[b,a],
      r'\textbf{Which part of pretraining changes the representation?} Panel A isolates embodied pretraining from task adaptation. Panel B holds source exposure and clean conditions fixed. W and A denote world and action; Gradient denotes action-loss access to world parameters. A probe reports R-squared; C error is consequence average displacement error (ADE).')

# 4. Data ingredients, capacity and annotation density share one matched-budget study.
rows = []
for i, ((_, vals), human, consequence) in enumerate(zip(pn['composition']['rows'].items(), ['Off', 'On', 'On'], ['Off', 'Off', 'On'])):
    rows.append([(r'\jamshade\textbf{JAM mixture}' if i == 2 else ['Robot', '+ human video'][i]), 'Matched', human, consequence] + [pending(x) for x in vals])
a = panel('A. Which supervision source contributes?', ['Mixture', 'Robot budget', 'Human', 'Human C', 'LIBERO', 'Plus', 'C error'], rows)
rows = []
for i, (_, vals) in enumerate(pn['scale_controls']['rows'].items()):
    axis = 'Agent width' if i < 3 else 'Action labels'
    setting = str(vals[0]) + (r'\%' if i >= 3 else '')
    rows.append([(r'\jamshade{}' if i in [1, 5] else '') + axis, setting, 'Full', '60k', pending(vals[1])])
    if i == 2: rows.append(r'\midrule')
b = panel('B. Capacity and supervision density', ['Axis', 'Setting', 'Corpus', 'Updates', 'Plus'], rows)
table('data_scaling.tex', 'tab:data_scaling', [a, b],
      r'\textbf{Which data and scale choices support action grounding?} Panel A matches robot exposure; Panel B fixes the backbone, corpus, and update budget. Success is in percent and C error is image-normalized ADE. Blue rows identify reference settings.')


# Current mixture, generated directly from the audited runtime inventory.
inv=json.loads((P/'artifacts/data_inventory.json').read_text())
rows=[]
names={'droid':'DROID','bridge':'BridgeData V2','egodex':'EgoDex','ego4d':'Ego4D',
       'robomind_franka':'RoboMIND Franka','robomind_ur':'RoboMIND UR5e','robomind_agilex':'RoboMIND AgileX'}
for label,ids in [('Robot demonstrations',['droid','bridge','robomind_franka','robomind_ur','robomind_agilex']),
                  ('Human video',['egodex','ego4d'])]:
    rows.append(r'\panelrow{4}{'+label+'}')
    for key in ids:
        target_name='World + consequence' if key=='egodex' else ('World' if key=='ego4d' else 'World + action')
        rows.append(names[key]+' & '+target_name+' & '+f"{inv['source_counts'][key]:,}"+' & '+f"{inv['probabilities'][key]*100:.2f}"+r' \\')
body=[r'\begin{table}[H]',r'\centering\small',r'\begin{tabularx}{\linewidth}{@{}lYRR@{}}',r'\toprule',
      r'Source & Targets & Train windows & Sampling (\%) \\',r'\midrule']+rows+[r'\bottomrule',r'\end{tabularx}',
      r'\caption{\textbf{Current pretraining mixture.} Sampling probabilities follow cached training-window counts with temperature 0.7. Counts describe windows rather than unique episodes or duration.}',r'\label{tab:corpus}',r'\end{table}']
(T/'corpus.tex').write_text('\n'.join(body)+'\n')
