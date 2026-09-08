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

Experimental setup remains two paragraphs. All main benchmark tables precede the Joint optimization subsection. The Figure 3 revision brings the main text to 11 pages, with references and appendix separate. Tables use full-width composition, hierarchical rules, short labels, and pale-blue JAM rows. Numerical plots retain embedded DejaVu Serif vector fonts.

Validation checks source hashes, copied cells, PRO aggregation, current mixture probabilities, measured records, references, citations, target markers, and the main-page limit. Final PDF pages are rasterized and reviewed for overlaps and clipping. No source-project code or training jobs are changed.

## Consequence-supervision figure revision

Figure 3 now follows the drawing requirements in the user's reference task, `01a07e80-5bdf-71f3-b277-99058429ac35`: white background, Toppan Bunkyu Mincho text, restrained blue-gray and teal fills, gray local arrows, and dark-red main flow arrows. The gripper-track schematic comes unchanged from slide 1 of the supplied version-9 framework deck. It is an illustration, not an observation or a model prediction.

The diagram separates tracked image motion, anchor-relative displacement, target encoding, and masked joint training. Its binary examples give masks (1,1,1) for a valid visible point, (0,0,1) for an occluded point with a valid anchor, and (0,0,0) for an absent slot. Gray target zeros are stored values excluded from supervision. A separate mask arrow enters the joint loss. Human labels are described as projected supplied hand poses, matching the active adapter; the drawing makes no claim of measured cross-embodiment invariance.

`scripts/build_consequence_figure.py` checks text bounds and text intersections, then exports the PDF, PNG, live-text SVG, and outlined SVG. The smallest text is 8.12 pt at the manuscript's 6.5-inch width. The PDF embeds vector glyph outlines for the CFF/OpenType font. Experimental page breaks become float barriers so the expanded figure does not leave an isolated adaptation paragraph on an otherwise empty page. Experimental content, ordering, and values are preserved.

## Framework replacement from the supplied PowerPoint

Figure 2 now uses the single slide in the user-supplied `JAM-framework-joint-flow-v11.pptx`. The original deck is archived unchanged in `Figures/source/JAM-framework-v11.pptx`. PowerPoint exports the figure natively to PDF, preserving vector geometry, mathematical artwork, embedded fonts, and the original layout. A font-normalization script adds only Unicode maps to the embedded Toppan CID fonts. It verifies that all page drawing streams remain byte-identical. This avoids missing text in PDF readers without Adobe-Japan1 language maps.

The Figure 2 caption describes masked supervision, independent corruption, reciprocal attention, and joint sampling, and expands the diagram's architecture acronyms. Figure numbering and the framework cross-reference are preserved. Figure 2 is on page 3; Figure 3 remains on page 5. The main text remains 11 pages. The supplied presentation is unchanged, and no experiment values or training artifacts are modified.

The latest refresh uses `/Users/lixuan/Desktop/JAM-Figures/Framework/JAM-framework-joint-flow-v11.pptx`, source SHA-256 `ebaed152c82ceb37e3f1b1437d923febd9aee88168a3ca20fa25322bbde26b28`. It retains the updated bottom title, emphasized labels, and revised diagram details. Native export runs on a separate working copy. The archived source remains byte-identical to the supplied file. All 58 live-text labels are checked against the PDF; the styled title is exported as artwork and is verified visually. The Unicode-map repair also covers the source's Toppan Gothic heading. Standalone and manuscript rendering remain free of missing text or clipping.
