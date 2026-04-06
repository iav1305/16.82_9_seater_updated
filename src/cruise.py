import math

from atmosphere import dynamic_pressure_pa, isa_density_kgpm3
from geometry import wing_geometry_from_weight_and_ws


def induced_drag_factor_k(aspect_ratio: float, oswald_efficiency: float) -> float:
    ar = float(aspect_ratio)
    e = max(float(oswald_efficiency), 1e-6)
    return 1.0 / (math.pi * ar * e)


def cruise_aero_from_cd0_e(
    weight_n: float,
    wing_loading_npm2: float,
    aspect_ratio: float,
    cd0_clean: float,
    oswald_efficiency: float,
    speed_mps: float,
    altitude_m: float,
) -> dict:
    rho = isa_density_kgpm3(altitude_m)
    q = dynamic_pressure_pa(rho, speed_mps)
    geom = wing_geometry_from_weight_and_ws(weight_n, wing_loading_npm2, aspect_ratio)

    sref = geom["S_m2"]
    cl = weight_n / max(q * sref, 1e-12)
    k = induced_drag_factor_k(aspect_ratio, oswald_efficiency)
    cd = float(cd0_clean) + k * cl ** 2

    ld = cl / max(cd, 1e-12)
    drag_n = q * sref * cd
    power_required_w = drag_n * float(speed_mps)

    cl_ldmax = math.sqrt(float(cd0_clean) / max(k, 1e-12))
    v_ldmax = math.sqrt((2.0 * weight_n) / max(rho * sref * cl_ldmax, 1e-12))

    return {
        "rho_cruise": rho,
        "q_cruise": q,
        "S_m2": geom["S_m2"],
        "b_m": geom["b_m"],
        "cbar_m": geom["cbar_m"],
        "CL_cruise": cl,
        "CD_cruise": cd,
        "k_induced": k,
        "L_over_D": ld,
        "Drag_N": drag_n,
        "Power_required_W": power_required_w,
        "CL_at_LDmax": cl_ldmax,
        "V_at_LDmax_mps": v_ldmax,
    }
