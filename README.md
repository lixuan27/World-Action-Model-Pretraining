# JAM: Action-Grounded World Pretraining

LaTeX manuscript for JAM, Joint Action–World Modeling. The paper studies how action supervision can shape a world representation through reciprocal generative computation.

## Build

The generated tables and vector figures are committed. Compile with:

```sh
tectonic -X compile main.tex --keep-logs --keep-intermediates
```

A standard TeX Live installation can instead run `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`. The output is `main.pdf`; `paper/JAM.pdf` is the compiled reading copy.

To regenerate and verify all numerical displays:

```sh
python3 -m pip install -r requirements-paper.txt
python3 scripts/build_artifacts.py
tectonic -X compile main.tex --keep-logs --keep-intermediates
python3 scripts/validate.py --verify-external
```

The first Tectonic build downloads standard TeX packages. Figures 1 and 2 use the latest supplied version-11 PowerPoint deck, exported as vector PDFs with the supplied Toppan fonts. Four numerical figures, including the appendix sensitivity check, are generated with Matplotlib in DejaVu Serif. Figure 3 uses Toppan Bunkyu Mincho, with STIX serif mathematical glyphs, and provides a PDF, PNG, editable SVG, and portable outlined SVG. Paper builds launch no training.

The editable source for both figures is `Figures/source/JAM-framework-v11.pptx`, copied byte-for-byte from the updated file under `Desktop/JAM-Figures/Framework/`. The deck has two slides: slide 1 is the framework, and slide 2 is the teaser. Export a working copy of the complete deck from PowerPoint as PDF. Normalize and select its pages with:

```sh
python3 scripts/normalize_framework_pdf.py native-export.pdf Figures/framework_v11.pdf --font /path/to/ToppanBunkyuMinchoPr6N-Regular.otf --pptx Figures/source/JAM-framework-v11.pptx --slide 1 --crop 8 9 1242 440
python3 scripts/normalize_framework_pdf.py native-export.pdf Figures/teaser_v11.pdf --font /path/to/ToppanBunkyuMinchoPr6N-Regular.otf --pptx Figures/source/JAM-framework-v11.pptx --slide 2 --crop 280 5 957 485 --teaser-spacing-fix
```

Use the complete Toppan font from the macOS font assets, rather than its small system subset. Unicode mappings make the embedded fonts portable to readers without external Japanese font maps. Crops remove only outer blank margins. The teaser's Independent label moves left by 8 points to separate it from One-way; every other drawing byte is preserved. The original PPT remains unchanged. `artifacts/teaser_v11_qa.json` and `artifacts/framework_v11_qa.json` record slide mapping, source hashes, crop bounds, verified labels, and the spacing correction. Figure 1 fills the homepage below the abstract; Figure 2 appears on page 4.

To regenerate Figure 3, run `python3 scripts/build_consequence_figure.py` on a Mac with Toppan Bunkyu Mincho installed. Elsewhere, set `JAM_FIGURE_FONT` to the font's `ToppanBunkyuMinchoPr6N-Regular.otf` file. The committed PDF compiles on any supported LaTeX installation without the local font. The SVG with live text preserves editability; the outlined SVG preserves appearance without requiring font installation.

Figure 3 distinguishes current anchors, future image positions, gain-scaled displacement, observability, and coordinate validity. Its examples explicitly separate visible points, occluded points, and missing slots. The mask has its own path into the joint loss. The interaction illustration is reused unchanged from the user-supplied reference drawing and represents a schematic, rather than a measured rollout. Source and drawing provenance are recorded in `artifacts/consequence_figure_qa.json`.

Figure 5 compares frozen-world motor-action and visual-consequence readout across all six sampled layers. The upper panels show JAM, video initialization, and random initialization; the lower panels show JAM's layerwise gain over video initialization. The consequence panel retains the copy-first reference, which JAM surpasses at layers 10, 15, and 20. `artifacts/representation_comparison.json` records source hashes, absolute values, and the derived gains. The appendix separately plots the complete action-input sensitivity comparison, whose paired intervals all include zero. These probe results describe information accessibility under partially visible future observations and window-based splits; the coupling ablations remain necessary to isolate the effect of joint computation.

## Experimental organization

The main text occupies **11 pages**, including the homepage teaser, framework, consequence interface, and all main experimental displays. References and appendix follow separately. Experimental setup contains exactly two paragraphs.

| Table | Benchmark or question | Contents |
|---|---|---|
| 1 | LIBERO-Plus | Seven perturbations and all 13 source baselines |
| 2 | LIBERO-PRO | Goal, Spatial, Long, Object, Total; six source baselines |
| 3 | VLABench | Overall SR, PS, IS; eight source baselines |
| 4 | Bimanual manipulation | RoboTwin2.0-Full and RoboDojo in side-by-side panels |
| 5 | Mobile manipulation | RoboCasa365 and EBench in side-by-side panels |
| 6 | Pretraining and reciprocal computation | Initialization and coupling controls, marked targets |
| 7 | Data and supervision | Mixture, capacity, and annotation density, marked targets |
| Appendix | Current recipe; LIBERO | Seven-source probabilities; all 18 standard LIBERO baselines |

