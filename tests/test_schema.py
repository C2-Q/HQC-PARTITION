from pathlib import Path

from hqcep.schema import (
    AssessmentResult,
    EnergyWorkflowCase,
    PartitionRecommendation,
    QuantumComponentEvidence,
    WorkflowStage,
    as_dict,
    quantum_component_from_dict,
    read_yaml,
    workflow_case_from_dict,
    workflow_stage_from_dict,
)


ROOT = Path(__file__).resolve().parents[1]


def test_schema_instantiation() -> None:
    case = EnergyWorkflowCase(
        case_id="case-1",
        source_id="pypsa_uc",
        source_url="https://docs.pypsa.org/latest/examples/unit-commitment/",
        workflow_type="scheduling_workflow",
        scheduling_problem="unit_commitment",
        horizon_hours=24,
        num_generators=None,
        has_reserve_requirement=None,
        has_ramp_constraints=True,
        has_min_up_down_constraints=True,
        has_startup_shutdown_costs=True,
        has_renewables=None,
        has_storage=False,
        rolling_horizon=True,
        notes=["example"],
    )
    stage = WorkflowStage(
        stage_id="binary_commitment",
        description="Discrete commitment core.",
        default_side="quantum_candidate",
        rationale="Discrete structure.",
    )
    component = QuantumComponentEvidence(
        component_id="component-1",
        source_id="planqk_euc",
        source_url="https://github.com/PlanQK/EnergyUnitCommitment",
        method_type="qaoa",
        target_subproblem="unit_commitment_binary_core",
        evidence_level="simulated",
        classical_comparator="acceptable",
        provider_dependency="cloud_qpu",
        encoding_overhead="high",
        scalability_note="Limited by problem size.",
    )
    assessment = AssessmentResult(admissibility="exploratory")
    partition = PartitionRecommendation(
        partition_id="partition-1",
        stage_assignments={"binary_commitment": "quantum_candidate"},
    )

    assert as_dict(case)["case_id"] == "case-1"
    assert stage.default_side == "quantum_candidate"
    assert component.method_type == "qaoa"
    assert assessment.admissibility == "exploratory"
    assert partition.partition_id == "partition-1"


def test_yaml_examples_deserialize() -> None:
    workflow_payload = read_yaml(ROOT / "case_sheets/examples/pypsa_uc_workflow_example.yaml")
    component_payload = read_yaml(ROOT / "case_sheets/examples/planqk_quantum_component_example.yaml")

    case = workflow_case_from_dict(workflow_payload["case"])
    stages = [workflow_stage_from_dict(item) for item in workflow_payload["stages"]]
    component = quantum_component_from_dict(component_payload["components"][0])

    assert case.case_id == "pypsa_uc_workflow_example"
    assert any(stage.stage_id == "binary_commitment" for stage in stages)
    assert component.component_id == "planqk_qaoa_uc_component"
