#!/usr/bin/env python3
"""Build full-width, panelled displays from measured, external, and planned data."""
from pathlib import Path
import json
import statistics
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

P = Path(__file__).resolve().parents[1]
T, F = P / 'Tables', P / 'Figures'
plans = json.loads((P / 'experiments/layout_targets.json').read_text())
assert plans['status'] == 'planned'
pn, display = plans['tables'], plans['display']
refs = json.loads((P / 'artifacts/external_reference.json').read_text())
refs2 = json.loads((P / 'artifacts/external_baselines.json').read_text())
lookup = {(r['table'], r['model']): r for r in refs['rows'] + refs2['rows']}


def ext(table, model, columns):
    row = lookup[(table, model)]
    return [row['cells'][row['columns'].index(c)]['text'] for c in columns]


def model(name):
    return {'π₀': r'$\pi_0$', 'π₀.₅': r'$\pi_{0.5}$', 'Cosmos-Policy': 'Cosmos Policy'}.get(name, name)


def target(x):
    return r'\target{' + (f'{x:.2f}' if abs(x) < 1 else f'{x:.1f}') + '}'


def jam(name, scores):
    return [r'\jamshade\textbf{JAM ' + name + '}'] + [target(x) for x in scores]


def panel(title, headers, rows, fmt=None):
    n = len(headers)
    spec = fmt or ('l' + 'R' * (n - 1))
    out = [r'\begin{tabularx}{\linewidth}{' + spec + '}',
           r'\toprule', r'\panelrow{' + str(n) + '}{' + title + '}',
           ' & '.join(headers) + r' \\', r'\midrule']
    for row in rows:
        out.append(row if isinstance(row, str) else ' & '.join(row) + r' \\')
    out += [r'\bottomrule', r'\end{tabularx}']
    return '\n'.join(out)


def table(filename, label, panels, caption, planned=True, size=9):
    out = ['% PLANNED-VALUE: superscript T identifies design values awaiting measurement.' if planned else '% EXTERNAL-REFERENCE: verbatim source values.',
           r'\begin{table}[H]', r'\centering',
           r'\begingroup\fontsize{' + str(size) + '}{' + str(size + 1.5) + r'}\selectfont',
           r'\setlength{\tabcolsep}{3.5pt}\renewcommand{\arraystretch}{1.12}',
           '\n\\vspace{2pt}\n'.join(panels), r'\endgroup',
           r'\caption{' + caption + (' ' + r'\targetnote' if planned else '') + '}',
           r'\label{' + label + '}', r'\end{table}']
    (T / filename).write_text('\n'.join(out) + '\n')


# 1. Overall control: suite-level and embodiment-level views of one question.
rows = [[model(m)] + ext('libero', m, ['Spatial', 'Object', 'Goal', 'Long', 'Avg'])
        for m in ['OpenVLA', 'π₀', 'π₀.₅', 'OpenVLA-OFT', 'X-VLA', 'R1']]
rows += [r'\midrule', jam('direct', display['libero']['Direct']), jam('pretrained', display['libero']['Pretrained'])]
a = panel('A. LIBERO: task control', ['Model', 'Spatial', 'Object', 'Goal', 'Long', 'Mean'], rows)
rows = []
for m in ['π₀.₅', 'R1']:
    rows.append([model(m)] + ext('robotwin', m, ['Clean', 'Randomized', 'Avg'])
                + ext('vlabench', m, ['Avg · SR']) + ext('robocasa_365', m, ['Avg']))
rows += [r'\midrule']
for key, name, oldkey in [('Direct', 'direct', 'Direct adaptation'), ('Pretrained', 'pretrained', 'JAM pretraining + adaptation')]:
    vals = display['robotwin_full'][key] + pn['main']['rows'][oldkey][2:]
    rows.append(jam(name, vals))
b = panel('B. Transfer across task families', ['Model', 'Twin: clean', 'Twin: random', 'Twin: mean', 'VLABench', 'Casa365'], rows)
table('main_results.tex', 'tab:main', [a, b],
      r'\textbf{Does joint pretraining improve downstream control?} Success percentages; Twin denotes RoboTwin 2.0 Full. External scores reproduce the \refsource{} export. JAM pairs match adaptation settings. Casa365 compares external full-suite scores with JAM target-task scores, preserving their distinct scopes.')

# 2. Shift axes as columns, with short model names as rows.
plus_cols = ['Camera', 'Robot', 'Language', 'Light', 'Background', 'Noise', 'Layout', 'Avg']
rows = [[model(m)] + ext('libero_plus', m, plus_cols)
        for m in ['π₀', 'π₀.₅', 'OpenVLA-OFT', 'Cosmos-Policy', 'R1']]
rows += [r'\midrule', jam('direct', display['libero_plus']['Direct']), jam('pretrained', display['libero_plus']['Pretrained'])]
a = panel('A. LIBERO-Plus: visual and interaction shifts',
          ['Model', 'Camera', 'Robot', 'Language', 'Light', 'Backgr.', 'Noise', 'Layout', 'Mean'], rows)
