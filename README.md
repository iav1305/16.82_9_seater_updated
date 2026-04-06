# Simple Plane Design V2

A clean end-to-end repo for first-pass aircraft design.

## What it does

1. Sweeps candidate airplanes from top-level requirements.
2. Picks the best candidates from the simple sizing model.
3. Converts the best candidate into a JVL-ready geometry by scaling a baseline planform.
4. Runs JVL cruise and takeoff alpha sweeps.
5. Saves one combined summary for design review.

## Hard requirements

- Takeoff distance <= 150 ft
- Range >= 1500 miles
- Payload = 9 passengers + luggage = 900 kg
- MTOW < 19000 lb

## Soft goal

- Cruise near 125 m/s

## Repo structure

- `src/requirements.py` — top-level requirements
- `src/sizing.py` — first-pass sizing sweep
- `src/design_parameters.py` — baseline geometry definition for JVL
- `src/aircraft_builder.py` — scales baseline geometry to a sized candidate
- `src/jvl_builder.py` — writes a JVL file from the aircraft dictionary
- `src/run_jvl.py` — runs JVL
- `src/parse_jvl.py` — parses run results
- `src/validate.py` — validates top candidates in JVL
- `src/run_design.py` — one-command full pipeline

## Required setup

1. Install packages:

```bash
pip install -r requirements.txt
```

2. Edit `config.yaml` so `jvl_exe` points to your local JVL executable.

3. Run:

```bash
python src/run_design.py
```

## Outputs

Saved under `data/outputs/`:

- `sizing_results_all.csv`
- `sizing_results_feasible.csv`
- `top_candidates_geometry.csv`
- `jvl_validation_summary.csv`
- plots for the sizing sweep
- per-run JVL folders with `model.jvl`, `run_cases.txt`, `forces.txt`, etc.

## Important limitations

This repo is meant for first-pass design, not final certification-level truth.

It still uses:
- simple mass closure
- simple Breguet-style range estimate
- simple takeoff distance estimate
- approximate geometry scaling for the JVL candidate

The JVL side is meant to validate and refine the first-pass sizing model, not replace it.
