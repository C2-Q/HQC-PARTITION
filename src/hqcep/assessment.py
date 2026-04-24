from __future__ import annotations

from .schema import AssessmentResult, EnergyWorkflowCase, QuantumComponentEvidence


def _target_matches_case(case: EnergyWorkflowCase, component: QuantumComponentEvidence) -> bool:
    problem = case.scheduling_problem.lower().replace("-", "_")
    target = component.target_subproblem.lower().replace("-", "_")
    return problem in target or target in problem


def _has_warning(component: QuantumComponentEvidence) -> bool:
    note = component.scalability_note.lower()
    warning_tokens = ["limited", "warning", "explor", "overhead", "constraint", "scal"]
    return component.encoding_overhead in {"medium", "high"} or any(token in note for token in warning_tokens)


def assess_component(case: EnergyWorkflowCase, component: QuantumComponentEvidence) -> AssessmentResult:
    blocking_conditions: list[str] = []
    positive_conditions: list[str] = []
    rationale: list[str] = []

    if component.classical_comparator in {"none", "weak", "unknown"}:
        blocking_conditions.append(
            f"Classical comparator is {component.classical_comparator}, which is below the minimum evidence threshold."
        )

    if component.evidence_level in {"toy", "unknown"}:
        blocking_conditions.append(
            f"Evidence level is {component.evidence_level}, which is not sufficient for workflow admission."
        )

    if component.encoding_overhead == "high" and component.provider_dependency == "specific_vendor":
        blocking_conditions.append(
            "High encoding overhead combined with specific vendor dependency blocks admission."
        )

    if not _target_matches_case(case, component):
        blocking_conditions.append(
            f"Target subproblem {component.target_subproblem!r} is not compatible with scheduling problem {case.scheduling_problem!r}."
        )

    if blocking_conditions:
        rationale.extend(blocking_conditions)
        rationale.append("Component is rejected because required evidence and compatibility conditions are not met.")
        return AssessmentResult(
            admissibility="reject",
            blocking_conditions=blocking_conditions,
            positive_conditions=positive_conditions,
            rationale=rationale,
        )

    if component.classical_comparator in {"acceptable", "strong"}:
        positive_conditions.append(f"Classical comparator is {component.classical_comparator}.")

    if component.evidence_level in {"simulated", "hardware_demo", "deployment_relevant"}:
        positive_conditions.append(f"Evidence level is {component.evidence_level}.")

    if component.target_subproblem:
        positive_conditions.append(f"Target subproblem {component.target_subproblem} is compatible with the case.")

    pilot_ready = (
        (
            component.evidence_level == "deployment_relevant"
            or (component.evidence_level == "hardware_demo" and component.classical_comparator == "strong")
        )
        and component.classical_comparator == "strong"
        and component.encoding_overhead != "high"
        and component.provider_dependency != "specific_vendor"
    )

    if pilot_ready:
        rationale.append("Component meets the conservative threshold for a pilot-admissible workflow insertion.")
        return AssessmentResult(
            admissibility="pilot_admissible",
            blocking_conditions=blocking_conditions,
            positive_conditions=positive_conditions,
            rationale=rationale,
        )

    exploratory_ready = (
        component.evidence_level in {"simulated", "hardware_demo"}
        and component.classical_comparator in {"acceptable", "strong"}
        and component.provider_dependency in {"simulator", "cloud_qpu", "specific_vendor"}
    )

    if exploratory_ready:
        if _has_warning(component):
            blocking_conditions.append(
                "Scalability or integration warnings require fallback and keep the component in exploratory status."
            )
        rationale.append("Component is admissible only for exploratory assessment-guided partitioning.")
        return AssessmentResult(
            admissibility="exploratory",
            blocking_conditions=blocking_conditions,
            positive_conditions=positive_conditions,
            rationale=rationale,
        )

    blocking_conditions.append("Component does not meet the conservative thresholds for exploratory admission.")
    rationale.append("Assessment falls back to reject because admissibility conditions were not satisfied.")
    return AssessmentResult(
        admissibility="reject",
        blocking_conditions=blocking_conditions,
        positive_conditions=positive_conditions,
        rationale=rationale,
    )
