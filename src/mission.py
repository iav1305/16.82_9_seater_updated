import math


def fuel_fraction_breguet_prop(
    range_km: float,
    speed_mps: float,
    propulsive_efficiency: float,
    l_over_d: float,
    tsfc_per_s: float,
) -> dict:
    range_m = float(range_km) * 1000.0
    time_s = range_m / max(float(speed_mps), 1e-12)
    ln_wi_wf = time_s * float(tsfc_per_s) / max(float(propulsive_efficiency) * float(l_over_d), 1e-12)
    fuel_fraction = 1.0 - math.exp(-ln_wi_wf)
    return {"ln_WiWf": ln_wi_wf, "fuel_fraction": fuel_fraction}
