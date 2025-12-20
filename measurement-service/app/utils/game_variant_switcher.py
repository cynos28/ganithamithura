VARIANTS = {
    "length": ["L-V1", "L-V2", "L-V3", "L-V4"],
    "area": ["A-V1", "A-V2", "A-V3", "A-V4"],
    "capacity": ["C-V1", "C-V2", "C-V3", "C-V4"],
    "weight": ["W-V1", "W-V2", "W-V3", "W-V4"]
}

def switch_variant(domain, current_variant, diagnosis):
    variants = VARIANTS[domain]
    index = variants.index(current_variant)

    if diagnosis == "increase" and index < len(variants) - 1:
        return variants[index + 1]

    if diagnosis == "decrease" and index > 0:
        return variants[index - 1]

    return current_variant
