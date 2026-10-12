# Multi-mission public-service recovery in UK national museums — replication package

This **public GitHub repository** contains the data, scripts, robustness checks and figure-generation materials supporting the manuscript **"When recovery depends on policy priorities: Set-valued monitoring of multi-mission public-service recovery in national museums"** (Socio-Economic Planning Sciences submission project).

The scientific analysis is frozen; this public-distribution edition differs from the original private 2026-10-10 archive only in licensing/documentation, the exclusion of a third-party National Audit Office (NAO) PDF, and a link to its official source. No empirical data, analysis code, numerical results or figure assets were changed for public release. Details appear in `PUBLIC_RELEASE_NOTES.md`.

## Reproduce core findings

From this repository root:

```bash
cd SEPS_replication_package_v1.0/core_replication_v0.1/replication_package_v0.1
python reproduce_core_results.py
```

Expected: `PASS: core manuscript benchmark reproduced exactly.`

The output covers 10 museum groups × 5 post-pandemic financial years (50 museum-years), with 23 RED, 25 AMBER, and 2 GREEN at the illustrative 0.90 benchmark.

## Rebuild Figures 1–5

From the repository root, install packages listed in `SEPS_replication_package_v1.0/figure_system_portable/requirements.txt` and run `python SEPS_replication_package_v1.0/figure_system_portable/run_all_portable.py`.

## Data, provenance, reuse conditions

The empirical museum-year input tables are sourced from UK DCMS official statistics and HM Treasury deflators. Geographic GIS layers and base maps use sources from GLA, ONS, OpenStreetMap and Wikidata. See `THIRD_PARTY_ATTRIBUTION_AND_LICENSE_REVIEW.md` and the included geographic provenance metadata for licensing and attribution; OpenStreetMap-derived database layers are subject to ODbL. No blanket license is granted over third-party content.

The NAO report used for an external comparison is **not mirrored**, because of separate reproduction rights; access the official report at https://www.nao.org.uk/reports/the-financial-resilience-of-dcms-sponsored-museums-and-galleries/ . Its archived source checksum appears in `SEPS_replication_package_v1.0/core_replication_v0.1/replication_package_v0.1/raw/NAO_SOURCE_LINK.txt`.

## Integrity and limitations

`SEPS_replication_package_v1.0/MANIFEST_SHA256.csv` records the updated checksum of each distributed file in the public edition. The full unmodified original ZIP remains preserved privately by the research team. This analysis provides descriptive set-valued monitoring, **not** causal estimates, efficiency measurement, or optimal resource-allocation solutions.

Repository URL: https://github.com/suyu15525080347-hash/seps-museum-service-recovery-replication

**No DOI has been assigned to this GitHub repository**. A future archival repository deposit or versioned release may provide a persistent identifier.
