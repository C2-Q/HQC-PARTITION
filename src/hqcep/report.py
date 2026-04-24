from __future__ import annotations

import json
from pathlib import Path

from .schema import (
    AssessmentResult,
    EnergyWorkflowCase,
    PartitionRecommendation,
    QuantumComponentEvidence,
    as_dict,
)


def _report_payload(
    case: EnergyWorkflowCase,
    component: QuantumComponentEvidence,
    assessment: AssessmentResult,
    partition: PartitionRecommendation,
) -> dict:
    return {
        "case": as_dict(case),
        "component": as_dict(component),
        "assessment": as_dict(assessment),
        "partition": as_dict(partition),
        "warning": "This is assessment guidance, not solver performance.",
    }


def write_json_report(
    path: str | Path,
    case: EnergyWorkflowCase,
    component: QuantumComponentEvidence,
    assessment: AssessmentResult,
    partition: PartitionRecommendation,
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump(_report_payload(case, component, assessment, partition), handle, indent=2)
        handle.write("\n")


def write_markdown_report(
    path: str | Path,
    case: EnergyWorkflowCase,
    component: QuantumComponentEvidence,
    assessment: AssessmentResult,
    partition: PartitionRecommendation,
) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)

    blocking = assessment.blocking_conditions or ["None recorded."]
    lines = [
        "# Partition Report",
        "",
        f"- Case id: `{case.case_id}`",
        f"- Source URLs: `{case.source_url}`, `{component.source_url}`",
        f"- Component id: `{component.component_id}`",
        f"- Assessment result: `{assessment.admissibility}`",
        f"- Recommended partition: `{partition.partition_id}`",
        f"- Quantum stages: `{', '.join(partition.quantum_stage_ids) if partition.quantum_stage_ids else 'none'}`",
        f"- Classical stages: `{', '.join(partition.classical_stage_ids)}`",
        f"- Fallback required: `{partition.fallback_required}`",
        "",
        "## Blocking conditions",
        "",
    ]

    lines.extend([f"- {item}" for item in blocking])
    lines.extend(
        [
            "",
            "## Rationale",
            "",
        ]
    )
    lines.extend([f"- {item}" for item in partition.rationale])
    lines.extend(
        [
            "",
            "This is assessment guidance, not solver performance.",
            "",
        ]
    )

    with target.open("w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
