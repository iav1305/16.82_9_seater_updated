from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from requirements import get_default_requirements
from sizing import run_sizing_sweep
from validate import validate_top_candidates


def print_requirements(req):
    print("TOP-LEVEL REQUIREMENTS")
    print(f"  takeoff_distance_m_max   = {req.takeoff_distance_m_max}")
    print(f"  range_km_min             = {req.range_km_min}")
    print(f"  payload_kg               = {req.payload_kg}")
    print(f"  mtow_kg_max              = {req.mtow_kg_max}")
    print(f"  desired_cruise_speed_mps = {req.desired_cruise_speed_mps}")


def save_sizing_results(df: pd.DataFrame, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    all_csv = out_dir / "sizing_results_all.csv"
    feasible_csv = out_dir / "sizing_results_feasible.csv"
    df.to_csv(all_csv, index=False)
    df[df["feasible"] == True].copy().to_csv(feasible_csv, index=False)
    return all_csv, feasible_csv


def make_sizing_plots(df: pd.DataFrame, out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    feasible_df = df[df["feasible"] == True].copy()

    plt.figure(figsize=(8, 5))
    plt.scatter(df["wing_loading_npm2"], df["MTOW_kg"])
    plt.xlabel("Wing Loading W/S (N/m^2)")
    plt.ylabel("MTOW (kg)")
    plt.title("MTOW vs Wing Loading")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_dir / "mtow_vs_ws.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.scatter(df["wing_loading_npm2"], df["takeoff_distance_m_est"])
    plt.axhline(45.72, linestyle="--")
    plt.xlabel("Wing Loading W/S (N/m^2)")
    plt.ylabel("Estimated Takeoff Distance (m)")
    plt.title("Takeoff Distance vs Wing Loading")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_dir / "takeoff_vs_ws.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.scatter(df["cruise_speed_mps"], df["L_over_D"])
    plt.xlabel("Cruise Speed (m/s)")
    plt.ylabel("L/D")
    plt.title("L/D vs Cruise Speed")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(out_dir / "ld_vs_cruise_speed.png", dpi=200)
    plt.close()

    if not feasible_df.empty:
        plt.figure(figsize=(8, 5))
        plt.scatter(feasible_df["S_m2"], feasible_df["b_m"])
        plt.xlabel("Wing Area S (m^2)")
        plt.ylabel("Span b (m)")
        plt.title("Feasible Designs: Span vs Wing Area")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(out_dir / "feasible_span_vs_area.png", dpi=200)
        plt.close()


def print_top_designs(df: pd.DataFrame, n: int = 15):
    cols = [
        "feasible", "score", "wing_loading_npm2", "aspect_ratio", "cl_max_takeoff",
        "takeoff_thrust_to_weight", "cruise_speed_mps", "MTOW_kg", "S_m2", "b_m",
        "cbar_m", "CL_cruise", "CD_cruise", "L_over_D", "takeoff_distance_m_est",
        "v_stall_mps", "V_at_LDmax_mps",
    ]
    cols = [c for c in cols if c in df.columns]
    print(df[cols].head(n).to_string(index=False))


def main():
    repo_root = Path(__file__).resolve().parents[1]
    out_dir = repo_root / "data" / "outputs"

    req = get_default_requirements()
    print_requirements(req)

    sizing_df = run_sizing_sweep(
        requirements=req,
        wing_loading_values_npm2=[900, 1100, 1300, 1500, 1700, 1900, 2100],
        aspect_ratio_values=[8.0, 9.0, 10.0, 11.0, 12.0],
        cl_max_takeoff_values=[2.5, 3.0, 3.5, 4.0, 4.5],
        takeoff_tw_values=[0.25, 0.30, 0.35, 0.40, 0.45, 0.50],
        cruise_speed_values_mps=[60.0, 75.0, 90.0, 105.0, 125.0],
        cruise_altitude_m=3000.0,
        cd0_clean=0.030,
        oswald_efficiency=0.80,
        empty_fraction_guess=0.55,
        propulsive_efficiency=0.80,
        tsfc_per_s=1.3e-4,
    )

    print("\nTOP CANDIDATES FROM SIZING")
    print_top_designs(sizing_df, n=20)

    all_csv, feasible_csv = save_sizing_results(sizing_df, out_dir)
    make_sizing_plots(sizing_df, out_dir)

    geometry_df, validation_df = validate_top_candidates(repo_root, sizing_df, top_n=3)
    geometry_csv = out_dir / "top_candidates_geometry.csv"
    validation_csv = out_dir / "jvl_validation_summary.csv"
    geometry_df.to_csv(geometry_csv, index=False)
    validation_df.to_csv(validation_csv, index=False)

    print(f"\nSaved all sizing results to: {all_csv}")
    print(f"Saved feasible sizing results to: {feasible_csv}")
    print(f"Saved top-candidate geometry summary to: {geometry_csv}")
    print(f"Saved JVL validation summary to: {validation_csv}")

    if validation_df.empty:
        print("\nNo JVL validation rows were created.")
    else:
        display_cols = [
            "name", "Sref_m2", "Bref_m", "Cref_m", "MTOW_kg", "cruise_speed_mps",
            "jvl_cruise_cl_required", "jvl_cruise_alpha_deg", "jvl_cruise_CL", "jvl_cruise_CD",
            "jvl_takeoff_cl_required", "jvl_takeoff_alpha_deg", "jvl_takeoff_CL", "jvl_takeoff_CD",
        ]
        display_cols = [c for c in display_cols if c in validation_df.columns]
        print("\nJVL VALIDATION SUMMARY")
        print(validation_df[display_cols].to_string(index=False))


if __name__ == "__main__":
    main()
