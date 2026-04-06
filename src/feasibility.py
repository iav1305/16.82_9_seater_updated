def evaluate_design_against_requirements(requirements, design_result: dict) -> dict:
    takeoff_ok = design_result["takeoff_distance_m_est"] <= requirements.takeoff_distance_m_max
    range_ok = design_result["range_km_est"] >= requirements.range_km_min
    mtow_ok = design_result["MTOW_kg"] <= requirements.mtow_kg_max

    cruise_speed_error = abs(design_result["cruise_speed_mps"] - requirements.desired_cruise_speed_mps)

    feasible = (
        design_result.get("mass_closure_feasible", False)
        and takeoff_ok
        and range_ok
        and mtow_ok
    )

    score = (
        3.0 * max(0.0, design_result["takeoff_distance_m_est"] - requirements.takeoff_distance_m_max)
        + 0.01 * max(0.0, requirements.range_km_min - design_result["range_km_est"])
        + 0.02 * max(0.0, design_result["MTOW_kg"] - requirements.mtow_kg_max)
        + 0.10 * cruise_speed_error
    )

    return {
        "takeoff_ok": takeoff_ok,
        "range_ok": range_ok,
        "mtow_ok": mtow_ok,
        "feasible": feasible,
        "score": score,
    }
