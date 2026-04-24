from hqcep.assessment import assess_component
from hqcep.schema import EnergyWorkflowCase, QuantumComponentEvidence


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


def make_component(**overrides: str) -> QuantumComponentEvidence:
    payload = {
        "component_id": "component",
        "source_id": "planqk_euc",
        "source_url": "https://github.com/PlanQK/EnergyUnitCommitment",
        "method_type": "qaoa",
        "target_subproblem": "unit_commitment_binary_core",
        "evidence_level": "simulated",
        "classical_comparator": "acceptable",
        "provider_dependency": "cloud_qpu",
        "encoding_overhead": "medium",
        "scalability_note": "Limited integration scale.",
    }
    payload.update(overrides)
    return QuantumComponentEvidence(**payload)


def test_weak_comparator_rejects() -> None:
    result = assess_component(make_case(), make_component(classical_comparator="weak"))
    assert result.admissibility == "reject"


def test_toy_evidence_rejects() -> None:
    result = assess_component(make_case(), make_component(evidence_level="toy"))
    assert result.admissibility == "reject"


def test_simulated_acceptable_cloud_is_exploratory() -> None:
    result = assess_component(make_case(), make_component(provider_dependency="cloud_qpu"))
    assert result.admissibility == "exploratory"


def test_deployment_relevant_strong_is_pilot_admissible() -> None:
    result = assess_component(
        make_case(),
        make_component(
            evidence_level="deployment_relevant",
            classical_comparator="strong",
            provider_dependency="cloud_qpu",
            encoding_overhead="low",
            scalability_note="Controlled integration path.",
        ),
    )
    assert result.admissibility == "pilot_admissible"
