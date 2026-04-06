import math


def wing_area_from_weight_and_wing_loading(weight_n: float, wing_loading_npm2: float) -> float:
    return float(weight_n) / float(wing_loading_npm2)


def span_from_area_and_aspect_ratio(area_m2: float, aspect_ratio: float) -> float:
    return math.sqrt(float(aspect_ratio) * float(area_m2))


def mean_chord_from_area_and_span(area_m2: float, span_m: float) -> float:
    return float(area_m2) / float(span_m)


def wing_geometry_from_weight_and_ws(weight_n: float, wing_loading_npm2: float, aspect_ratio: float) -> dict:
    s = wing_area_from_weight_and_wing_loading(weight_n, wing_loading_npm2)
    b = span_from_area_and_aspect_ratio(s, aspect_ratio)
    cbar = mean_chord_from_area_and_span(s, b)
    return {"S_m2": s, "b_m": b, "cbar_m": cbar}
