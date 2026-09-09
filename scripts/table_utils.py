from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]
T=P/"Tables"
studies=json.loads((P/"experiments/pending_studies.json").read_text())
pn=studies["tables"]
refs=json.loads((P/"artifacts/external_reference.json").read_text())
refs2=json.loads((P/"artifacts/external_baselines.json").read_text())
lookup={(r["table"],r["model"]):r for r in refs["rows"]+refs2["rows"]}
def ext(table, model, columns):
    row = lookup[(table, model)]
    return [row['cells'][row['columns'].index(c)]['text'] for c in columns]


def model(name):
    return {'π₀': r'$\pi_0$', 'π₀.₅': r'$\pi_{0.5}$', 'Cosmos-Policy': 'Cosmos Policy'}.get(name, name)


def pending(x):
    if x is not None:
        raise ValueError('Pending outcomes must be null; archive measurement provenance before adding results.')
    return ''


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
    out = ['% PENDING-MEASUREMENT: empty result cells await archived experimental evidence.' if planned else '% EXTERNAL-REFERENCE: verbatim source values.',
           r'\begin{table}[H]', r'\centering',
           r'\begingroup\fontsize{' + str(size) + '}{' + str(size + 1.5) + r'}\selectfont',
           r'\setlength{\tabcolsep}{3.5pt}\renewcommand{\arraystretch}{1.12}',
           '\n\\vspace{2pt}\n'.join(panels), r'\endgroup',
           r'\caption{' + caption + (' ' + r'\pendingstudynote' if planned else '') + '}',
           r'\label{' + label + '}', r'\end{table}']
    (T / filename).write_text('\n'.join(out) + '\n')
