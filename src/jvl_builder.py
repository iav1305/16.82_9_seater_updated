from pathlib import Path


def _fmt(value):
    if isinstance(value, int):
        return str(value)
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _replace_line_after_header(lines, header_text, values):
    for i, line in enumerate(lines):
        if header_text in line:
            lines[i + 1] = "    ".join(_fmt(v) for v in values)
            return
    raise ValueError(f"Could not find header '{header_text}' in base JVL file.")


def _find_surface_block(lines, surface_name):
    start = None
    end = len(lines)
    for i in range(len(lines) - 1):
        if lines[i].strip() == "SURFACE" and lines[i + 1].strip() == surface_name:
            start = i
            break
    if start is None:
        raise ValueError(f"Could not find SURFACE block '{surface_name}'.")
    for j in range(start + 1, len(lines)):
        if j > start and lines[j].strip() in {"SURFACE", "BODY"}:
            end = j
            break
    return start, end


def _section_starts(lines, start, end):
    return [i for i in range(start, end) if lines[i].strip().startswith("SECTION")]


def _replace_surface_paneling(lines, surface_name, paneling):
    start, end = _find_surface_block(lines, surface_name)
    for i in range(start, end):
        if "#Nchord" in lines[i]:
            old = lines[i + 1].split()
            while len(old) < 8:
                old.append("0")
            mapping = [
                paneling.get("nchordwise"),
                paneling.get("cspace"),
                paneling.get("nspanwise"),
                paneling.get("sspace"),
                paneling.get("nujet"),
                paneling.get("cusp"),
                paneling.get("nwjet"),
                paneling.get("cwsp"),
            ]
            for idx, val in enumerate(mapping):
                if val is not None:
                    old[idx] = _fmt(val)
            lines[i + 1] = "    ".join(old)
            return


def _replace_yduplicate(lines, surface_name, ydup):
    if ydup is None:
        return
    start, end = _find_surface_block(lines, surface_name)
    for i in range(start, end):
        if lines[i].strip() == "YDUPLICATE":
            lines[i + 1] = _fmt(ydup)
            return


def _replace_jetparam(lines, surface_name, jet_params):
    if not jet_params:
        return
    start, end = _find_surface_block(lines, surface_name)
    for i in range(start, end):
        if lines[i].strip() == "JETPARAM":
            lines[i + 2] = "    ".join(
                _fmt(jet_params.get(k, 0.0))
                for k in ["hdisk", "fh", "djet0", "djet1", "djet3", "dxdisk", "dndisk"]
            )
            return


def _replace_sections(lines, surface_name, section_defs):
    start, end = _find_surface_block(lines, surface_name)
    starts = _section_starts(lines, start, end)
    if len(starts) != len(section_defs):
        raise ValueError(
            f"Surface '{surface_name}' has {len(starts)} sections in the base file but "
            f"{len(section_defs)} section definitions in Python."
        )

    for sec_idx, sec_start in enumerate(starts):
        geom_idx = sec_start + 2
        sec = section_defs[sec_idx]
        lines[geom_idx] = " ".join([
            _fmt(sec["xle"]), _fmt(sec["yle"]), _fmt(sec["zle"]),
            _fmt(sec["chord"]), _fmt(sec.get("ainc", 0.0)),
            _fmt(sec.get("nspanwise", 10)), _fmt(sec.get("sspace", 1.0)),
        ])

        for j in range(geom_idx + 1, min(geom_idx + 8, end)):
            if lines[j].strip() in {"AFIL", "NACA"}:
                lines[j + 1] = str(sec.get("airfoil", "0012"))
                break


def _replace_body(lines, fuselage):
    if not fuselage.get("enabled", False):
        return
    for i, line in enumerate(lines):
        if line.strip() == "BODY":
            for j in range(i, len(lines)):
                if lines[j].strip() == "TRANSLATE":
                    lines[j + 2] = " ".join(_fmt(v) for v in fuselage.get("translate", [0.0, 0.0, 0.0]))
                if lines[j].strip() == "SCALE":
                    lines[j + 2] = "      ".join(_fmt(v) for v in fuselage.get("scale", [1.0, 1.0, 1.0]))
                if lines[j].strip() == "BFILE":
                    lines[j + 1] = str(fuselage.get("bfile", "fuse2.dat"))
                    return


def build_jvl(base_file: str | Path, output_file: str | Path, aircraft: dict):
    base_file = Path(base_file)
    output_file = Path(output_file)
    lines = base_file.read_text(encoding="utf-8", errors="ignore").splitlines()

    lines[0] = aircraft.get("name", lines[0])

    ref = aircraft["reference"]
    analysis = aircraft["analysis_settings"]
    _replace_line_after_header(lines, "#Mach", [analysis.get("mach", 0.0)])
    _replace_line_after_header(lines, "#Sref", [ref["sref"], ref["cref"], ref["bref"]])
    _replace_line_after_header(lines, "#Xref", [ref["xref"], ref["yref"], ref["zref"]])
    _replace_line_after_header(lines, "# CDp", [ref.get("cdp", 0.0)])

    wing = aircraft["wing"]
    _replace_surface_paneling(lines, "Main Wing", wing.get("paneling", {}))
    _replace_yduplicate(lines, "Main Wing", wing.get("symmetry", {}).get("ydup"))
    _replace_jetparam(lines, "Main Wing", wing.get("jet_parameters", {}))
    _replace_sections(lines, "Main Wing", wing["sections"])

    htail = aircraft["horizontal_tail"]
    _replace_surface_paneling(lines, "Horizontal Tail", htail.get("paneling", {}))
    _replace_yduplicate(lines, "Horizontal Tail", htail.get("symmetry", {}).get("ydup"))
    _replace_sections(lines, "Horizontal Tail", htail["sections"])

    vtail = aircraft["vertical_tail"]
    _replace_surface_paneling(lines, "Vertical Tail", vtail.get("paneling", {}))
    _replace_sections(lines, "Vertical Tail", vtail["sections"])

    _replace_body(lines, aircraft.get("fuselage", {}))

    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
