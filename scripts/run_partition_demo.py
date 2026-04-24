from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hqcep.assessment import assess_component
from hqcep.partition import recommend_partition
from hqcep.report import write_json_report, write_markdown_report
from hqcep.schema import (
    quantum_component_from_dict,
    read_yaml,
    workflow_case_from_dict,
    workflow_stage_from_dict,
)


def main() -> None:
    workflow_payload = read_yaml(ROOT / "case_sheets/examples/pypsa_uc_workflow_example.yaml")
    component_payload = read_yaml(ROOT / "case_sheets/examples/planqk_quantum_component_example.yaml")

    case = workflow_case_from_dict(workflow_payload["case"])
    stages = [workflow_stage_from_dict(item) for item in workflow_payload["stages"]]
    component = quantum_component_from_dict(component_payload["components"][0])

    assessment = assess_component(case, component)
    partition = recommend_partition(case, component, assessment, stages)

    output_dir = ROOT / "outputs/demo"
    write_json_report(output_dir / "partition_report.json", case, component, assessment, partition)
    write_markdown_report(output_dir / "partition_report.md", case, component, assessment, partition)


if __name__ == "__main__":
    main()
