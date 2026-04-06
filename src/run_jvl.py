import datetime
import shutil
import subprocess
from pathlib import Path


def _ordered_control_names(aircraft: dict) -> list[str]:
    names = []
    for surface_key in ["wing", "vertical_tail", "horizontal_tail"]:
        for control in aircraft.get(surface_key, {}).get("controls", []):
            names.append(control["name"])
    return names


def _ordered_jet_names(aircraft: dict) -> list[str]:
    names = []
    for surface_key in ["wing", "vertical_tail", "horizontal_tail"]:
        for jet in aircraft.get(surface_key, {}).get("jets", []):
            names.append(jet["name"])
    return names


def _support_files(aircraft: dict) -> list[str]:
    files = set()
    for surface_key in ["wing", "horizontal_tail", "vertical_tail"]:
        for sec in aircraft.get(surface_key, {}).get("sections", []):
            af = str(sec.get("airfoil", "")).strip()
            if af.lower().endswith(".dat"):
                files.add(af)
    if aircraft.get("fuselage", {}).get("enabled", False):
        bfile = str(aircraft["fuselage"].get("bfile", "")).strip()
        if bfile.lower().endswith(".dat"):
            files.add(bfile)
    return sorted(files)


def _edit_variable(code: str, value) -> list[str]:
    return [code, f"{code} {value}"]


def _build_oper_commands(aircraft: dict) -> list[str]:
    a = aircraft.get("analysis_settings", {})
    cmds = ["OPER"]
    cmds += _edit_variable("A", a.get("alpha_deg", 0.0))
    cmds += _edit_variable("B", a.get("beta_deg", 0.0))
    cmds += _edit_variable("R", a.get("pb_2v", 0.0))
    cmds += _edit_variable("P", a.get("qc_2v", 0.0))
    cmds += _edit_variable("Y", a.get("rb_2v", 0.0))

    for i, name in enumerate(_ordered_control_names(aircraft), start=1):
        val = a.get("control_defaults_deg", {}).get(name, 0.0)
        cmds += _edit_variable(f"D{i}", val)

    for i, name in enumerate(_ordered_jet_names(aircraft), start=1):
        val = a.get("jet_defaults", {}).get(name, 0.0)
        cmds += _edit_variable(f"J{i}", val)

    cmds += ["X", "W", "forces.txt", "S", "run_cases.txt"]
    return cmds


def run_jvl(jvl_exe: str, jvl_input: Path, runs_dir: Path, aircraft: dict, repo_root: Path) -> Path:
    runs_dir = Path(runs_dir)
    runs_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    run_dir = runs_dir / f"run_{stamp}"
    run_dir.mkdir(parents=True, exist_ok=True)

    local_input = run_dir / "model.jvl"
    shutil.copy2(jvl_input, local_input)

    airfoil_dir = Path(repo_root) / "data" / "airfoils"
    for filename in _support_files(aircraft):
        src = airfoil_dir / filename
        if not src.exists():
            raise FileNotFoundError(f"Missing support file: {src}")
        shutil.copy2(src, run_dir / filename)

    commands = "\n".join(["LOAD", "model.jvl"] + _build_oper_commands(aircraft) + ["", "QUIT", ""])
    (run_dir / "jvl_commands_sent.txt").write_text(commands, encoding="utf-8")

    result = subprocess.run(
        [jvl_exe],
        cwd=str(run_dir),
        input=commands,
        text=True,
        capture_output=True,
    )

    (run_dir / "jvl_stdout.txt").write_text(result.stdout, encoding="utf-8", errors="ignore")
    (run_dir / "jvl_stderr.txt").write_text(result.stderr, encoding="utf-8", errors="ignore")

    if not (run_dir / "run_cases.txt").exists():
        raise RuntimeError(
            f"JVL did not produce run_cases.txt. Return code={result.returncode}. "
            f"See {run_dir / 'jvl_stdout.txt'}"
        )

    return run_dir
