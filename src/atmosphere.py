R_AIR = 287.05287


def isa_temperature_k(altitude_m: float) -> float:
    t0 = 288.15
    lapse = 0.0065
    return t0 - lapse * float(altitude_m)


def isa_pressure_pa(altitude_m: float) -> float:
    t0 = 288.15
    p0 = 101325.0
    lapse = 0.0065
    g0 = 9.80665
    t = isa_temperature_k(altitude_m)
    return p0 * (t / t0) ** (g0 / (R_AIR * lapse))


def isa_density_kgpm3(altitude_m: float) -> float:
    t = isa_temperature_k(altitude_m)
    p = isa_pressure_pa(altitude_m)
    return p / (R_AIR * t)


def dynamic_pressure_pa(rho_kgpm3: float, speed_mps: float) -> float:
    return 0.5 * float(rho_kgpm3) * float(speed_mps) ** 2
