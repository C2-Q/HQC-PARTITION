from __future__ import annotations

from .schema import AssessmentResult, EnergyWorkflowCase, PartitionRecommendation, QuantumComponentEvidence, WorkflowStage


def _is_binary_commitment_stage(stage: WorkflowStage) -> bool:
    text = f"{stage.stage_id} {stage.description}".lower()
    return "binary_commitment" in text or ("commitment" in text and ("binary" in text or "discrete" in text))


def _matches_target(stage: WorkflowStage, component: QuantumComponentEvidence) -> bool:
    target = component.target_subproblem.lower()
    text = f"{stage.stage_id} {stage.description}".lower()
    if "binary_core" in target:
        return _is_binary_commitment_stage(stage)
    return any(token in text for token in target.split("_") if token)


def recommend_partition(
    case: EnergyWorkflowCase,
    component: QuantumComponentEvidence,
    assessment: AssessmentResult,
    stages: list[WorkflowStage],
) -> PartitionRecommendation:
    stage_assignments: dict[str, str] = {}
    quantum_stage_ids: list[str] = []
    classical_stage_ids: list[str] = []
    rationale: list[str] = []
    fallback_required = False

    if assessment.admissibility == "reject":
        for stage in stages:
            stage_assignments[stage.stage_id] = "classical"
            classical_stage_ids.append(stage.stage_id)
        rationale.append("Quantum component rejected by assessment; keep the full workflow classical.")
        rationale.extend(assessment.rationale)
        return PartitionRecommendation(
            partition_id=f"{case.case_id}__{component.component_id}",
            stage_assignments=stage_assignments,
            quantum_stage_ids=quantum_stage_ids,
            classical_stage_ids=classical_stage_ids,
            fallback_required=False,
            rationale=rationale,
        )

    if assessment.admissibility == "exploratory":
        fallback_required = True
        for stage in stages:
            if _is_binary_commitment_stage(stage):
                stage_assignments[stage.stage_id] = "quantum_candidate"
                quantum_stage_ids.append(stage.stage_id)
            else:
                stage_assignments[stage.stage_id] = "classical"
                classical_stage_ids.append(stage.stage_id)
        rationale.append("Exploratory partition allows only the discrete commitment core to be quantum-enabled.")
        rationale.append("Dispatch, feasibility repair, rolling horizon control, and postprocessing remain classical.")
        rationale.append("This is a limited exploratory partition, not a deployment recommendation.")
        rationale.extend(assessment.rationale)
        return PartitionRecommendation(
            partition_id=f"{case.case_id}__{component.component_id}",
            stage_assignments=stage_assignments,
            quantum_stage_ids=quantum_stage_ids,
            classical_stage_ids=classical_stage_ids,
            fallback_required=fallback_required,
            rationale=rationale,
        )

    fallback_required = True
    for stage in stages:
        if _matches_target(stage, component) and not any(
            token in stage.stage_id for token in ["dispatch", "feasibility", "postprocessing", "rolling_horizon"]
        ):
            stage_assignments[stage.stage_id] = "quantum_candidate"
            quantum_stage_ids.append(stage.stage_id)
        else:
            stage_assignments[stage.stage_id] = "classical"
            classical_stage_ids.append(stage.stage_id)

    rationale.append("Pilot-admissible partition still keeps safety, feasibility, and postprocessing stages classical.")
    rationale.extend(assessment.rationale)
    return PartitionRecommendation(
        partition_id=f"{case.case_id}__{component.component_id}",
        stage_assignments=stage_assignments,
        quantum_stage_ids=quantum_stage_ids,
        classical_stage_ids=classical_stage_ids,
        fallback_required=fallback_required,
        rationale=rationale,
    )
