# JAM: Action-Grounded World Pretraining

LaTeX sources for the report *JAM: Action-Grounded World Pretraining*, where
JAM stands for Joint Action-World Modeling.

## Build

The document is plain pdfLaTeX with BibTeX and needs no external image files:
every figure is drawn with TikZ inside the section sources.

```bash
pdflatex main && bibtex main && pdflatex main && pdflatex main
```

`00README.json` declares `main.tex` as the top-level source and `pdflatex` as
the compiler, so the Overleaf git bridge picks the right entry point without
further configuration.

## Layout

| Path | Contents |
|---|---|
| `main.tex` | preamble, macros, planning marker, section includes |
| `Sections/0_Abstract.tex` | abstract |
| `Sections/1_Introduction.tex` | Section 1, five paragraphs, no subsections |
| `Sections/2_RelatedWork.tex` | Section 2, three run-in paragraphs |
| `Sections/3_JointModeling.tex` | Section 3, formulation, noise plane, coupling axis, consequence |
| `Sections/4_Pretraining.tex` | Section 4, architecture, interfaces, corpus, procedure, measurement plan |
| `Sections/5_Experiments.tex` | Section 5, setup and four result blocks |
| `Sections/6_Conclusion.tex` | Section 6 |
| `Sections/A_Appendix.tex` | implementation status, reproduction interface |
| `Sections/_preamble.tex`, `Sections/_macros.tex` | inherited template packages and helpers |
| `jam.bib` | bibliography, every entry cited |
| `cambrian.cls` and the `.sty` files | inherited document class |

## Provenance of the numbers

Two kinds of number appear, and the document separates them everywhere.

**Published results.** Tables 4 to 6 carry the published results of OpenVLA,
Pi-0, and Pi-0.5 on the benchmark each table covers. Those rows print in black,
their captions say so, and the bibliography carries the source. Each of those
policies received large-scale pretraining of its own, which the table states in
its panel headers, so the pretrained rows of this work are the ones that compare
with them directly.

**Pre-registered targets.** Every other number in Section 5 is a target for a
run that the measurement programme still has to execute. Targets print in a
distinct colour through the `\pv{...}` macro, their captions say so, and the
source marks each such float with the token `PLANNED-VALUE`:

```bash
grep -n "PLANNED-VALUE" Sections/*.tex
```

Replacing a target with a measurement means deleting the `\pv{...}` wrapper
around that value and, once a float holds no target, removing its
`PLANNED-VALUE` comment and its `\plannednote{}` or `\plannedfig{}` call.

## Figures and tables

The report carries eight tables and four figures. Tables 1 and 2 are conceptual,
Table 3 is the corpus, Tables 4 to 7 are the four result tables, and Table 8
records implementation status. Figures 1 to 3 are method diagrams and Figure 4
collects the three result panels. Every figure is TikZ, uses one font size
through `\figfont`, and draws from a single low-saturation palette declared in
`main.tex`.

## Conventions

Section 3 carries the formulation and the only equations. Sections 1 and 5 carry
no formulas and no symbols. Every acronym is expanded at first use. Cross
references use `\sref`, `\tref`, and `\fref` for sections, tables, and figures.
