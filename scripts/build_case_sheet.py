from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hqcep.pglib_uc_parser import extract_case_features, load_pglib_uc_json
from hqcep.schema import as_dict, write_yaml


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a minimal case sheet from a local PGLib-UC JSON file.")
    parser.add_argument("input_json", help="Path to a local PGLib-UC JSON file.")
    parser.add_argument("output_yaml", help="Path to the case-sheet YAML to write.")
    parser.add_argument("--case-id", default="pglib_uc_case", help="Case identifier to store in the YAML.")
    parser.add_argument(
        "--source-url",
        default="https://github.com/power-grid-lib/pglib-uc",
        help="Source URL to record in the case sheet.",
    )
    args = parser.parse_args()

    data = load_pglib_uc_json(args.input_json)
    case = extract_case_features(data, source_url=args.source_url, case_id=args.case_id)
    write_yaml(args.output_yaml, {"case": as_dict(case)})


if __name__ == "__main__":
    main()
