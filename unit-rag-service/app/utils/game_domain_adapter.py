# -------- LENGTH VARIANTS (L-V1 → L-V4) --------

def adjust_length_params(diagnosis, params):
    """Adjust parameters based on current variant and performance diagnosis."""
    variant = params.get("current_variant", "L-V1")
    
    # Variant-specific adjustments
    if variant == "L-V1":
        return _adjust_v1_params(diagnosis, params)
    elif variant == "L-V2":
        return _adjust_v2_params(diagnosis, params)
    elif variant == "L-V3":
        return _adjust_v3_params(diagnosis, params)
    elif variant == "L-V4":
        return _adjust_v4_params(diagnosis, params)
    else:
        return params  # fallback


def _adjust_v1_params(diagnosis, params):
    """V1 (Ruler Explorer): Adjust object size range and choice complexity."""
    if diagnosis == "increase":
        # Harder: smaller objects, tighter range, fewer hints
        params["object_size_range"] = shrink(params.get("object_size_range", [5, 15]))
        params["choice_spread"] = max(1, params.get("choice_spread", 3) - 1)
        params["hints"] = max(0, params.get("hints", 2) - 1)
    elif diagnosis == "decrease":
        # Easier: larger objects, wider range, more hints
        params["object_size_range"] = widen(params.get("object_size_range", [5, 15]))
        params["choice_spread"] = min(5, params.get("choice_spread", 3) + 1)
        params["hints"] = min(3, params.get("hints", 2) + 1)
    
    return params


def _adjust_v2_params(diagnosis, params):
    """V2 (Compare): Adjust size difference between objects."""
    if diagnosis == "increase":
        # Harder: objects closer in size
        params["min_size_difference"] = max(1, params.get("min_size_difference", 3) - 1)
        params["object_size_range"] = shrink(params.get("object_size_range", [5, 20]))
        params["hints"] = max(0, params.get("hints", 2) - 1)
    elif diagnosis == "decrease":
        # Easier: objects more different in size
        params["min_size_difference"] = min(6, params.get("min_size_difference", 3) + 1)
        params["object_size_range"] = widen(params.get("object_size_range", [5, 20]))
        params["hints"] = min(3, params.get("hints", 2) + 1)
    
    return params


def _adjust_v3_params(diagnosis, params):
    """V3 (Calculate & Win): Adjust conversion difficulty and value ranges."""
    if diagnosis == "increase":
        # Harder: more complex conversions, decimal values
        params["allow_decimals"] = True
        params["value_range_mm"] = [50, 250]  # harder mm values
        params["value_range_m"] = [0.15, 0.45]  # harder m values (more decimal places)
        params["choice_spread"] = max(1, params.get("choice_spread", 3) - 1)
        params["hints"] = max(0, params.get("hints", 2) - 1)
    elif diagnosis == "decrease":
        # Easier: simpler whole numbers
        params["allow_decimals"] = False
        params["value_range_mm"] = [30, 150]  # easier mm values (multiples of 10)
        params["value_range_m"] = [0.05, 0.25]  # easier m values
        params["choice_spread"] = min(5, params.get("choice_spread", 3) + 1)
        params["hints"] = min(3, params.get("hints", 2) + 1)
    
    return params


def _adjust_v4_params(diagnosis, params):
    """V4 (Bridge): Adjust bridge complexity and plank variety."""
    if diagnosis == "increase":
        # Harder: longer bridges, more/smaller planks, more combinations
        params["bridge_target_range"] = [15, 25]
        params["plank_sizes"] = [2, 3, 4, 5, 6, 7, 8]  # more variety, smaller sizes
        params["plank_count"] = min(10, params.get("plank_count", 7) + 1)
        params["hints"] = max(0, params.get("hints", 2) - 1)
    elif diagnosis == "decrease":
        # Easier: shorter bridges, fewer/larger planks, obvious combos
        params["bridge_target_range"] = [8, 14]
        params["plank_sizes"] = [3, 5, 7, 9]  # fewer variety, larger sizes
        params["plank_count"] = max(5, params.get("plank_count", 7) - 1)
        params["hints"] = min(3, params.get("hints", 2) + 1)
    
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
