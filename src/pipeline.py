from pathlib import Path

import yaml

from jvl_builder import build_jvl
from run_jvl import run_jvl
from parse_jvl import parse_jvl_combined


def run_aircraft_case(repo_root: Path, aircraft: dict, runs_dir_override=None):
    repo_root = Path(repo_root)
    cfg = yaml.safe_load((repo_root / "config.yaml").read_text())

    jvl_exe = cfg["jvl_exe"]
    base_jvl = repo_root / cfg["base_jvl"]
    runs_dir = Path(runs_dir_override) if runs_dir_override is not None else repo_root / cfg["runs_dir"]

    built_model = repo_root / "data" / "temp" / "model.jvl"
    built_model.parent.mkdir(parents=True, exist_ok=True)
    build_jvl(base_file=base_jvl, output_file=built_model, aircraft=aircraft)

    run_dir = run_jvl(
        jvl_exe=jvl_exe,
        jvl_input=built_model,
        runs_dir=runs_dir,
        aircraft=aircraft,
        repo_root=repo_root,
    )

    (run_dir / "aircraft_used.yaml").write_text(yaml.safe_dump(aircraft, sort_keys=False))

    run_cases_file = run_dir / "run_cases.txt"
    forces_file = run_dir / "forces.txt"
    df = parse_jvl_combined(run_cases_file, forces_file)
    df.to_csv(run_dir / "combined_results.csv", index=False)
    return run_dir, df
