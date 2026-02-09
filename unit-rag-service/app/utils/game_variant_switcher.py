"""
Game Variant Switcher
=====================
Manages progressive difficulty variants for AR measurement games.
Each domain has 4 variants (V1-V4) with increasing complexity.
"""

from typing import Dict, List, Optional
from enum import Enum


class Diagnosis(str, Enum):
    """Possible diagnostic outcomes from game evaluation"""
    INCREASE = "increase"
    DECREASE = "decrease"
    MAINTAIN = "maintain"


# ========== VARIANT DEFINITIONS ==========

VARIANTS = {
    "length": ["L-V1", "L-V2", "L-V3", "L-V4"],
    "area": ["A-V1", "A-V2", "A-V3", "A-V4"],
    "capacity": ["C-V1", "C-V2", "C-V3", "C-V4"],
    "weight": ["W-V1", "W-V2", "W-V3", "W-V4"]
}


VARIANT_METADATA = {
    # LENGTH VARIANTS
    "L-V1": {
        "difficulty": 1,
        "description": "Basic length measurement with ruler and simple objects",
        "typical_time": 45,
        "skills": ["ruler_reading", "single_object_measure"]
    },
    "L-V2": {
        "difficulty": 2,
        "description": "Multiple objects with tighter tolerances",
        "typical_time": 60,
        "skills": ["ruler_reading", "multi_object_measure", "precision"]
    },
    "L-V3": {
        "difficulty": 3,
        "description": "Complex measurements with reduced hints",
        "typical_time": 75,
        "skills": ["ruler_reading", "estimation", "self_correction"]
    },
    "L-V4": {
        "difficulty": 4,
        "description": "Advanced: minimal hints, strict tolerances, multiple objects",
        "typical_time": 90,
        "skills": ["mastery", "independent_problem_solving"]
    },
    
    # AREA VARIANTS
    "A-V1": {
        "difficulty": 1,
        "description": "Simple shapes with visible grid",
        "typical_time": 50,
        "skills": ["grid_counting", "basic_shapes"]
    },
    "A-V2": {
        "difficulty": 2,
        "description": "More complex shapes, grid still visible",
        "typical_time": 65,
        "skills": ["grid_counting", "composite_shapes"]
    },
    "A-V3": {
        "difficulty": 3,
        "description": "Complex shapes without visible grid",
        "typical_time": 80,
        "skills": ["mental_calculation", "shape_decomposition"]
    },
    "A-V4": {
        "difficulty": 4,
        "description": "Advanced: irregular shapes, no scaffolding",
        "typical_time": 95,
        "skills": ["mastery", "abstract_reasoning"]
    },
    
    # CAPACITY VARIANTS
    "C-V1": {
        "difficulty": 1,
        "description": "Single liquid with ghost line guidance",
        "typical_time": 40,
        "skills": ["volume_reading", "basic_pouring"]
    },
    "C-V2": {
        "difficulty": 2,
        "description": "Multiple ingredients with medium steps",
        "typical_time": 55,
        "skills": ["volume_reading", "multi_step_pouring"]
    },
    "C-V3": {
        "difficulty": 3,
        "description": "Finer pour control, no ghost line",
        "typical_time": 70,
        "skills": ["precise_measurement", "estimation"]
    },
    "C-V4": {
        "difficulty": 4,
        "description": "Advanced: multiple ingredients, fine control",
        "typical_time": 85,
        "skills": ["mastery", "complex_mixing"]
    },
    
    # WEIGHT VARIANTS
    "W-V1": {
        "difficulty": 1,
        "description": "Few objects with visible labels",
        "typical_time": 45,
        "skills": ["balance_reading", "simple_comparison"]
    },
    "W-V2": {
        "difficulty": 2,
        "description": "More objects, tighter tolerance",
        "typical_time": 60,
        "skills": ["balance_reading", "weight_estimation"]
    },
    "W-V3": {
        "difficulty": 3,
        "description": "Many objects without labels",
        "typical_time": 75,
        "skills": ["weight_reasoning", "trial_error"]
    },
    "W-V4": {
        "difficulty": 4,
        "description": "Advanced: multiple objects, minimal scaffolding",
        "typical_time": 90,
        "skills": ["mastery", "complex_balancing"]
    }
}


