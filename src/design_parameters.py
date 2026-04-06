def get_baseline_aircraft() -> dict:
    """
    Baseline JVL geometry and control definition used as the scaling template.

    This version intentionally uses a simple three-section wing matching
    the included team9-base-fuse.jvl file.
    """
    return {
        "name": "Simple Plane Design V2 Baseline",
        "reference": {
            "sref": 29.3,
            "cref": 1.7,
            "bref": 17.1,
            "xref": 0.425,
            "yref": 0.0,
            "zref": 0.0,
            "cdp": 0.055,
        },
        "wing": {
            "name": "Main Wing",
            "paneling": {
                "nchordwise": 18,
                "cspace": 1.0,
                "nspanwise": 25,
                "sspace": -2.0,
                "nujet": 0.2,
                "cusp": 0.0,
                "nwjet": 30,
                "cwsp": -2.0,
            },
            "symmetry": {"ydup": 0.0},
            "jet_parameters": {
                "hdisk": 0.188,
                "fh": 0.0,
                "djet0": 0.0,
                "djet1": 0.0,
                "djet3": 0.0,
                "dxdisk": 0.10,
                "dndisk": -0.188,
            },
            "sections": [
                {"name": "Root", "xle": 0.0, "yle": 0.0, "zle": 0.0, "chord": 2.11, "ainc": 0.0, "nspanwise": 10, "sspace": -2.0, "airfoil": "bw02.dat"},
                {"name": "Mid",  "xle": 0.2, "yle": 4.275, "zle": 0.0, "chord": 1.71, "ainc": 0.0, "nspanwise": 10, "sspace": 1.0,  "airfoil": "bw02.dat"},
                {"name": "Tip",  "xle": 0.4, "yle": 8.55, "zle": 0.0, "chord": 1.31, "ainc": 0.0, "nspanwise": 10, "sspace": 1.0,  "airfoil": "bw02.dat"},
            ],
            "controls": [
                {"name": "Flap1", "gain": 1.0, "xhinge": 0.66, "hvec": [0.0, 0.0, 0.0], "signdup": 1.0},
                {"name": "Aileron", "gain": 1.0, "xhinge": 0.66, "hvec": [0.0, 0.0, 0.0], "signdup": -1.0},
            ],
            "jets": [
                {"name": "JetIn", "gain": 1.0, "signdup": 1.0},
                {"name": "JetInDiff", "gain": 1.0, "signdup": -1.0},
                {"name": "JetOut", "gain": 1.0, "signdup": 1.0},
                {"name": "JetOutDiff", "gain": 1.0, "signdup": -1.0},
            ],
        },
        "horizontal_tail": {
            "name": "Horizontal Tail",
            "paneling": {"nchordwise": 10, "cspace": 1.0, "nspanwise": 12, "sspace": 1.0},
            "symmetry": {"ydup": 0.0},
            "sections": [
                {"xle": 6.998, "yle": 0.0, "zle": 2.26, "chord": 1.69, "ainc": 0.0, "nspanwise": 10, "sspace": 1.0, "airfoil": "0012"},
                {"xle": 7.488, "yle": 3.385, "zle": 2.26, "chord": 1.2,  "ainc": 0.0, "nspanwise": 10, "sspace": 1.0, "airfoil": "0012"},
            ],
            "controls": [
                {"name": "Elevator", "gain": 1.0, "xhinge": 0.65, "hvec": [0.0, 0.0, 0.0], "signdup": 1.0},
            ],
        },
        "vertical_tail": {
            "name": "Vertical Tail",
            "paneling": {"nchordwise": 8, "cspace": 1.0, "nspanwise": 8, "sspace": 1.0},
            "sections": [
                {"xle": 5.868, "yle": 0.0, "zle": 0.0,  "chord": 2.12, "ainc": 0.0, "nspanwise": 10, "sspace": 1.0, "airfoil": "0012"},
                {"xle": 6.998, "yle": 0.0, "zle": 2.26, "chord": 1.69, "ainc": 0.0, "nspanwise": 10, "sspace": 1.0, "airfoil": "0012"},
            ],
            "controls": [
                {"name": "Rudder", "gain": 1.0, "xhinge": 0.66, "hvec": [0.0, 0.0, 0.0], "signdup": 1.0},
            ],
        },
        "fuselage": {
            "enabled": True,
            "name": "Fuselage",
            "nbody": 15,
            "bspace": 1.0,
            "translate": [-3.472, 0.0, -0.8022],
            "scale": [11.46, 11.46, 11.46],
            "bfile": "fuse2.dat",
        },
        "mass_properties": {
            "mtow_kg": 4200.0,
            "payload_kg": 900.0,
            "empty_weight_kg": None,
            "fuel_or_energy_mass_kg": None,
        },
        "analysis_settings": {
            "mach": 0.053,
            "alpha_deg": 0.0,
            "beta_deg": 0.0,
            "pb_2v": 0.0,
            "qc_2v": 0.0,
            "rb_2v": 0.0,
            "control_defaults_deg": {
                "Flap1": 0.0,
                "Aileron": 0.0,
                "Rudder": 0.0,
                "Elevator": 0.0,
            },
            "jet_defaults": {
                "JetIn": 0.0,
                "JetInDiff": 0.0,
                "JetOut": 0.0,
                "JetOutDiff": 0.0,
            },
        },
        "flight_conditions": {
            "cruise": {
                "rho_kgpm3": 0.905,
                "speed_mps": 90.0,
                "weight_kg": 5000.0,
                "flap_deg": 0.0,
                "elevator_deg": 0.0,
                "fan_values": {"JetIn": 0.0, "JetInDiff": 0.0, "JetOut": 0.0, "JetOutDiff": 0.0},
            },
            "takeoff": {
                "rho_kgpm3": 1.225,
                "speed_mps": 35.0,
                "weight_kg": 5000.0,
                "flap_deg": 20.0,
                "elevator_deg": 0.0,
                "fan_values": {"JetIn": 0.15, "JetInDiff": 0.0, "JetOut": 0.15, "JetOutDiff": 0.0},
            },
        },
    }
