from hqcep.partition import recommend_partition
from hqcep.schema import (
    AssessmentResult,
    EnergyWorkflowCase,
    QuantumComponentEvidence,
    WorkflowStage,
)


def make_case() -> EnergyWorkflowCase:
    return EnergyWorkflowCase(
        case_id="case",
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
        notes=[],
    )


def make_component() -> QuantumComponentEvidence:
    return QuantumComponentEvidence(
        component_id="component",
        source_id="planqk_euc",
        source_url="https://github.com/PlanQK/EnergyUnitCommitment",
        method_type="qaoa",
        target_subproblem="unit_commitment_binary_core",
        evidence_level="simulated",
        classical_comparator="acceptable",
        provider_dependency="cloud_qpu",
        encoding_overhead="high",
        scalability_note="Limited by encoding overhead.",
    )


def make_stages() -> list[WorkflowStage]:
    return [
        WorkflowStage("data_preparation", "Prepare data.", "classical", "Preprocessing."),
        WorkflowStage("binary_commitment", "Discrete binary commitment core.", "quantum_candidate", "Discrete stage."),
        WorkflowStage("dispatch_feasibility", "Check continuous dispatch feasibility.", "classical", "Continuous stage."),
        WorkflowStage("rolling_horizon_update", "Advance rolling horizon.", "classical", "Control stage."),
        WorkflowStage("postprocessing", "Export outputs.", "classical", "Reporting."),
    ]


def test_reject_assigns_all_classical() -> None:
    partition = recommend_partition(
        make_case(),
        make_component(),
        AssessmentResult(admissibility="reject", rationale=["Rejected"]),
        make_stages(),
    )
    assert set(partition.stage_assignments.values()) == {"classical"}
    assert partition.quantum_stage_ids == []
    assert partition.fallback_required is False


def test_exploratory_only_binary_commitment_is_quantum_candidate() -> None:
    partition = recommend_partition(
        make_case(),
        make_component(),
        AssessmentResult(admissibility="exploratory", rationale=["Exploratory"]),
        make_stages(),
    )
    assert partition.stage_assignments["binary_commitment"] == "quantum_candidate"
    assert partition.stage_assignments["dispatch_feasibility"] == "classical"
    assert partition.stage_assignments["rolling_horizon_update"] == "classical"
    assert partition.fallback_required is True


def test_pilot_keeps_dispatch_and_postprocessing_classical() -> None:
    partition = recommend_partition(
        make_case(),
        make_component(),
        AssessmentResult(admissibility="pilot_admissible", rationale=["Pilot"]),
        make_stages(),
    )
    assert partition.stage_assignments["binary_commitment"] == "quantum_candidate"
    assert partition.stage_assignments["dispatch_feasibility"] == "classical"
    assert partition.stage_assignments["postprocessing"] == "classical"
    assert partition.fallback_required is True
