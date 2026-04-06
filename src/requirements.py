from dataclasses import dataclass


@dataclass(frozen=True)
class AircraftRequirements:
    takeoff_distance_m_max: float = 45.72
    range_km_min: float = 2414.0
    payload_kg: float = 900.0
    mtow_kg_max: float = 8618.0
    desired_cruise_speed_mps: float = 125.0


def get_default_requirements() -> AircraftRequirements:
    return AircraftRequirements()
