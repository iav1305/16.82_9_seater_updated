import copy
import math

from design_parameters import get_baseline_aircraft


BASE_HALFSPAN = 8.55
BASE_MEAN_CHORD = (2.11 + 1.71 + 1.31) / 3.0


def build_aircraft_from_candidate(candidate_row) -> dict:
    """
    Scale the baseline aircraft to the sized candidate.

    This preserves the baseline wing shape pattern and keeps the tail and
    fuselage fixed for Version 2.
    """
    aircraft = copy.deepcopy(get_baseline_aircraft())

    sref_new = float(candidate_row["S_m2"])
    bref_new = float(candidate_row["b_m"])
    cref_new = sref_new / bref_new
    mtow_kg = float(candidate_row["MTOW_kg"])
    cruise_speed = float(candidate_row["cruise_speed_mps"])

    aircraft["name"] = (
        f"Sized candidate | WS={float(candidate_row['wing_loading_npm2']):.0f} | "
        f"AR={float(candidate_row['aspect_ratio']):.1f} | V={cruise_speed:.1f}"
    )

    aircraft["reference"]["sref"] = sref_new
    aircraft["reference"]["bref"] = bref_new
    aircraft["reference"]["cref"] = cref_new

    aircraft["mass_properties"]["mtow_kg"] = mtow_kg
    aircraft["mass_properties"]["empty_weight_kg"] = float(candidate_row.get("empty_mass_kg", float("nan")))
    aircraft["mass_properties"]["fuel_or_energy_mass_kg"] = float(candidate_row.get("fuel_mass_kg", float("nan")))

    aircraft["flight_conditions"]["cruise"]["weight_kg"] = 0.92 * mtow_kg
    aircraft["flight_conditions"]["cruise"]["speed_mps"] = cruise_speed
    aircraft["flight_conditions"]["takeoff"]["weight_kg"] = mtow_kg
    aircraft["flight_conditions"]["takeoff"]["speed_mps"] = float(candidate_row.get("v_lof_mps", 35.0))

    halfspan_new = 0.5 * bref_new
    span_scale = halfspan_new / BASE_HALFSPAN
    chord_scale = cref_new / BASE_MEAN_CHORD

    for sec in aircraft["wing"]["sections"]:
        sec["yle"] = float(sec["yle"]) * span_scale
        sec["chord"] = float(sec["chord"]) * chord_scale
        sec["xle"] = float(sec["xle"]) * chord_scale

    # Simple sweep-based Mach update using cruise speed and altitude density not needed here.
    aircraft["analysis_settings"]["mach"] = min(0.40, cruise_speed / 330.0)

    return aircraft


def summarize_aircraft_geometry(aircraft: dict) -> dict:
    wing_sections = aircraft["wing"]["sections"]
    return {
        "name": aircraft["name"],
        "Sref_m2": aircraft["reference"]["sref"],
        "Bref_m": aircraft["reference"]["bref"],
        "Cref_m": aircraft["reference"]["cref"],
        "MTOW_kg": aircraft["mass_properties"]["mtow_kg"],
        "cruise_speed_mps": aircraft["flight_conditions"]["cruise"]["speed_mps"],
        "wing_root_chord_m": wing_sections[0]["chord"],
        "wing_mid_y_m": wing_sections[1]["yle"],
        "wing_mid_chord_m": wing_sections[1]["chord"],
        "wing_tip_y_m": wing_sections[2]["yle"],
        "wing_tip_chord_m": wing_sections[2]["chord"],
    }
