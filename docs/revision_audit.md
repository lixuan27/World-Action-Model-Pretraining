# Experiment revision audit, 8 September 2026

This revision updates the experimental account from a fixed, read-only snapshot of JAM. The main scientific question and formulation remain intact. Source revision: `27a9703989073c12ef50f8ad2d4f733ea2bf4fe1`; evidence cutoff: foundation update 8,600 at 08:47 UTC+8. The earlier 5,200-update prefix is preserved in `artifacts/measurements/history/`.

## Verified changes

| Topic | Evidence | Manuscript decision |
|---|---|---|
| Consumed data | Five-source runtime mixture after resume at 8,400 | Add RoboMIND Franka and UR5e; show initial and current probabilities |
| Dataset expansion | Merged Ego4D cache; ongoing AgileX/InternData/RoboCOIN/EPIC preparation | Name the full selected pipeline and mark admission status separately |
| EgoDex timing | Training export keeps every third original frame | Correct 30 Hz to 10 Hz |
| Ego4D split | 436,116 train and 50,856 holdout windows; no shared video identifiers | Record grouping and counts; world-only initial admission |
| Runtime topology | Startup excerpt records FULL_SHARD, mesh (8,) | Separate actual single-node runtime from the config's hybrid strategy request |
| Recipe boundary | Mixture, outlier mask, missing-modality inputs, and sharding all change at 8,400 | Preserve the boundary and avoid single-cause attribution |
| Probes | Frozen-world layer sweep with ridge readouts and reference initializations | Plot every sampled layer instead of selecting the best test layer |
| Probe information | Future-world corruption 0.5; action/consequence corruption 1 | State visible future context and restrict interpretation to readout |
| Probe split | Up to 4,000 holdout-corpus windows internally split by window | Report possible shared episodes; require episode-disjoint confirmation |
| Conditional sampler | Unobserved consequences now integrate independently of clamped actions | Replace obsolete unresolved-sampler statement; retain fidelity evaluation as pending |
| Action sensitivity | Corrected 300-window report has all non-oracle intervals spanning zero | Plot the measured negative/weak signal without a causal-prediction claim |
| Benchmark provenance | Full immutable source export and official PRO leaderboard | Preserve numeric strings, missingness, and model-dependent evaluation scope |
| JAM benchmark results | No completed full-suite artifact in this snapshot | Use one blue Awaiting evaluation row per benchmark |
| Direct adaptation | Public video initialization plus fresh agent, followed by task adaptation | Rename as Without embodied pretraining and place only in initialization ablation |

## Benchmark organization

The six requested benchmarks each have one main-text table. Multi-panel tables keep distinct metrics within the same benchmark: VLABench has success/progress/intention panels; RoboDojo has success/score panels; LIBERO-PRO separates its four suites. Standard LIBERO appears in one appendix table. Every available source baseline is retained for these benchmarks.

The requested website contains no LIBERO-PRO table. Its official benchmark-maintainer leaderboard is the separately attributed fallback. Percentage conversion multiplies the original normalized values by 100, preserving reported totals and unreported environment tests. R1 remains the external system identified by the immutable source link. It is not a renamed JAM result. Source-reported scores may come from different original evaluation implementations.

## Visual and layout checks

Experimental setup remains two paragraphs. Tables span the text width, use short headers, hierarchical rules, and a pale-blue JAM row. Matplotlib figures use DejaVu Serif with embedded vector fonts. New main figures show data admission, measured foundation optimization, and measured representation diagnostics. The appendix retains the complete six-panel optimization record. The scaling figure remains explicitly planned. The main text includes the existing teaser, framework, and consequence schematic within 12 pages.

Validation checks source hashes, every copied baseline row and displayed cell, PRO percentage conversion, mixture probabilities, actual loss records, measured-probe settings, superscript target markers, references, citations, and the compiled page limit. PDF pages are rasterized for visual review after compilation. No training work is launched or changed.

## Evidence boundaries

Only the controlled pretraining/scaling designs retain layout targets. Their superscript T and captions identify them as awaiting measurement; they are not preregistered outcomes. The abstract and conclusion continue limiting empirical conclusions to supported implementation and optimization evidence. Probes add preliminary readout measurements, not a closed-loop or causal pretraining claim.

Remaining research includes completed foundation releases, full-suite adaptation/evaluation, condition-matched coupling controls, episode-disjoint probes, executed alternative-action futures, conditional fidelity, and data-overlap audits for newly admitted sources. These belong to the active training project.
