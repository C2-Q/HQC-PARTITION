# Partition Report

- Case id: `pypsa_uc_workflow_example`
- Source URLs: `https://docs.pypsa.org/latest/examples/unit-commitment/`, `https://github.com/PlanQK/EnergyUnitCommitment`
- Component id: `planqk_qaoa_uc_component`
- Assessment result: `exploratory`
- Recommended partition: `pypsa_uc_workflow_example__planqk_qaoa_uc_component`
- Quantum stages: `binary_commitment`
- Classical stages: `data_preparation, dispatch_feasibility, ramp_and_min_up_down_checks, rolling_horizon_update, postprocessing`
- Fallback required: `True`

## Blocking conditions

- Scalability or integration warnings require fallback and keep the component in exploratory status.

## Rationale

- Exploratory partition allows only the discrete commitment core to be quantum-enabled.
- Dispatch, feasibility repair, rolling horizon control, and postprocessing remain classical.
- This is a limited exploratory partition, not a deployment recommendation.
- Component is admissible only for exploratory assessment-guided partitioning.

Warning: This is assessment guidance, not solver performance.
