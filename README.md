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

The first Tectonic build downloads standard TeX packages. Framework diagrams use editable TikZ. Five scientific figures are generated with Matplotlib in DejaVu Serif and exported as vector PDFs plus PNG previews. Paper builds launch no training.

## Experimental organization

The main text occupies **12 pages**, including the homepage teaser, framework, consequence interface, and all main experimental displays. References and appendix follow separately. Experimental setup contains exactly two paragraphs.

| Table | Benchmark or question | Contents |
|---|---|---|
| 1 | LIBERO-Plus | All seven perturbation axes and all 13 external baselines |
| 2 | LIBERO-PRO | Four suites, five perturbations, six external baselines |
| 3 | VLABench | Success, progress, and intention; eight external baselines |
| 4 | RoboTwin2.0-Full | Clean and randomized control; 14 external baselines |
| 5 | RoboCasa365 | Atomic and compositional tasks; 10 external baselines |
| 6 | RoboDojo | Six capability groups, success and score; 13 external baselines |
| 7 | Pretraining and reciprocal computation | Initialization and coupling controls, marked layout targets |
| 8 | Data and supervision | Mixture, capacity, and annotation-density controls, marked layout targets |
| Appendix | Pretraining inventory; LIBERO | Data admission status; all 18 standard LIBERO baselines |

Each benchmark has one full-width table. Panels separate metrics within that benchmark. Short headers, horizontal rules, and a pale-blue JAM row keep the organization consistent. The old mixed-benchmark summary tables are removed.

`JAM direct` meant task adaptation from public video weights and a newly initialized agent, without JAM embodied pretraining. It was an initialization control, not a separate JAM method. Main benchmark tables now contain a single JAM row. The control appears only in the pretraining ablation, named **Without embodied pretraining**. Its displayed target scores remain marked T.

## Fixed evidence snapshot

The source project was inspected read-only at `/public/home/lixuan/lixuan/JAM`. The latest snapshot is **8 September 2026, 08:47 cluster time (UTC+8)**, revision `27a9703989073c12ef50f8ad2d4f733ea2bf4fe1`, with foundation logs through update **8,600**. Live training continues independently. `artifacts/provenance.json` records exact source and published hashes; a source HEAD identifies the audit rather than every run's launch revision.

The consumed mixture now contains DROID, BridgeData V2, EgoDex, RoboMIND Franka, and RoboMIND UR5e. The RoboMIND sources enter after update 8,400. Their five sampling probabilities are 40.44%, 16.24%, 22.80%, 4.66%, and 15.87%. Ego4D is merged; RoboMIND AgileX, InternData-A1, RoboCOIN, and EPIC-KITCHENS-100 remain in preparation or acquisition. Access-gated candidates are recorded separately. Prepared data is not counted as consumed exposure. The EgoDex training export operates at **10 Hz**, correcting the earlier 30 Hz description.

Three evidence classes remain explicit:

- **Measured:** complete 20,000-update LIBERO adaptation losses; the foundation prefix through update 8,600; world-feature probes at update 5,100; and a corrected action-input sensitivity report. These diagnostics do not establish closed-loop performance or causal pretraining gains. The internal probe train/test split is window-based and can share episodes; future observations are partly visible during extraction. All non-oracle sensitivity intervals include zero.
- **External:** source-reported baseline values, with original strings, immutable revisions, hashes, and cell pointers. No external value is a JAM measurement. Missing source entries are NR, never zero.
- **Planned:** only controlled-study tables and the scaling display retain marked layout values from `experiments/layout_targets.json`. Superscript T and explicit plot labels identify them. They are neither measured results nor preregistered predictions. JAM benchmark rows instead say **Awaiting evaluation**.

The recipe boundary also activates the displacement outlier mask and pure-noise inputs for absent modalities. Runtime sharding changes to single-node FULL_SHARD. Curves retain outliers and do not smooth across this boundary. These simultaneous changes require separate controls before attributing a loss change to one cause.

## External attribution

The requested reference website's immutable benchmark export is archived in `artifacts/source_reports/benchmark_export.json`. Its 113 rows across nine simulation tables are indexed in `artifacts/external_baselines.json`. The seven manuscript benchmark tables contain 76 distinct rows from this export plus six LIBERO-PRO rows. R1 denotes the external method named in that source; it is never a JAM alias. The website aggregates source-reported evaluations, so the manuscript does not assert that its authors reran every baseline under one protocol.

**LIBERO-PRO is absent from that export.** Its table uses the benchmark maintainers' pinned official README leaderboard, recorded in `artifacts/external_libero_pro.json`. Normalized success is converted to percentage exactly. The reported totals are preserved, including differing coverage of environment tests. `artifacts/rendered_baseline_cells.json` maps each displayed source cell back to the archived export.

## Repository and result updates

- `main.tex`, `Sections/`, `jam.bib`: manuscript and citations.
- `Figures/`, `Tables/`: editable diagrams, vector figures, and generated tables.
- `artifacts/`: evidence, sanitized configurations, source reports, and provenance.
- `experiments/`: protocol ledger and explicitly planned layout values.
- `scripts/`: generation and evidence/layout validation.
- `docs/revision_audit.md`: verified corrections and interpretation limits.

Promoting a pending row requires a checkpoint identity, completed task/reset manifest, per-episode results, aggregation command, and appropriate uncertainty estimates. Archive the artifact and its hash first, then regenerate the display and review the associated claim. Configuration snapshots use logical asset paths and document runs rather than providing standalone launch commands. No source-project code, training jobs, or datasets are modified by this manuscript workflow.
