import re
from pathlib import Path

import pandas as pd

RUN_CASE_RE = re.compile(r"Run case\s+(\d+):\s*(.*)")
ASSIGNMENT_RE = re.compile(r"^\s*(.*?)\s*->\s*(.*?)\s*=\s*([-\d.Ee+]+)\s*$")
RESULT_RE = re.compile(r"^\s*([^=]+?)\s*=\s*([-\d.Ee+]+)(?:\s+(.*))?$")


def _clean_name(name: str) -> str:
    name = name.strip()
    for old, new in [(".", ""), ("/", "_per_"), (" ", "_"), ("-", "_"), ("(", ""), (")", ""), ("'", "prime")]:
        name = name.replace(old, new)
    return name


def _add_common_aliases(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    lower_map = {c.lower(): c for c in df.columns}

    def first_existing(candidates):
        for c in candidates:
            if c.lower() in lower_map:
                return lower_map[c.lower()]
        return None

    alias_candidates = {
        "alpha": ["alpha", "Alpha", "assign_alpha"],
        "CL": ["CL", "cl", "CLtot", "cltot"],
        "CD": ["CD", "cd", "CDtot", "cdtot", "CDff", "cdff"],
        "CDi": ["CDi", "cdi", "CDind", "cdind"],
        "CDv": ["CDv", "cdv", "CDvis", "cdvis", "CDf", "cdf"],
        "Cm": ["Cm", "cm", "Cmtot", "cmtot", "CM"],
        "e_jvl": ["e", "e_jvl"],
    }

    for alias, candidates in alias_candidates.items():
        if alias not in df.columns:
            found = first_existing(candidates)
            if found is not None:
                df[alias] = df[found]

    if "CL" in df.columns and "CD" in df.columns and "CL_over_CD" not in df.columns:
        df["CL_over_CD"] = df["CL"] / df["CD"].replace(0, pd.NA)

    return df


def parse_jvl_run_cases(file_path: str | Path) -> pd.DataFrame:
    lines = Path(file_path).read_text(encoding="utf-8", errors="ignore").splitlines()
    cases = []
    current_case = None

    for raw_line in lines:
        line = raw_line.rstrip()
        m_case = RUN_CASE_RE.search(line)
        if m_case:
            if current_case is not None:
                cases.append(current_case)
            current_case = {"run_case": int(m_case.group(1)), "case_name": m_case.group(2).strip()}
            continue
        if current_case is None:
            continue

        m_assign = ASSIGNMENT_RE.match(line)
        if m_assign:
            lhs = _clean_name(m_assign.group(1))
            rhs = _clean_name(m_assign.group(2))
            current_case[f"assign_{lhs}"] = float(m_assign.group(3))
            current_case[f"maps_to_{lhs}"] = rhs
            continue

        m_result = RESULT_RE.match(line)
        if m_result:
            current_case[_clean_name(m_result.group(1))] = float(m_result.group(2))

    if current_case is not None:
        cases.append(current_case)

    return _add_common_aliases(pd.DataFrame(cases))


def parse_jvl_forces(file_path: str | Path) -> pd.DataFrame:
    lines = Path(file_path).read_text(encoding="utf-8", errors="ignore").splitlines()
    data = {}
    for raw_line in lines:
        pairs = re.findall(r"([A-Za-z0-9_'.]+)\s*=\s*([-\d.Ee+]+)", raw_line)
        for name, value in pairs:
            try:
                data[_clean_name(name)] = float(value)
            except ValueError:
                pass
    return _add_common_aliases(pd.DataFrame([data]))


def parse_jvl_combined(run_cases_file: str | Path, forces_file: str | Path | None = None) -> pd.DataFrame:
    run_cases_file = Path(run_cases_file)
    if forces_file is None:
        forces_file = run_cases_file.with_name("forces.txt")
    else:
        forces_file = Path(forces_file)

    df_run = parse_jvl_run_cases(run_cases_file)
    if not forces_file.exists():
        return df_run

    df_forces = parse_jvl_forces(forces_file)
    if df_run.empty:
        return df_forces
    if df_forces.empty:
        return df_run

    force_row = df_forces.iloc[0].to_dict()
    for col, value in force_row.items():
        if col not in df_run.columns:
            df_run[col] = value
    return _add_common_aliases(df_run)
