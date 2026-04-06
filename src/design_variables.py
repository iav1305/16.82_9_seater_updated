from dataclasses import dataclass


@dataclass(frozen=True)
class DesignVariables:
    wing_loading_npm2: float
    aspect_ratio: float
    cl_max_takeoff: float
    takeoff_thrust_to_weight: float
    cruise_speed_mps: float
    cruise_altitude_m: float
    cd0_clean: float
    oswald_efficiency: float
    empty_fraction_guess: float
    propulsive_efficiency: float
    tsfc_per_s: float


def make_design_variables(
    wing_loading_npm2: float,
    aspect_ratio: float,
    cl_max_takeoff: float,
    takeoff_thrust_to_weight: float,
    cruise_speed_mps: float,
    cruise_altitude_m: float,
    cd0_clean: float,
    oswald_efficiency: float,
    empty_fraction_guess: float,
    propulsive_efficiency: float,
    tsfc_per_s: float,
) -> DesignVariables:
    return DesignVariables(
        wing_loading_npm2=wing_loading_npm2,
        aspect_ratio=aspect_ratio,
        cl_max_takeoff=cl_max_takeoff,
        takeoff_thrust_to_weight=takeoff_thrust_to_weight,
        cruise_speed_mps=cruise_speed_mps,
        cruise_altitude_m=cruise_altitude_m,
        cd0_clean=cd0_clean,
        oswald_efficiency=oswald_efficiency,
        empty_fraction_guess=empty_fraction_guess,
        propulsive_efficiency=propulsive_efficiency,
        tsfc_per_s=tsfc_per_s,
    )
