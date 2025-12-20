# -------- LENGTH (L1–L3) --------

def adjust_length_params(diagnosis, params):
    if diagnosis == "increase":
        params["tolerance"] *= 0.8
        params["target_range"] = shrink(params["target_range"])
        params["hints"] = max(params["hints"] - 1, 0)
        params["required_objects"] += 1

    elif diagnosis == "decrease":
        params["tolerance"] *= 1.2
        params["target_range"] = widen(params["target_range"])
        params["hints"] = min(params["hints"] + 1, 3)
        params["required_objects"] = max(1, params["required_objects"] - 1)

    return params


# -------- CAPACITY (C1–C3) --------

def adjust_capacity_params(diagnosis, params):
    if diagnosis == "increase":
        params["target_volume"] += 50
        params["pour_step"] = max(10, params["pour_step"] - 10)
        params["show_ghost_line"] = False
        params["ingredients"] = min(3, params["ingredients"] + 1)

    elif diagnosis == "decrease":
        params["target_volume"] = max(100, params["target_volume"] - 50)
        params["pour_step"] += 10
        params["show_ghost_line"] = True
        params["ingredients"] = max(1, params["ingredients"] - 1)

    return params


# -------- AREA (A1–A3) --------

def adjust_area_params(diagnosis, params):
    if diagnosis == "increase":
        params["tile_goal"] += 2
        params["grid_visible"] = False
        params["shape_complexity"] += 1
        params["outline"] = False

    elif diagnosis == "decrease":
        params["tile_goal"] = max(4, params["tile_goal"] - 2)
        params["grid_visible"] = True
        params["shape_complexity"] = max(1, params["shape_complexity"] - 1)
        params["outline"] = True

    return params


# -------- WEIGHT (W1–W3) --------

def adjust_weight_params(diagnosis, params):
    if diagnosis == "increase":
        params["target_weight"] += 100
        params["tolerance"] *= 0.8
        params["show_labels"] = False
        params["object_variety"] += 1

    elif diagnosis == "decrease":
        params["target_weight"] = max(200, params["target_weight"] - 100)
        params["tolerance"] *= 1.2
        params["show_labels"] = True
        params["object_variety"] = max(2, params["object_variety"] - 1)

    return params

def shrink(range_tuple, factor=0.8):
    """
    Shrinks a numeric range inward.
    Example: [8, 12] → [8.8, 11.2]
    """
    min_v, max_v = range_tuple
    center = (min_v + max_v) / 2
    half_width = (max_v - min_v) / 2 * factor
    return [round(center - half_width, 2), round(center + half_width, 2)]


def widen(range_tuple, factor=1.2):
    """
    Widens a numeric range outward.
    Example: [8, 12] → [7.6, 12.4]
    """
    min_v, max_v = range_tuple
    center = (min_v + max_v) / 2
    half_width = (max_v - min_v) / 2 * factor
    return [round(center - half_width, 2), round(center + half_width, 2)]



DOMAIN_ADAPTERS = {
    "length": adjust_length_params,
    "capacity": adjust_capacity_params,
    "area": adjust_area_params,
    "weight": adjust_weight_params
}