# ========== CORE FUNCTIONS ==========

def switch_variant(
    domain: str, 
    current_variant: str, 
    diagnosis: str
) -> str:
    """
    Switch to next/previous variant based on diagnostic outcome.
    
    Args:
        domain: Measurement domain (length, area, capacity, weight)
        current_variant: Current variant code (e.g., "L-V2")
        diagnosis: Diagnostic outcome (increase, decrease, maintain)
    
    Returns:
        New variant code
    
    Raises:
        ValueError: If domain is invalid
        ValueError: If current variant is not found
    """
    # Validate domain
    if domain not in VARIANTS:
        raise ValueError(
            f"Invalid domain '{domain}'. "
            f"Valid domains: {list(VARIANTS.keys())}"
        )
    
    variants = VARIANTS[domain]
    
    # Validate current variant
    if current_variant not in variants:
        # Auto-correct to V1 if invalid
        print(f"⚠️ Invalid variant '{current_variant}' for {domain}. Resetting to V1.")
        return variants[0]
    
    index = variants.index(current_variant)
    
    # Handle diagnosis
    if diagnosis == Diagnosis.INCREASE:
        if index < len(variants) - 1:
            new_variant = variants[index + 1]
            print(f"📈 Increasing difficulty: {current_variant} → {new_variant}")
            return new_variant
        else:
            print(f"🏆 Already at max difficulty: {current_variant}")
            return current_variant
    
    elif diagnosis == Diagnosis.DECREASE:
        if index > 0:
            new_variant = variants[index - 1]
            print(f"📉 Decreasing difficulty: {current_variant} → {new_variant}")
            return new_variant
        else:
            print(f"🔰 Already at min difficulty: {current_variant}")
            return current_variant
    
    else:  # maintain
        print(f"➡️ Maintaining difficulty: {current_variant}")
        return current_variant


def get_variant_info(variant_code: str) -> Optional[Dict]:
    """
    Get metadata for a specific variant.
    
    Args:
        variant_code: Variant code (e.g., "L-V2")
    
    Returns:
        Variant metadata dict or None if not found
    """
    return VARIANT_METADATA.get(variant_code)


def get_difficulty_level(variant_code: str) -> int:
    """
    Get numeric difficulty level (1-4) for a variant.
    
    Args:
        variant_code: Variant code (e.g., "L-V2")
    
    Returns:
        Difficulty level (1-4) or 1 if not found
    """
    metadata = get_variant_info(variant_code)
    return metadata.get("difficulty", 1) if metadata else 1


def get_expected_time(variant_code: str) -> int:
    """
    Get expected completion time in seconds.
    
    Args:
        variant_code: Variant code (e.g., "L-V2")
    
    Returns:
        Expected time in seconds
    """
    metadata = get_variant_info(variant_code)
    return metadata.get("typical_time", 60) if metadata else 60


def get_all_variants_for_domain(domain: str) -> List[str]:
    """
    Get all available variants for a domain.
    
    Args:
        domain: Measurement domain
    
    Returns:
        List of variant codes
    
    Raises:
        ValueError: If domain is invalid
    """
    if domain not in VARIANTS:
        raise ValueError(f"Invalid domain: {domain}")
    return VARIANTS[domain]


def is_max_difficulty(domain: str, variant_code: str) -> bool:
    """
    Check if variant is at maximum difficulty for domain.
    
    Args:
        domain: Measurement domain
        variant_code: Variant code
    
    Returns:
        True if at max difficulty
    """
    variants = VARIANTS.get(domain, [])
    return variant_code == variants[-1] if variants else False


def is_min_difficulty(domain: str, variant_code: str) -> bool:
    """
    Check if variant is at minimum difficulty for domain.
    
    Args:
        domain: Measurement domain
        variant_code: Variant code
    
    Returns:
        True if at min difficulty
    """
    variants = VARIANTS.get(domain, [])
    return variant_code == variants[0] if variants else False


def reset_to_initial(domain: str) -> str:
    """
    Reset domain to initial variant (V1).
    
    Args:
        domain: Measurement domain
    
    Returns:
        Initial variant code
    
    Raises:
        ValueError: If domain is invalid
    """
    if domain not in VARIANTS:
        raise ValueError(f"Invalid domain: {domain}")
    return VARIANTS[domain][0]
