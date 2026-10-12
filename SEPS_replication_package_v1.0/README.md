# SEPS replication package v1.0

Prepared: 2026-10-10

This is the frozen replication package for the manuscript:

**When recovery depends on policy priorities: Set-valued monitoring of multi-mission public-service recovery in national museums**

This is the public GitHub distribution edition of the frozen research materials. The unmodified original archive is preserved privately; the standalone third-party NAO PDF has been replaced by a verifiable official-source link for licensing reasons. See the repository root PUBLIC_RELEASE_NOTES.md.

## What is included

- `core_replication_v0.1/`: validated core replication package and source-derived analysis tables.
- `05_35_code_original/`: project analysis and figure scripts used for the current results.
- `05_35_inputs/`: frozen figure-ready inputs and assertion files.
- `05_35_gis_compact/`: GIS layers and provenance files used for the city-scale figure.
- `05_36_horizon_matched/`: pre-specified horizon-matched robustness materials and the labelled post-hoc Royal Armouries sensitivity.
- `figure_system_portable/`: relative-path, portable Figure 1–5 rebuild system.
- `final_artwork/`: final standalone figure files.
- `DATA_AVAILABILITY_STATEMENT.txt`: text prepared for the manuscript/submission declarations.
- `MANIFEST_SHA256.csv`: SHA256 manifest for all package files.

## Core empirical sources

The empirical source data are publicly available official statistics:

1. UK Department for Culture, Media and Sport (DCMS), *DCMS-sponsored Museums and Galleries Annual Performance Indicators 2024/25*.
2. DCMS, *Total Income of DCMS-funded cultural organisations 2023/24 and 2024/25*.
3. HM Treasury, *GDP deflators at market prices, and money GDP September 2026 (Quarterly National Accounts)*.
4. National Audit Office, *The financial resilience of DCMS-sponsored museums and galleries*, used for external comparison.
5. Geographic context/provenance for Figure 1 uses GLA, ONS, OpenStreetMap and Wikidata sources; detailed provenance and source URLs are stored with the GIS files.

## Reproduce the core manuscript benchmarks

```bash
cd core_replication_v0.1/replication_package_v0.1
python reproduce_core_results.py
```

Expected terminal status:

`PASS: core manuscript benchmark reproduced exactly.`

## Rebuild Figures 1–5

Install the dependencies in `figure_system_portable/requirements.txt`, then run:

```bash
python figure_system_portable/run_all_portable.py
```

The figure scripts contain value assertions so that the plotted scientific quantities are checked against the frozen inputs.

## Scope

The package reproduces a descriptive, set-valued public-sector monitoring analysis. It does not estimate a causal Grant-in-Aid effect, museum technical efficiency, financial-failure risk, or population-level effects for museums generally.

## Reuse and source licences

For public review, analysis code and derived materials may be inspected and run; separate licences apply to third-party datasets and maps. Original government and geographic source data remain subject to their respective source licences and attribution requirements. See the provenance files for the relevant geographic sources.
