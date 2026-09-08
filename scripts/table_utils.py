from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]
T=P/"Tables"
plans=json.loads((P/"experiments/layout_targets.json").read_text())
pn,display=plans["tables"],plans["display"]
refs=json.loads((P/"artifacts/external_reference.json").read_text())
refs2=json.loads((P/"artifacts/external_baselines.json").read_text())
lookup={(r["table"],r["model"]):r for r in refs["rows"]+refs2["rows"]}
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
