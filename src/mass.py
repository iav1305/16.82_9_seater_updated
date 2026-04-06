G = 9.81


def close_mass_simple(payload_kg: float, empty_fraction_guess: float, fuel_fraction: float) -> dict:
    f_empty = float(empty_fraction_guess)
    f_fuel = float(fuel_fraction)

    if f_empty + f_fuel >= 0.98:
        return {
            "mass_closure_feasible": False,
            "MTOW_kg": float("nan"),
            "MTOW_N": float("nan"),
            "empty_mass_kg": float("nan"),
            "fuel_mass_kg": float("nan"),
            "payload_mass_kg": float(payload_kg),
        }

    mtow_kg = float(payload_kg) / (1.0 - f_empty - f_fuel)
    empty_mass_kg = f_empty * mtow_kg
    fuel_mass_kg = f_fuel * mtow_kg

    return {
        "mass_closure_feasible": True,
        "MTOW_kg": mtow_kg,
        "MTOW_N": mtow_kg * G,
        "empty_mass_kg": empty_mass_kg,
        "fuel_mass_kg": fuel_mass_kg,
        "payload_mass_kg": float(payload_kg),
    }
