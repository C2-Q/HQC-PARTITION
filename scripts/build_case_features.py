from __future__ import annotations

import csv
import sys
import tempfile
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

from matplotlib import pyplot as plt
from matplotlib.colors import ListedColormap

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hqcep.pglib_uc_parser import download_pglib_case, extract_case_features, load_pglib_uc_json
from hqcep.schema import as_dict, write_yaml

SELECTED_PGLIB_CASES = [
    ("pglib_uc_ca_2014_09_01_reserves_0", "https://raw.githubusercontent.com/power-grid-lib/pglib-uc/master/ca/2014-09-01_reserves_0.json"),
    ("pglib_uc_ca_2014_09_01_reserves_1", "https://raw.githubusercontent.com/power-grid-lib/pglib-uc/master/ca/2014-09-01_reserves_1.json"),
    ("pglib_uc_ca_2014_09_01_reserves_3", "https://raw.githubusercontent.com/power-grid-lib/pglib-uc/master/ca/2014-09-01_reserves_3.json"),
    ("pglib_uc_ca_2014_09_01_reserves_5", "https://raw.githubusercontent.com/power-grid-lib/pglib-uc/master/ca/2014-09-01_reserves_5.json"),
    ("pglib_uc_ferc_2015_01_01_lw", "https://raw.githubusercontent.com/power-grid-lib/pglib-uc/master/ferc/2015-01-01_lw.json"),
    ("pglib_uc_ferc_2015_01_01_hw", "https://raw.githubusercontent.com/power-grid-lib/pglib-uc/master/ferc/2015-01-01_hw.json"),
]

CSV_COLUMNS = [
    "case_id",
    "source_url",
    "horizon_hours",
    "num_generators",
    "has_reserve_requirement",
    "has_ramp_constraints",
    "has_min_up_down_constraints",
    "has_startup_shutdown_costs",
    "has_renewables",
    "has_storage",
    "rolling_horizon",
    "notes_count",
]

FIGURE_FIELDS = [
    ("has_reserve_requirement", "reserve"),
    ("has_ramp_constraints", "ramp"),
    ("has_min_up_down_constraints", "min up/down"),
    ("has_startup_shutdown_costs", "startup/shutdown"),
    ("has_renewables", "renewables"),
    ("has_storage", "storage"),
]


def _bool_to_code(value: bool | None) -> int:
    if value is True:
        return 2
    if value is False:
        return 0
    return 1


def _write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def _write_note(path: Path) -> None:
    lines = [
        "# Case feature note",
        "",
        "- Cases were selected from public PGLib-UC JSON files.",
        "- Extraction is metadata-level, not solver performance.",
        "- Fields are used to support assessment and partition case-sheet construction.",
        "- These are benchmark cases, not live deployment logs.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_figure(path: Path, case_rows: list[dict[str, object]]) -> None:
    matrix = [
        [_bool_to_code(row[field]) for field, _label in FIGURE_FIELDS]
        for row in case_rows
    ]
    labels = [row["case_id"].replace("pglib_uc_", "") for row in case_rows]
    columns = [label for _field, label in FIGURE_FIELDS]

    fig, ax = plt.subplots(figsize=(10, 3.6))
    cmap = ListedColormap(["#f2f2f2", "#cfcfcf", "#4c78a8"])
    image = ax.imshow(matrix, cmap=cmap, vmin=0, vmax=2, aspect="auto")
    _ = image  # keep linter quiet if enabled later

    ax.set_xticks(range(len(columns)))
    ax.set_xticklabels(columns, rotation=20, ha="right")
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.set_title("Selected PGLib-UC case feature matrix")

    for row_index, row in enumerate(matrix):
        for col_index, value in enumerate(row):
            text = {0: "absent", 1: "unknown", 2: "present"}[value]
            ax.text(col_index, row_index, text, ha="center", va="center", fontsize=7, color="#111111")

    ax.set_xticks([x - 0.5 for x in range(1, len(columns))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(labels))], minor=True)
    ax.grid(which="minor", color="#ffffff", linestyle="-", linewidth=1.0)
    ax.tick_params(which="minor", bottom=False, left=False)

    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    generated_dir = ROOT / "case_sheets/generated"
    output_dir = ROOT / "outputs/case_features"
    generated_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []

    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)

        for case_id, url in SELECTED_PGLIB_CASES:
            temp_json = temp_dir / f"{case_id}.json"
            try:
                download_pglib_case(url, str(temp_json))
                data = load_pglib_uc_json(str(temp_json))
            except Exception as exc:
                raise SystemExit(f"Failed to build case features from {url}: {exc}") from exc

            case = extract_case_features(data, source_url=url, case_id=case_id)
            write_yaml(generated_dir / f"{case_id}.yaml", {"case": as_dict(case)})

            rows.append(
                {
                    "case_id": case.case_id,
                    "source_url": case.source_url,
                    "horizon_hours": case.horizon_hours,
                    "num_generators": case.num_generators,
                    "has_reserve_requirement": case.has_reserve_requirement,
                    "has_ramp_constraints": case.has_ramp_constraints,
                    "has_min_up_down_constraints": case.has_min_up_down_constraints,
                    "has_startup_shutdown_costs": case.has_startup_shutdown_costs,
                    "has_renewables": case.has_renewables,
                    "has_storage": case.has_storage,
                    "rolling_horizon": case.rolling_horizon,
                    "notes_count": len(case.notes),
                }
            )

    _write_csv(output_dir / "pglib_uc_case_features.csv", rows)
    _write_figure(output_dir / "fig_case_feature_matrix.png", rows)
    _write_note(output_dir / "case_feature_note.md")


if __name__ == "__main__":
    main()
