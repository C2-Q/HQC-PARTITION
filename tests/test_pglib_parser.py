from hqcep.pglib_uc_parser import extract_case_features


def test_extract_case_features_handles_fake_pglib_like_dict() -> None:
    data = {
        "time_periods": 24,
        "demand": [1.0] * 24,
        "reserves": [0.1] * 24,
        "thermal_generators": {
            "G1": {
                "ramp_up_limit": 5.0,
                "ramp_down_limit": 5.0,
                "time_up_minimum": 2,
                "time_down_minimum": 2,
                "startup": [{"lag": 2, "cost": 10.0}],
            }
        },
        "renewable_generators": {},
    }

    case = extract_case_features(data, source_url="https://example.invalid/case.json", case_id="fake_case")

    assert case.horizon_hours == 24
    assert case.num_generators == 1
    assert case.has_reserve_requirement is True
    assert case.has_ramp_constraints is True
    assert case.has_min_up_down_constraints is True
    assert case.has_startup_shutdown_costs is True
    assert case.has_renewables is False


def test_missing_fields_produce_none_and_notes() -> None:
    case = extract_case_features({}, source_url="https://example.invalid/missing.json", case_id="missing_case")

    assert case.horizon_hours is None
    assert case.num_generators is None
    assert case.has_reserve_requirement is None
    assert case.has_ramp_constraints is None
    assert case.has_min_up_down_constraints is None
    assert case.has_startup_shutdown_costs is None
    assert case.has_renewables is None
    assert case.has_storage is None
    assert len(case.notes) > 0