vla_cols = ['In-dist. · SR', 'Category · SR', 'Commonsense · SR', 'Instruction · SR', 'Texture · SR', 'Avg · SR']
rows = [[model(m)] + ext('vlabench', m, vla_cols) for m in ['π₀', 'π₀.₅', 'R1']]
rows += [r'\midrule', jam('direct', display['vlabench']['Direct']), jam('pretrained', display['vlabench']['Pretrained'])]
b = panel('B. VLABench: semantic and visual transfer', ['Model', 'In-dist.', 'Category', 'Reasoning', 'Instruction', 'Texture', 'Mean'], rows)
rows = []
for i, name in enumerate(['direct', 'pretrained']):
    vals = [pn['ood']['rows'][key][i] for key in ['Initial-state shift: LIBERO-PRO', 'Task-instruction shift: LIBERO-PRO', 'Environment shift: RoboTwin randomized', 'Embodiment transfer: held-out platform']]
    rows.append(jam(name, vals))
c = panel('C. Held-out conditions and embodiments', ['Model', 'PRO: state', 'PRO: task', 'Twin: random', 'Embodiment'], rows)
table('robustness.tex', 'tab:robustness', [a, b, c],
      r'\textbf{Which shifts preserve a pretraining gain?} Success percentages. External values retain source aggregation. Panel C pairs resets; Twin evaluates randomized conditions after clean-only adaptation. Embodiment transfer holds out the target platform from pretraining. Appendix~\ref{app:setup} specifies evaluation and statistics.', size=8.5)

# 3. Combine mechanism controls and readouts in one hierarchy.
short = ['World only', 'Action only', 'Independent', 'Auxiliary', 'One-way', r'\textbf{JAM joint}']
flags = [('Off', 'Off', 'Off'), ('Off', 'Off', 'Off'), ('Off', 'Off', 'Off'), ('Off', 'On', 'Off'), ('Off', 'On', 'On'), ('On', 'On', 'On')]
rows = []
for i, ((_, vals), name, fl) in enumerate(zip(pn['coupling']['rows'].items(), short, flags)):
    rows.append([(r'\jamshade{}' if i == 5 else '') + name] + list(fl) + [target(x) for x in vals] + [target(display['coupling_consequence_ade'][i])])
a = panel('A. Information exchange and gradient routing',
          ['Variant', r'W reads A', r'A reads W', 'Gradient', 'LIBERO', 'Plus', 'A probe', 'C error'], rows)
mech = list(pn['mechanism']['rows'].values())
labels = [('Action probe', 'R-squared', 'Auxiliary', 'JAM'), ('Consequence', 'ADE', 'Auxiliary', 'JAM'),
          ('Intervention', 'ADE', 'Auxiliary', 'JAM'), ('World forecast', 'Image dist.', 'Action', 'Action + C'),
          ('C conditioning', 'ADE', 'Observed C', 'Predicted C')]
rows = [[r'\jamshade{}' + lab, metric, ref, test, target(vals[0]), target(vals[1])]
        for (lab, metric, ref, test), vals in zip(labels, mech)]
b = panel('B. Representation and consequence diagnostics', ['Diagnostic', 'Metric', 'Reference', 'Test', 'Ref. score', 'Test score'], rows)
table('joint_analysis.tex', 'tab:joint', [a, b],
      r'\textbf{What does reciprocal action--world learning change?} W, A, and C denote world, action, and consequence. Panel A fixes clean conditions; Gradient denotes action-loss access to world parameters; the probe reports R-squared and C error is average displacement error (ADE). Panel B pairs each diagnostic with its reference and test condition. Image distance measures perceptual prediction error. Observed and predicted consequences remain separate conditions, including a possible prediction gap.')

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
      r'\textbf{Which data and scale choices support action grounding?} Panel A matches robot exposure and varies human video and consequence supervision. Panel B fixes the video backbone, corpus, and update budget; blue rows identify the reference settings. Success is in percent and C error uses image-normalized ADE. Figure~\ref{fig:scaling} separately varies unique data and update count.')

# Compact external-only appendix, preserving the additional source anchors.
triples = [('LIBERO','libero','Avg'), ('Twin Full','robotwin','Avg'), ('VLABench','vlabench','Avg · SR'),
           ('Casa365','robocasa_365','Avg'), ('Dojo','robodojo','Avg · SR'), ('EBench','ebench','Overall · SR'),
           ('Plus','libero_plus','Avg'), ('Twin clean','robotwin_c2r','Clean'), ('Twin random','robotwin_c2r','Randomized'),
           ('Twin mean','robotwin_c2r','Avg'), ('Casa-GR1','robocasa_gr1','SR (%)'), ('LIBERO Long','libero','Long')]
