# Assessment-Guided Partition for Hybrid Quantum-Classical Scheduling Workflows

Assessment-guided partition for hybrid quantum-classical scheduling workflows.

<p align="center">
  <img src="assets/readme_figure.png" width="900" alt="HQC partition overview">
</p>

## Problem

Digital energy scheduling workflows such as unit commitment may include candidate quantum-enabled optimisation components. The practical question is not whether quantum optimisation is promising in general. The practical question is whether a quantum component is admissible for a workflow and, if so, which stages should remain classical and which may be quantum. This repository asks: "Given a scheduling workflow and a candidate quantum-enabled optimisation component, is the component admissible, and where could it be placed in the workflow?"

## What this repo does

- builds small case sheets from public unit commitment sources,
- represents candidate quantum components as evidence profiles,
- applies conservative assessment rules,
- outputs a recommended hybrid partition and blocking rationale,
- extracts simple workflow features from selected PGLib-UC cases.

## Data/source grounding

- PGLib-UC: https://github.com/power-grid-lib/pglib-uc
- PyPSA Unit Commitment example: https://docs.pypsa.org/latest/examples/unit-commitment/
- PlanQK EnergyUnitCommitment: https://github.com/PlanQK/EnergyUnitCommitment
- PyPSA-stochUC as a later representative case: https://github.com/PPGS-Tools/PyPSA-stochUC
- 6GESS energy-systems context: https://www.6gflagship.com/6gess/

## Quick demo

```bash
python scripts/run_partition_demo.py
```

Expected output:
- `outputs/demo/partition_report.json`
- `outputs/demo/partition_report.md`

## Case-feature extraction

```bash
python scripts/build_case_features.py
```

Expected:
- `outputs/case_features/pglib_uc_case_features.csv`
- `outputs/case_features/fig_case_feature_matrix.png`

## Current status

This is a small research seed. The demo remains a conservative rule-based partition advisor. The repository includes selected PGLib-UC case-feature extraction and a feature-matrix figure based on selected public PGLib-UC cases. The output is assessment guidance, not solver performance.
