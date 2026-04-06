from itertools import product

import pandas as pd

from requirements import get_default_requirements
from design_variables import make_design_variables
from cruise import cruise_aero_from_cd0_e
from takeoff import estimate_takeoff_distance_m
from mass import close_mass_simple
from mission import fuel_fraction_breguet_prop
from feasibility import evaluate_design_against_requirements


def evaluate_candidate(requirements, dv) -> dict:
    fuel_guess = 0.12
    mass0 = close_mass_simple(
        payload_kg=requirements.payload_kg,
        empty_fraction_guess=dv.empty_fraction_guess,
        fuel_fraction=fuel_guess,
    )
    if not mass0["mass_closure_feasible"]:
        return {"mass_closure_feasible": False, "feasible": False}

    cruise0 = cruise_aero_from_cd0_e(
        weight_n=mass0["MTOW_N"],
        wing_loading_npm2=dv.wing_loading_npm2,
        aspect_ratio=dv.aspect_ratio,
        cd0_clean=dv.cd0_clean,
        oswald_efficiency=dv.oswald_efficiency,
        speed_mps=dv.cruise_speed_mps,
        altitude_m=dv.cruise_altitude_m,
    )

    fuel_info = fuel_fraction_breguet_prop(
        range_km=requirements.range_km_min,
        speed_mps=dv.cruise_speed_mps,
        propulsive_efficiency=dv.propulsive_efficiency,
        l_over_d=cruise0["L_over_D"],
        tsfc_per_s=dv.tsfc_per_s,
    )

    mass = close_mass_simple(
        payload_kg=requirements.payload_kg,
        empty_fraction_guess=dv.empty_fraction_guess,
        fuel_fraction=fuel_info["fuel_fraction"],
    )
    if not mass["mass_closure_feasible"]:
        return {"mass_closure_feasible": False, "feasible": False}

    cruise = cruise_aero_from_cd0_e(
        weight_n=mass["MTOW_N"],
        wing_loading_npm2=dv.wing_loading_npm2,
        aspect_ratio=dv.aspect_ratio,
        cd0_clean=dv.cd0_clean,
        oswald_efficiency=dv.oswald_efficiency,
        speed_mps=dv.cruise_speed_mps,
        altitude_m=dv.cruise_altitude_m,
    )

    takeoff = estimate_takeoff_distance_m(
        wing_loading_npm2=dv.wing_loading_npm2,
        thrust_to_weight=dv.takeoff_thrust_to_weight,
        cl_max_takeoff=dv.cl_max_takeoff,
        rho_kgpm3=1.225,
    )

    result = {
        "mass_closure_feasible": mass["mass_closure_feasible"],
        "payload_kg": requirements.payload_kg,
        "MTOW_kg": mass["MTOW_kg"],
        "MTOW_N": mass["MTOW_N"],
        "empty_mass_kg": mass["empty_mass_kg"],
        "fuel_mass_kg": mass["fuel_mass_kg"],
        "fuel_fraction": fuel_info["fuel_fraction"],
        "ln_WiWf": fuel_info["ln_WiWf"],
        "wing_loading_npm2": dv.wing_loading_npm2,
        "aspect_ratio": dv.aspect_ratio,
        "cl_max_takeoff": dv.cl_max_takeoff,
        "takeoff_thrust_to_weight": dv.takeoff_thrust_to_weight,
        "cruise_speed_mps": dv.cruise_speed_mps,
        "cruise_altitude_m": dv.cruise_altitude_m,
        "cd0_clean": dv.cd0_clean,
        "oswald_efficiency": dv.oswald_efficiency,
        "empty_fraction_guess": dv.empty_fraction_guess,
        "propulsive_efficiency": dv.propulsive_efficiency,
        "tsfc_per_s": dv.tsfc_per_s,
        "range_km_est": requirements.range_km_min,
        "rho_cruise": cruise["rho_cruise"],
        "q_cruise": cruise["q_cruise"],
        "S_m2": cruise["S_m2"],
        "b_m": cruise["b_m"],
        "cbar_m": cruise["cbar_m"],
        "CL_cruise": cruise["CL_cruise"],
        "CD_cruise": cruise["CD_cruise"],
        "k_induced": cruise["k_induced"],
        "L_over_D": cruise["L_over_D"],
        "Drag_N": cruise["Drag_N"],
        "Power_required_W": cruise["Power_required_W"],
        "CL_at_LDmax": cruise["CL_at_LDmax"],
        "V_at_LDmax_mps": cruise["V_at_LDmax_mps"],
        "v_stall_mps": takeoff["v_stall_mps"],
        "v_lof_mps": takeoff["v_lof_mps"],
        "takeoff_distance_m_est": takeoff["takeoff_distance_m_est"],
        "takeoff_a_over_g": takeoff["a_over_g"],
    }
    result.update(evaluate_design_against_requirements(requirements, result))
    return result


def run_sizing_sweep(
    requirements=None,
    wing_loading_values_npm2=None,
    aspect_ratio_values=None,
    cl_max_takeoff_values=None,
    takeoff_tw_values=None,
    cruise_speed_values_mps=None,
    cruise_altitude_m: float = 3000.0,
    cd0_clean: float = 0.030,
    oswald_efficiency: float = 0.80,
    empty_fraction_guess: float = 0.55,
    propulsive_efficiency: float = 0.80,
    tsfc_per_s: float = 1.3e-4,
) -> pd.DataFrame:
    if requirements is None:
        requirements = get_default_requirements()
    if wing_loading_values_npm2 is None:
        wing_loading_values_npm2 = [900, 1100, 1300, 1500, 1700, 1900, 2100]
    if aspect_ratio_values is None:
        aspect_ratio_values = [8.0, 9.0, 10.0, 11.0, 12.0]
    if cl_max_takeoff_values is None:
        cl_max_takeoff_values = [2.5, 3.0, 3.5, 4.0, 4.5]
    if takeoff_tw_values is None:
        takeoff_tw_values = [0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    if cruise_speed_values_mps is None:
        cruise_speed_values_mps = [60.0, 75.0, 90.0, 105.0, 125.0]

    rows = []
    for ws, ar, clmax_to, tw, vcr in product(
        wing_loading_values_npm2,
        aspect_ratio_values,
        cl_max_takeoff_values,
        takeoff_tw_values,
        cruise_speed_values_mps,
    ):
        dv = make_design_variables(
            wing_loading_npm2=ws,
            aspect_ratio=ar,
            cl_max_takeoff=clmax_to,
            takeoff_thrust_to_weight=tw,
            cruise_speed_mps=vcr,
            cruise_altitude_m=cruise_altitude_m,
            cd0_clean=cd0_clean,
            oswald_efficiency=oswald_efficiency,
            empty_fraction_guess=empty_fraction_guess,
            propulsive_efficiency=propulsive_efficiency,
            tsfc_per_s=tsfc_per_s,
        )
        rows.append(evaluate_candidate(requirements, dv))

    df = pd.DataFrame(rows)
    return df.sort_values(by=["feasible", "score"], ascending=[False, True]).reset_index(drop=True)
