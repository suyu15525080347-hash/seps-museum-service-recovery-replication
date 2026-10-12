# Replication package v0.1
Prepared: 2026-10-09

## Purpose
This package reproduces the core quantitative claims in the manuscript *When recovery depends on policy priorities: Set-valued monitoring of multi-mission public-service recovery in national museums*.

The package is intentionally limited to public institutional data. It contains no personal data, survey microdata or confidential museum information.

## Quick reproduction
Requirements: Python 3.9+; the portable core check uses only the Python standard library.

Run:
```
python reproduce_core_results.py
```

A successful run prints the reconstructed summary and ends with:
`PASS: core manuscript benchmark reproduced exactly.`

The portable script recomputes, from the source-audited FY2020/21–FY2024/25 five-mission trajectories:
- 50 complete museum-year observations from 10 museum groups;
- equal-weight masking mean 0.2299 and median 0.2200;
- visitor-only masking mean 0.2407 and median 0.2447;
- bottleneck counts by mission;
- tau=.90 equal-weight/all-mission/visitor masking counts;
- 23 RED / 25 AMBER / 2 GREEN unrestricted-weight states;
- all leave-one-mission-out masking means;
- cap 1.00 / 1.25 / uncapped masking results.

## Folder structure
- `raw/`: official DCMS performance and income ODS files, HM Treasury September 2026 GDP deflator workbook, and the 2026 NAO report used for source cross-validation.
- `data/`: source-audited museum-year panel and analysis-ready derived trajectories/benchmarks.
- `qa/`: machine-readable source/comparability and robustness checks.
- `code/`: archived project scripts used to build the panel, audit source definitions, run robustness checks and generate manuscript tables/figures.
- `outputs/`: manuscript tables plus the portable reproduced-core-results JSON.
- `MANIFEST_SHA256.csv`: file sizes and SHA-256 checksums.

## Important methodological boundaries
The package does not estimate a causal effect of Grant-in-Aid, does not predict financial failure, and does not estimate technical efficiency. Grant-in-Aid is descriptive resource context only.

The primary service-recovery attainment is capped at 1.0 relative to FY2018/19 so that above-baseline recovery in one mission does not compensate a shortfall in another mission. The unrestricted policy-weight set is non-negative and sums to one. For epsilon=0 the weighted-score envelope equals the weakest-to-strongest mission interval.

The illustrative thresholds (.75, .80, .90 and 1.00) are sensitivity cases, not learned or official DCMS action thresholds. The threshold-free equal-weight masking span is the primary aggregation-loss measure.

## Source-comparability note
The DCMS UK-loan-venue source contains an internal final-column label inconsistency. The source workbook title extends through FY2024/25, the final institution values sum to 1,078 and the DCMS FY2024/25 headline also reports 1,078 venues. The original source file is preserved unchanged; the reconciliation is documented in `qa/UK_DCMS_Table9_loanvenue_2023_25_header_source_discrepancy_QA_v1.json`.

## Public source locations
- DCMS museum performance statistics: https://www.gov.uk/government/statistics/dcms-sponsored-museums-and-galleries-annual-performance-indicators-202425
- DCMS cultural-organisation income statistics: https://www.gov.uk/government/statistics/total-income-of-dcms-funded-cultural-organisations-202324-and-202425
- HM Treasury September 2026 GDP deflators: https://www.gov.uk/government/statistics/gdp-deflators-at-market-prices-and-money-gdp-september-2026-quarterly-national-accounts
- National Audit Office museum financial-resilience report: https://www.nao.org.uk/reports/the-financial-resilience-of-dcms-sponsored-museums-and-galleries/

## Archival scripts versus portable script
The `code/` directory preserves the exact project scripts, including project-directory discovery logic used during analysis. These files provide the audit trail from raw official files to manuscript outputs. For an external reviewer who only wants to verify the principal numerical claims without reproducing every ingestion step, `reproduce_core_results.py` is the portable entry point.

## Before public deposition
The author should choose a public repository and assign a persistent identifier. After deposition, update the manuscript Data Availability statement with the repository URL/DOI and archive the exact submitted package version.
