from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schema import EnergyWorkflowCase


def load_pglib_uc_json(path: str) -> dict[str, Any]:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(f"PGLib-UC JSON file not found: {path}")
    with source.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"PGLib-UC JSON root must be an object, got {type(data).__name__}")
    return data


def _first_mapping(data: dict[str, Any], keys: list[str]) -> dict[str, Any] | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, dict):
            return value
    return None


def _first_sequence(data: dict[str, Any], keys: list[str]) -> list[Any] | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, list):
            return value
    return None


def _detect_horizon_hours(data: dict[str, Any], notes: list[str]) -> int | None:
    explicit_keys = ["time_periods", "horizon_hours", "num_periods", "T"]
    for key in explicit_keys:
        value = data.get(key)
        if isinstance(value, int):
            return value

    for sequence_key in ["demand", "load", "net_load", "reserves", "renewables", "wind_profile", "solar_profile"]:
        value = data.get(sequence_key)
        if isinstance(value, list):
            return len(value)
        if isinstance(value, dict):
            lengths = [len(series) for series in value.values() if isinstance(series, list)]
            if lengths:
                return max(lengths)

    notes.append("Could not infer horizon_hours from the provided PGLib-UC JSON.")
    return None


def _collect_generator_records(data: dict[str, Any], notes: list[str]) -> list[dict[str, Any]]:
    generator_map = _first_mapping(data, ["thermal_generators", "generators", "units", "generator"])
    if generator_map is not None:
        return [value for value in generator_map.values() if isinstance(value, dict)]

    generator_list = _first_sequence(data, ["thermal_generators", "generators", "units", "generator"])
    if generator_list is not None:
        return [value for value in generator_list if isinstance(value, dict)]

    notes.append("No generator collection found in the provided PGLib-UC JSON.")
    return []


def _find_bool_feature(records: list[dict[str, Any]], candidate_keys: list[str]) -> bool | None:
    found_key = False
    for record in records:
        for key in candidate_keys:
            if key not in record:
                continue
            found_key = True
            value = record.get(key)
            if value not in (None, 0, 0.0, False, ""):
                return True
    return False if found_key else None


def _detect_reserves(data: dict[str, Any], notes: list[str]) -> bool | None:
    reserve_keys = ["reserves", "reserve", "spinning_reserve", "reserve_requirement"]
    for key in reserve_keys:
        if key in data:
            return True

    system = data.get("system")
    if isinstance(system, dict) and any(key in system for key in reserve_keys):
        return True

    notes.append("Reserve requirement field not found; has_reserve_requirement set to None.")
    return None


def _detect_renewables(data: dict[str, Any], generator_records: list[dict[str, Any]], notes: list[str]) -> bool | None:
    renewable_keys = ["renewables", "renewable_series", "wind_profile", "solar_profile"]
    if any(key in data for key in renewable_keys):
        return True

    if generator_records:
        for record in generator_records:
            fuel = str(record.get("fuel", "")).lower()
            unit_type = str(record.get("unit_type", "")).lower()
            renewable_flag = record.get("is_renewable")
            if renewable_flag is True or fuel in {"wind", "solar", "hydro"} or unit_type in {"wind", "solar", "renewable"}:
                return True
        return False

    notes.append("Could not determine whether renewable series are present.")
    return None


def _detect_storage(data: dict[str, Any], notes: list[str]) -> bool | None:
    if any(key in data for key in ["storage", "batteries", "storage_units"]):
        return True
    notes.append("Storage field not found; has_storage set to None unless known absent.")
    return None


def extract_case_features(data: dict[str, Any], source_url: str, case_id: str) -> EnergyWorkflowCase:
    notes: list[str] = []
    generator_records = _collect_generator_records(data, notes)
    num_generators = len(generator_records) if generator_records else None
    if num_generators is None:
        notes.append("num_generators set to None because no generator list could be confirmed.")

    has_storage = _detect_storage(data, notes)

    return EnergyWorkflowCase(
        case_id=case_id,
        source_id="pglib_uc",
        source_url=source_url,
        workflow_type="unit_commitment_benchmark_case",
        scheduling_problem="unit_commitment",
        horizon_hours=_detect_horizon_hours(data, notes),
        num_generators=num_generators,
        has_reserve_requirement=_detect_reserves(data, notes),
        has_ramp_constraints=_find_bool_feature(
            generator_records,
            ["ramp_up_limit", "ramp_down_limit", "ramp_up", "ramp_down", "RU", "RD"],
        ),
        has_min_up_down_constraints=_find_bool_feature(
            generator_records,
            ["min_up_time", "min_down_time", "minimum_up_time", "minimum_down_time"],
        ),
        has_startup_shutdown_costs=_find_bool_feature(
            generator_records,
            ["startup_cost", "shutdown_cost", "start_up_cost", "shut_down_cost"],
        ),
        has_renewables=_detect_renewables(data, generator_records, notes),
        has_storage=has_storage if has_storage is not None else False,
        rolling_horizon=bool(data.get("rolling_horizon")) if "rolling_horizon" in data else None,
        notes=notes,
    )
