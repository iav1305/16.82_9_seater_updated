import copy


def get_flight_condition(aircraft: dict, condition_name: str) -> dict:
    flight_conditions = aircraft.get("flight_conditions", {})
    if condition_name not in flight_conditions:
        raise KeyError(f"Flight condition '{condition_name}' not found. Available: {list(flight_conditions.keys())}")
    return flight_conditions[condition_name]


def apply_flight_condition(aircraft: dict, condition_name: str) -> dict:
    new_aircraft = copy.deepcopy(aircraft)
    cond = get_flight_condition(new_aircraft, condition_name)

    controls = new_aircraft["analysis_settings"]["control_defaults_deg"]
    jets = new_aircraft["analysis_settings"]["jet_defaults"]

    controls["Flap1"] = float(cond.get("flap_deg", 0.0))
    controls["Elevator"] = float(cond.get("elevator_deg", 0.0))

    for jet_name in jets:
        jets[jet_name] = 0.0
    for jet_name, jet_value in cond.get("fan_values", {}).items():
        if jet_name not in jets:
            raise KeyError(f"Unknown jet name '{jet_name}' in condition '{condition_name}'.")
        jets[jet_name] = float(jet_value)

    return new_aircraft
