# Experiment revision audit, 8 September 2026

This revision updates the experimental account from a fixed, read-only snapshot of JAM. The main scientific question and formulation remain intact. The current source revision and evidence cutoff are specified below. The earlier 5,200-update prefix is preserved in `artifacts/measurements/history/`.

## Current experiment revision

The current runtime snapshot is `b46fd1b330593082995849f51a77ef51152751ab`, captured at 11:56 UTC+8 on 8 September 2026. Foundation evidence extends to update 10,501. The startup log confirms seven-source sampling after the 10,500-update resume. Historical prefixes remain archived.

| Request | Final manuscript change |
|---|---|
| Remove data-mixture figure | Delete its PDF/PNG and generator; put current source counts and probabilities in the appendix |
| Use the latest recipe | Seven active sources, read from the resolved runtime mixture; no preparation roadmap in the manuscript |
| Consolidate training dynamics | One six-panel plot after all main benchmark results, covering foundation and task adaptation |
| Compact LIBERO-PRO | Goal, Spatial, Long, Object, Total; suite means derived from reported perturbation rates |
| Compact VLABench | Overall SR, PS, IS, preserving all source baseline rows |
| Merge bimanual benchmarks | One table, with RoboTwin2.0-Full and RoboDojo side-by-side; RoboDojo reports overall SR and Score |
| Merge mobile benchmarks | One table, with RoboCasa365 and EBench side-by-side; EBench reports overall SR and Score |

## Numeric provenance

All 85 source baseline rows for the selected export benchmarks are retained, with 344 copied source cells. Side-by-side panels keep each benchmark's own model coverage and avoid manufacturing values for a model absent from another benchmark. EBench comes from the same pinned export as the other reference benchmarks.

LIBERO-PRO's four suite values are arithmetic means of the published perturbation percentages, rounded half up to one decimal. Its reported Total is copied. Unreported environment tests are excluded from the corresponding suite mean, with affected rows flagged by an asterisk. The derivation is written to `artifacts/libero_pro_aggregation.json` and independently checked during validation. The reduced table therefore distinguishes derived summaries from published totals.

## Scientific boundaries

The update-5,100 probes precede the current recipe. Their heldout-corpus windows are split internally by window and can share episodes; future-world inputs are partly observed. They remain preliminary readout diagnostics. The corrected action-input sensitivity intervals all span zero. Executed alternative-action futures are required for a causal prediction claim.

At update 8,400, the mixture, displacement mask, missing-modality inputs, and runtime topology change together. At update 10,500, the current seven-source mixture begins. The archived final segment contains one logged update. Curves preserve raw outliers and restart smoothing across these boundaries. JAM benchmark rows await completed evaluations; controlled-study targets remain explicitly marked T.

## Layout and validation

Experimental setup remains two paragraphs. All main benchmark tables precede the Joint optimization subsection. Main text is 10 pages, with references and appendix separate. Tables use full-width composition, hierarchical rules, short labels, and pale-blue JAM rows. Scientific plots retain embedded DejaVu Serif vector fonts.

Validation checks source hashes, copied cells, PRO aggregation, current mixture probabilities, measured records, references, citations, target markers, and the main-page limit. Final PDF pages are rasterized and reviewed for overlaps and clipping. No source-project code or training jobs are changed.
