# Manuscript revision audit, 7 September 2026

The manuscript now centers on one question: how does action learning influence the world representation through reciprocal generative computation? The six main sections progress from that question through the joint model, heterogeneous supervision, and controlled evaluation. Engineering detail and implementation limits are in the appendix.

## Evidence inspected

Read-only server snapshot: `/public/home/lixuan/lixuan/JAM`. Audit HEAD: `9bb88f9dd77bf01d523c367991556ac0df7129d7`. Reviewed the world and agent implementations, coupling masks, flow schedule, masked objective, sampler, action layout, normalization, cache partitioning, robot/human adapters, experimental configurations, research design, decision log, narrative, training ledger, daily notes, training logs, and result files. The companion manifest records hashes for core implementation files and all archived measurements.

The live project continued changing during the audit. This paper uses a fixed evidence cutoff: foundation update 5,200 and the complete 20,000-update direct-adaptation record. A repository HEAD is not a substitute for the launch revision of a particular run. Neither server source code nor jobs were modified.

## Corrections affecting the scientific account

| Topic | Verified state | Manuscript decision |
|---|---|---|
| Independent noise | UWM already draws modality levels independently and uses flexible conditioning | Cite this precedent explicitly; focus JAM on reciprocal representation learning and consequence supervision |
| Consequence noise | Resolved objective sets `consequence_level: independent` | Use a separate consequence noise variable throughout |
| Boundary training | Resolved `p_boundary` is zero | Remove claims that explicit boundary rays were trained in the primary run |
| Human consequences | EgoDex adapter projects supplied hand poses and camera calibration | Describe tracked annotations accurately; do not call the active recipe fully self-supervised from raw video |
| Foundation data | Active DROID, Bridge, full EgoDex | Distinguish active cached windows from acquired or planned corpora |
| Training stage | Robot-only pointer was changed before update zero | Describe joint robot/human training from the first update |
| Available measurements | Direct adaptation finished; foundation training ongoing; closed-loop suite output incomplete | Training curves are measured; benchmark and representation tables are marked layout targets |
| Initialization | Public video backbone plus a fresh agent, followed by JAM embodied training | State initialization explicitly; avoid implying the video prior was trained from scratch |
| Visibility control | Disabling agent visibility also changes world access to state | Require equal static conditioning before attributing gains to generated-token coupling |
| Conditional sampler | Action clamping can hold an unobserved consequence latent fixed | Keep conditional fidelity pending until the schedule is resolved or all clamped variables are supplied |
| Corruption support | Independent levels do not establish correctness of every deployment sampler | Remove the unsupported all-path validity proposition |
| Interventions | Shuffling tests sensitivity; causal prediction needs matching alternative futures | Specify paired simulator states and rollout targets |
| Consequence transfer | Image coordinates retain camera and morphology dependence | Treat invariance as a tested property rather than a definition |
| Data quality | Extreme projected displacement labels affected the first segment | Preserve that segment's losses; treat the added mask as a separate correction awaiting evaluation |
| External metrics | Source clean-to-randomized mean is 69.0; randomized-only score is 48.7 | Keep these as distinct metrics with immutable source pointers |
| Benchmark scope | Current priority is four downstream arenas | Organize main comparisons around these, with robustness axes and external anchors separately |

## Editorial decisions

- Introduction: five paragraphs, one question, no experimental numbers or formulas.
- Related Work: three paragraphs, with corrected UWM authors and a precise relationship to Cosmos Policy.
- Method: three defining equations plus the masked objective and consequence definition. Remove the noise-plane theorem and parallel inference-mode narrative.
- Framework: editable TikZ showing inputs, shared conditions, coupled streams, velocity outputs, and masked supervision.
- Consequence figure: explicitly schematic. No illustrative drawing is presented as a model prediction.
- Experiments: one short pointer paragraph per experiment; training evidence and planned evaluation displays remain visibly distinct.
- Appendix: exact implementation choices, interpretation requirements, failure conditions, provenance, and source results.
- Abstract and conclusion: limit empirical statements to the observed joint optimization record.

## Evidence promotion rules

Layout values are tagged `PLANNED-VALUE` and rendered with superscript T. They were inherited or extended for manuscript layout, not preregistered and not estimated results. Promotion to a measurement requires an archived result, exact configuration and checkpoint, protocol manifest, aggregation command, and uncertainty estimate where appropriate. No target ordering is used as a scientific conclusion.

R1 is the external system named in the linked immutable source, not a renamed JAM model. Original source URLs and table pointers are retained exactly. Copying its values never creates a JAM measurement, and a full-suite source mean is not directly comparable to a target-task subset.

## Remaining scientific work

Complete foundation releases and matched downstream adaptation, repair the condition confound for coupling controls, complete probes and paired interventions, validate conditional samplers with latent consequences, audit data overlap for newly incorporated sources, and report errors with completed suite records. This work belongs to the training project; the manuscript revision does not launch or duplicate it.

## Layout refinement, 7 September 2026

- Condensed Experimental setup to two natural paragraphs and moved exact source counts, proportions, optimizer settings, splits, and evaluation protocols to Appendix B.
- Deleted the old data-inventory Table 1; automatic numbering now starts with the consolidated downstream-control table.
- Replaced eight small experimental displays with four full-width panelled tables. Native `tabularx` columns keep pale-blue shading continuous across each JAM row. Headers and cells use concise phrases rather than protocol prose.
- Expanded the LIBERO, LIBERO-Plus, RoboTwin Full, and VLABench breakdowns using 13 additional baseline rows from the same immutable export. All 27 external rows retain exact source strings and pointers. Source aggregation is preserved rather than recomputed.
- Extended the layout-only JAM arrays for the corresponding subcategories and consequence controls. Every new score remains marked T, and the target manifest records their status explicitly.
- Added a homepage overview and paired-intervention schematic. Kept the detailed framework and consequence interface. The measured optimization figure now displays both archived runs, with unsupervised records masked and foundation outliers preserved. The planned scaling figure adds agent capacity as a third panel.
- Kept the experiments adjacent to their displays and placed the conclusion on the final main page. The main text uses 9 pages, within the 12-page limit. References and appendix follow separately.
- Extended validation to check paragraph count, full-width tables, missing cells, homepage teaser placement, main-page budget, and exact external-row provenance. This revision preserves the existing evidence cutoff and launches no training.
