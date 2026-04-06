import math

G = 9.81


def stall_speed_from_ws(wing_loading_npm2: float, rho_kgpm3: float, cl_max: float) -> float:
    ws = float(wing_loading_npm2)
    rho = float(rho_kgpm3)
    clm = max(float(cl_max), 1e-12)
    return math.sqrt((2.0 * ws) / (rho * clm))


def liftoff_speed_from_stall(v_stall_mps: float, safety_factor: float = 1.2) -> float:
    return float(safety_factor) * float(v_stall_mps)


def estimate_takeoff_distance_m(
    wing_loading_npm2: float,
    thrust_to_weight: float,
    cl_max_takeoff: float,
    rho_kgpm3: float = 1.225,
    rolling_mu: float = 0.03,
    safety_factor_vlof: float = 1.2,
    drag_fraction_of_weight_during_roll: float = 0.08,
) -> dict:
    v_stall = stall_speed_from_ws(wing_loading_npm2, rho_kgpm3, cl_max_takeoff)
    v_lof = liftoff_speed_from_stall(v_stall, safety_factor_vlof)

    tw = float(thrust_to_weight)
    mu = float(rolling_mu)
    d_over_w = float(drag_fraction_of_weight_during_roll)
    a_over_g = tw - mu - d_over_w

    if a_over_g <= 1e-6:
        return {
            "feasible_acceleration": False,
            "v_stall_mps": v_stall,
            "v_lof_mps": v_lof,
            "takeoff_distance_m_est": float("inf"),
            "a_over_g": a_over_g,
        }

    a_mps2 = a_over_g * G
    s_to_m = (v_lof ** 2) / (2.0 * a_mps2)

    return {
        "feasible_acceleration": True,
        "v_stall_mps": v_stall,
        "v_lof_mps": v_lof,
        "takeoff_distance_m_est": s_to_m,
        "a_over_g": a_over_g,
    }