The dataset-mixture figure is removed. The appendix reports the current runtime recipe directly. The full six-panel training-dynamics figure follows all main benchmark tables in a single Joint optimization subsection. Compact benchmark panels preserve their own baseline coverage, with pale-blue JAM rows and short headers.

RoboDojo reports overall success rate and overall task score, corresponding to the aggregate values from the former A and B panels. EBench reports overall success rate and task score. VLABench reports the source-reported overall SR, PS, and IS metrics.

`JAM direct` meant task adaptation from public video weights and a newly initialized agent, without JAM embodied pretraining. It was an initialization control, not a separate JAM method. Main benchmark tables now contain a single JAM row. The control appears only in the pretraining ablation, named **Without embodied pretraining**. Its displayed target scores remain marked T.

## Fixed evidence snapshot

The source project was inspected read-only at `/public/home/lixuan/lixuan/JAM`. The latest snapshot is **8 September 2026, 11:56 cluster time (UTC+8)**, revision `b46fd1b330593082995849f51a77ef51152751ab`, with foundation logs through update **10,501**. The current stage resumes from update 10,500. `artifacts/provenance.json` records source and published hashes; runtime configuration and logs identify the evidence cutoff.

The current mixture contains DROID (29.17%), BridgeData V2 (11.71%), EgoDex (16.45%), Ego4D (11.37%), RoboMIND AgileX (16.50%), RoboMIND Franka (3.36%), and RoboMIND UR5e (11.44%). These probabilities come from the runtime startup record and temperature-0.7 sampling over training-window counts. The manuscript appendix contains only this current recipe. Historical configurations and log prefixes remain archived for interpreting the training curves. EgoDex training data is sampled at 10 Hz.

Three evidence classes remain explicit:

- **Measured:** complete 20,000-update LIBERO adaptation losses; the foundation prefix through update 10,501; world-feature probes at update 5,100; and a corrected action-input sensitivity report. These diagnostics do not establish closed-loop performance or causal pretraining gains. The internal probe train/test split is window-based and can share episodes; future observations are partly visible during extraction. All non-oracle sensitivity intervals include zero.
- **External:** source-reported baseline values, with original strings, immutable revisions, hashes, and cell pointers. No external value is a JAM measurement. Missing source entries are NR, never zero.
- **Planned:** only controlled-study tables and the scaling display retain marked layout values from `experiments/layout_targets.json`. Superscript T and explicit plot labels identify them. They are neither measured results nor preregistered predictions. JAM benchmark rows instead say **Awaiting evaluation**.

The 8,400-update configuration boundary activates the displacement outlier mask and pure-noise inputs for absent modalities. Runtime sharding changes to single-node FULL_SHARD. Curves retain outliers and do not smooth across this boundary. The 10,500-update boundary changes to the current seven-source recipe. Its first update is the only logged point in this final segment; the display makes no claim about this segment's convergence.

## External attribution

The requested reference website's immutable benchmark export is archived in `artifacts/source_reports/benchmark_export.json`. Its 113 rows across nine simulation tables are indexed in `artifacts/external_baselines.json`. The manuscript contains 85 distinct source rows across seven export benchmarks, plus six LIBERO-PRO rows. The rendering audit covers 344 copied numeric/missingness cells. R1 denotes the external method named in that source; it is never a JAM alias. The website aggregates source-reported evaluations, so the manuscript does not assert that its authors reran every baseline under one protocol.

**LIBERO-PRO is absent from that export.** Its table uses the benchmark maintainers' pinned official README leaderboard, recorded in `artifacts/external_libero_pro.json`. Normalized success is converted to percentage exactly. The four displayed suite scores are derived as unweighted means of available published perturbation rates, rounded half up to one decimal. An asterisk identifies models whose environment tests are unreported. Total retains the source-reported aggregate. The full derivation is archived in `artifacts/libero_pro_aggregation.json`. `artifacts/rendered_baseline_cells.json` maps each displayed source cell back to the archived export.

## Repository and result updates

- `main.tex`, `Sections/`, `jam.bib`: manuscript and citations.
- `Figures/`, `Tables/`: editable diagrams, vector figures, and generated tables.
- `artifacts/`: evidence, sanitized configurations, source reports, and provenance.
- `experiments/`: protocol ledger and explicitly planned layout values.
- `scripts/`: generation and evidence/layout validation.
- `docs/revision_audit.md`: verified corrections and interpretation limits.

Promoting a pending row requires a checkpoint identity, completed task/reset manifest, per-episode results, aggregation command, and appropriate uncertainty estimates. Archive the artifact and its hash first, then regenerate the display and review the associated claim. Configuration snapshots use logical asset paths and document runs rather than providing standalone launch commands. No source-project code, training jobs, or datasets are modified by this manuscript workflow.
