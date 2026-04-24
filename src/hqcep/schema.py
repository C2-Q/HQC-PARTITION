from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

import yaml

StageSide = Literal["classical", "quantum_candidate", "undecided"]
MethodType = Literal["qaoa", "quantum_annealing", "hybrid_benders", "other"]
EvidenceLevel = Literal["toy", "simulated", "hardware_demo", "deployment_relevant", "unknown"]
ComparatorStrength = Literal["none", "weak", "acceptable", "strong", "unknown"]
ProviderDependency = Literal["none", "simulator", "cloud_qpu", "specific_vendor", "unknown"]
EncodingOverhead = Literal["low", "medium", "high", "unknown"]
Admissibility = Literal["reject", "exploratory", "pilot_admissible"]


def _validate_literal(name: str, value: str, allowed: set[str]) -> None:
    if value not in allowed:
        raise ValueError(f"{name} must be one of {sorted(allowed)}, got {value!r}")


@dataclass
class EnergyWorkflowCase:
    case_id: str
    source_id: str
    source_url: str
    workflow_type: str
    scheduling_problem: str
    horizon_hours: int | None
    num_generators: int | None
    has_reserve_requirement: bool | None
    has_ramp_constraints: bool | None
    has_min_up_down_constraints: bool | None
    has_startup_shutdown_costs: bool | None
    has_renewables: bool | None
    has_storage: bool | None
    rolling_horizon: bool | None
    notes: list[str] = field(default_factory=list)


@dataclass
class WorkflowStage:
    stage_id: str
    description: str
    default_side: StageSide
    rationale: str

    def __post_init__(self) -> None:
        _validate_literal(
            "default_side",
            self.default_side,
            {"classical", "quantum_candidate", "undecided"},
        )


@dataclass
class QuantumComponentEvidence:
    component_id: str
    source_id: str
    source_url: str
    method_type: MethodType
    target_subproblem: str
    evidence_level: EvidenceLevel
    classical_comparator: ComparatorStrength
    provider_dependency: ProviderDependency
    encoding_overhead: EncodingOverhead
    scalability_note: str

    def __post_init__(self) -> None:
        _validate_literal("method_type", self.method_type, {"qaoa", "quantum_annealing", "hybrid_benders", "other"})
        _validate_literal("evidence_level", self.evidence_level, {"toy", "simulated", "hardware_demo", "deployment_relevant", "unknown"})
        _validate_literal("classical_comparator", self.classical_comparator, {"none", "weak", "acceptable", "strong", "unknown"})
        _validate_literal("provider_dependency", self.provider_dependency, {"none", "simulator", "cloud_qpu", "specific_vendor", "unknown"})
        _validate_literal("encoding_overhead", self.encoding_overhead, {"low", "medium", "high", "unknown"})


@dataclass
class AssessmentResult:
    admissibility: Admissibility
    blocking_conditions: list[str] = field(default_factory=list)
    positive_conditions: list[str] = field(default_factory=list)
    rationale: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        _validate_literal("admissibility", self.admissibility, {"reject", "exploratory", "pilot_admissible"})


@dataclass
class PartitionRecommendation:
    partition_id: str
    stage_assignments: dict[str, str]
    quantum_stage_ids: list[str] = field(default_factory=list)
    classical_stage_ids: list[str] = field(default_factory=list)
    fallback_required: bool = False
    rationale: list[str] = field(default_factory=list)


def as_dict(obj: Any) -> dict[str, Any]:
    return asdict(obj)


def read_yaml(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected mapping at {path}, got {type(data).__name__}")
    return data


def write_yaml(path: str | Path, data: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)


def workflow_case_from_dict(data: dict[str, Any]) -> EnergyWorkflowCase:
    payload = dict(data)
    payload.setdefault("notes", [])
    return EnergyWorkflowCase(**payload)


def workflow_stage_from_dict(data: dict[str, Any]) -> WorkflowStage:
    return WorkflowStage(**dict(data))


def quantum_component_from_dict(data: dict[str, Any]) -> QuantumComponentEvidence:
    return QuantumComponentEvidence(**dict(data))