rows = []
for i in range(0, len(triples), 3):
    row = []
    for label, t, col in triples[i:i+3]: row += [label] + ext(t, 'R1', [col])
    rows.append(row)
a = panel('R1: source protocol anchors', ['Benchmark', 'Success', 'Benchmark', 'Success', 'Benchmark', 'Success'], rows)
table('reference.tex', 'tab:reference', [a],
      r'\textbf{External reference coverage.} Source-reported success percentages from \refsource{}. Dojo denotes RoboDojo and Casa-GR1 denotes RoboCasa-GR1. Twin clean, random, and mean refer to the clean-to-randomized protocol. Exact source strings and row pointers accompany every value.', planned=False)

# Measured curves, including the active foundation prefix with missing supervision masked.
logs = {r: [json.loads(l) for l in (P / f'artifacts/measurements/{r}.jsonl').read_text().splitlines()]
        for r in ['e0_libero_bi', 'jam_base_v1']}
(T / 'evidence_macros.tex').write_text(r'\newcommand{\FoundationSteps}{' + f'{logs["jam_base_v1"][-1]["step"]:,}' + '}\n')
plt.rcParams.update({'font.family': 'serif', 'font.serif': ['DejaVu Serif'], 'font.size': 9,
                     'axes.spines.top': False, 'axes.spines.right': False, 'pdf.fonttype': 42,
                     'axes.labelcolor': '#314B60', 'axes.edgecolor': '#8796A1'})
colors = ['#557F9B', '#B39471', '#AE7A83']
fig, axes = plt.subplots(2, 3, figsize=(7.4, 3.25), layout='constrained')
for rindex, (run, title) in enumerate([('e0_libero_bi', 'Adaptation'), ('jam_base_v1', 'Foundation')]):
    data = logs[run]
    for ax, key, color in zip(axes[rindex], ['world', 'action', 'consequence'], colors):
        x = [r['step'] for r in data]
        y = np.array([r['loss/' + key] if r.get('frac/' + key + '_supervised', 1) > 0 else np.nan for r in data])
        smooth = [np.nanmean(y[max(0, i-10):i+1]) if np.isfinite(y[max(0, i-10):i+1]).any() else np.nan for i in range(len(y))]
        ax.set_facecolor('#F7FAFC'); ax.plot(x, y, color=color, alpha=.25, lw=.6)
        ax.plot(x, smooth, color=color, lw=1.5); ax.set_yscale('log'); ax.grid(alpha=.14)
        ax.set_title(f'{title} / {key}', fontsize=9)
        ax.set_ylabel('Training loss' if key == 'world' else '')
        ax.set_xticks([0, 10000, 20000] if rindex == 0 else [0, 2500, 5200],
                      ['0', '10k', '20k'] if rindex == 0 else ['0', '2.5k', '5.2k'])
        if rindex == 1: ax.set_xlabel('Optimizer updates')
        if rindex == 0:
            summary = json.loads((P / 'artifacts/measurements/e0_libero_bi_summary.json').read_text())
            val = summary['loss/' + key]['final_mean_last10pct']
            ax.text(.97, .93, f'Final mean {val:.4f}', ha='right', va='top', transform=ax.transAxes,
                    fontsize=8, bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': .8, 'pad': 2})
fig.savefig(F / 'training.pdf', bbox_inches='tight', metadata={'CreationDate': None}); plt.close(fig)

s = pn['scaling']; scale = list(pn['scale_controls']['rows'].values())
fig, axes = plt.subplots(1, 3, figsize=(7.4, 2.45), layout='constrained')
sets = [(s['fractions'], s['subset_success'], 'Unique data', 'Corpus fraction'),
        (s['updates'], s['milestone_success'], 'Training duration', 'Updates'),
        ([x[0] for x in scale[:3]], [x[1] for x in scale[:3]], 'Agent capacity', 'Agent width')]
for ax, (x, y, title, xlabel) in zip(axes, sets):
    ax.set_facecolor('#F5F9FC'); ax.plot(x, y, 'o--', color='#557F9B', mfc='white', lw=1.3, ms=4)
    ax.set_ylim(40, 100); ax.set_title(title, fontsize=10); ax.set_xlabel(xlabel); ax.grid(alpha=.15)
    ax.text(.04, .96, 'LAYOUT TARGETS', transform=ax.transAxes, va='top', fontsize=7, color='#995037')
axes[0].set_ylabel('LIBERO-Plus success (%)'); axes[0].set_xticks(s['fractions'], ['1/8', '1/4', '1/2', 'Full'])
axes[1].set_xticks([5000, 30000, 60000], ['5k', '30k', '60k']); axes[2].set_xticks([768,1024,1280])
fig.savefig(F / 'scaling_targets.pdf', bbox_inches='tight', metadata={'CreationDate': None}); plt.close(fig)
print('Built four main panelled tables, one appendix table, and evidence-typed plots.')
