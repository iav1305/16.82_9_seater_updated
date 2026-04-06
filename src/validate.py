import copy
from pathlib import Path

import pandas as pd

from aircraft_builder import build_aircraft_from_candidate, summarize_aircraft_geometry
from flight_conditions import apply_flight_condition
from pipeline import run_aircraft_case

G = 9.81


def required_cl(weight_kg: float, rho_kgpm3: float, speed_mps: float, sref: float) -> float:
    return weight_kg * G / max(0.5 * rho_kgpm3 * speed_mps ** 2 * sref, 1e-12)


def run_alpha_sweep(repo_root: Path, aircraft: dict, condition_name: str, alpha_values_deg: list[float]) -> pd.DataFrame:
    rows = []
    for alpha in alpha_values_deg:
        case_aircraft = apply_flight_condition(copy.deepcopy(aircraft), condition_name)
        case_aircraft["analysis_settings"]["alpha_deg"] = float(alpha)
        run_dir, df = run_aircraft_case(repo_root, case_aircraft)
        row = {"alpha_deg": float(alpha), "run_dir": str(run_dir)}
        if not df.empty:
            for col in ["CL", "CD", "CDi", "CDv", "Cm", "e_jvl", "CL_over_CD"]:
                if col in df.columns:
                    row[col] = float(df.iloc[0][col])
        rows.append(row)
    return pd.DataFrame(rows)


def pick_best_alpha_row(sweep_df: pd.DataFrame, cl_required: float) -> dict:
    if sweep_df.empty:
        return {}
    sweep_df = sweep_df.copy()
    sweep_df["cl_error_abs"] = (sweep_df["CL"] - cl_required).abs()
    best = sweep_df.sort_values(by=["cl_error_abs", "CD"]).iloc[0]
    return best.to_dict()


def validate_candidate_with_jvl(repo_root: Path, candidate_row: pd.Series) -> dict:
    aircraft = build_aircraft_from_candidate(candidate_row)
    geom = summarize_aircraft_geometry(aircraft)

    cruise_cond = aircraft["flight_conditions"]["cruise"]
    takeoff_cond = aircraft["flight_conditions"]["takeoff"]
    sref = aircraft["reference"]["sref"]

    cl_req_cruise = required_cl(cruise_cond["weight_kg"], cruise_cond["rho_kgpm3"], cruise_cond["speed_mps"], sref)
    cl_req_takeoff = required_cl(takeoff_cond["weight_kg"], takeoff_cond["rho_kgpm3"], takeoff_cond["speed_mps"], sref)

    cruise_sweep = run_alpha_sweep(repo_root, aircraft, "cruise", [-4, -2, 0, 2, 4, 6, 8, 10])
    takeoff_sweep = run_alpha_sweep(repo_root, aircraft, "takeoff", [0, 2, 4, 6, 8, 10, 12, 14, 16, 18])

    best_cruise = pick_best_alpha_row(cruise_sweep, cl_req_cruise)
    best_takeoff = pick_best_alpha_row(takeoff_sweep, cl_req_takeoff)

    out = candidate_row.to_dict()
    out.update(geom)
    out["jvl_cruise_cl_required"] = cl_req_cruise
    out["jvl_takeoff_cl_required"] = cl_req_takeoff
    for prefix, best in [("jvl_cruise", best_cruise), ("jvl_takeoff", best_takeoff)]:
        for key, value in best.items():
            out[f"{prefix}_{key}"] = value
    return out


def validate_top_candidates(repo_root: Path, sizing_df: pd.DataFrame, top_n: int = 3):
    feasible_df = sizing_df[sizing_df["feasible"] == True].copy()
    top_df = feasible_df.head(top_n) if not feasible_df.empty else sizing_df.head(top_n)

    geometry_rows = []
    validation_rows = []
    for _, row in top_df.iterrows():
        aircraft = build_aircraft_from_candidate(row)
        geometry_rows.append(summarize_aircraft_geometry(aircraft))
        validation_rows.append(validate_candidate_with_jvl(repo_root, row))

    return pd.DataFrame(geometry_rows), pd.DataFrame(validation_rows)
