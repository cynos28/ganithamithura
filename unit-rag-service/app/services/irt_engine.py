"""
IRT Adaptive Engine for Build-a-Bridge (L-V4)
==============================================

Implements a simplified 1PL (Rasch) Item-Response-Theory model to
adapt game difficulty per-student in real time.

Key concepts
------------
* **θ (theta)** — student ability on a continuous logit scale.
  θ = 0 ↔ average learner.  Positive = stronger.
* **β (beta)** — item (round) difficulty on the same scale.
* **P(correct)** = σ(θ − β) where σ is the logistic sigmoid.
* After each round we update θ online:
      θ ← θ + α · (outcome − P_expected)
  where α starts at 0.4 and decays toward 0.15 as more rounds accumulate,
  giving faster initial calibration and stability later.

Difficulty → Game-parameter mapping
------------------------------------
θ is mapped to a discrete *difficulty_level* (1-5) via fixed cut-points,
and each level selects different game parameters:

  Level 1 (θ < −1.0)  — target 8-12 cm, 2-3 planks, sizes 3-6
  Level 2 (−1.0 ≤ θ < 0)  — target 10-15, 3-4 planks, sizes 3-7
  Level 3 (0 ≤ θ < 0.8) — target 12-18, 4-5 planks, sizes 3-8
  Level 4 (0.8 ≤ θ < 1.5) — target 15-22, 4-6 planks, sizes 2-9, distractors
  Level 5 (θ ≥ 1.5)  — target 18-28, 5-7 planks, sizes 2-10, many distractors
"""

from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple


# ── IRT maths ────────────────────────────────────────────────────────────────

def _sigmoid(x: float) -> float:
    """Logistic sigmoid, clamped to avoid overflow."""
    x = max(-10.0, min(10.0, x))
    return 1.0 / (1.0 + math.exp(-x))


def irt_probability(theta: float, beta: float) -> float:
    """1PL probability of a correct response."""
    return _sigmoid(theta - beta)


def irt_update_theta(
    theta: float,
    beta: float,
    outcome: int,       # 1 = correct, 0 = incorrect
    rounds_so_far: int,
) -> float:
    """
    Online update of θ after one round.

    Uses a decaying learning rate:
        α = max(0.15, 0.4 × 0.95^n)
    so early rounds have stronger influence while later rounds stabilise.
    """
    alpha = max(0.15, 0.4 * (0.95 ** rounds_so_far))
    p_expected = irt_probability(theta, beta)
    theta_new = theta + alpha * (outcome - p_expected)
    # Clamp to reasonable range
    return max(-3.0, min(3.0, theta_new))


# ── Difficulty level mapping ────────────────────────────────────────────────

_THETA_CUTPOINTS: List[float] = [-1.0, 0.0, 0.8, 1.5]

def theta_to_level(theta: float) -> int:
    """Map continuous θ → difficulty level 1-5."""
    for i, cut in enumerate(_THETA_CUTPOINTS):
        if theta < cut:
            return i + 1
    return 5


def level_to_beta(level: int) -> float:
    """
    Map discrete difficulty level to an item difficulty β on the logit
    scale.  Chosen so that an average student (θ=0) has ~73% chance on
    level 1 and ~27% on level 5.
    """
    return {1: -1.0, 2: -0.3, 3: 0.3, 4: 0.8, 5: 1.5}.get(level, 0.0)


# ── L-V4 parameter presets per difficulty level ──────────────────────────────

@dataclass
class BridgeLevelConfig:
    """Game-parameter preset for one difficulty band."""
    bridge_target_range: Tuple[int, int]
    plank_sizes: List[int]
    plank_count: int          # total strips shown (solution + distractors)
    min_solution_planks: int  # minimum planks required in the solution
    max_solution_planks: int  # maximum planks in the solution
    hints_allowed: int

_BRIDGE_CONFIGS: Dict[int, BridgeLevelConfig] = {
    1: BridgeLevelConfig(
        bridge_target_range=(8, 12),
        plank_sizes=[3, 4, 5, 6],
        plank_count=5,
        min_solution_planks=2,
        max_solution_planks=3,
        hints_allowed=3,
    ),
    2: BridgeLevelConfig(
        bridge_target_range=(10, 15),
        plank_sizes=[3, 4, 5, 6, 7],
        plank_count=6,
        min_solution_planks=2,
        max_solution_planks=3,
        hints_allowed=2,
    ),
    3: BridgeLevelConfig(
        bridge_target_range=(12, 18),
        plank_sizes=[3, 4, 5, 6, 7, 8],
        plank_count=7,
        min_solution_planks=2,
        max_solution_planks=4,
        hints_allowed=2,
    ),
    4: BridgeLevelConfig(
        bridge_target_range=(15, 22),
        plank_sizes=[2, 3, 4, 5, 6, 7, 8, 9],
        plank_count=8,
        min_solution_planks=3,
        max_solution_planks=5,
        hints_allowed=1,
    ),
    5: BridgeLevelConfig(
        bridge_target_range=(18, 28),
        plank_sizes=[2, 3, 4, 5, 6, 7, 8, 9, 10],
        plank_count=9,
        min_solution_planks=3,
        max_solution_planks=6,
        hints_allowed=1,
    ),
}


def get_bridge_config(level: int) -> BridgeLevelConfig:
    """Return the L-V4 parameter preset for the given difficulty band."""
    return _BRIDGE_CONFIGS.get(level, _BRIDGE_CONFIGS[3])


def bridge_config_to_params(level: int) -> Dict[str, Any]:
    """
    Convert a BridgeLevelConfig into the flat dict format expected by
    the Flutter frontend (identical key names to existing `GameParameters.params`).
    """
    cfg = get_bridge_config(level)
    return {
        "bridge_target_range": list(cfg.bridge_target_range),
        "plank_sizes": cfg.plank_sizes,
        "plank_count": cfg.plank_count,
        "min_solution_planks": cfg.min_solution_planks,
        "max_solution_planks": cfg.max_solution_planks,
        "hints": cfg.hints_allowed,
    }


# ── A-V1 (Tile Rectangle) parameter presets per difficulty level ─────────────

@dataclass
class AreaTileLevelConfig:
    """Game-parameter preset for A-V1 Tile Rectangle at one difficulty band."""
    min_rect_size: int
    max_rect_size: int
    grid_visible: bool
    extra_grid_range: Tuple[int, int]   # (min_extra, max_extra) rows/cols
    hints_allowed: int

_AREA_TILE_CONFIGS: Dict[int, AreaTileLevelConfig] = {
    1: AreaTileLevelConfig(
        min_rect_size=2, max_rect_size=3,
        grid_visible=True, extra_grid_range=(1, 2), hints_allowed=3,
    ),
    2: AreaTileLevelConfig(
        min_rect_size=2, max_rect_size=4,
        grid_visible=True, extra_grid_range=(1, 2), hints_allowed=2,
    ),
    3: AreaTileLevelConfig(
        min_rect_size=2, max_rect_size=6,
        grid_visible=True, extra_grid_range=(1, 3), hints_allowed=2,
    ),
    4: AreaTileLevelConfig(
        min_rect_size=3, max_rect_size=7,
        grid_visible=True, extra_grid_range=(2, 3), hints_allowed=1,
    ),
    5: AreaTileLevelConfig(
        min_rect_size=4, max_rect_size=8,
        grid_visible=True, extra_grid_range=(2, 4), hints_allowed=1,
    ),
}


def area_tile_config_to_params(level: int) -> Dict[str, Any]:
    """Convert AreaTileLevelConfig → flat dict for Flutter (A-V1)."""
    cfg = _AREA_TILE_CONFIGS.get(level, _AREA_TILE_CONFIGS[3])
    return {
        "min_rect_size": cfg.min_rect_size,
        "max_rect_size": cfg.max_rect_size,
        "grid_visible": cfg.grid_visible,
        "extra_grid_min": cfg.extra_grid_range[0],
        "extra_grid_max": cfg.extra_grid_range[1],
        "hints": cfg.hints_allowed,
    }


# ── A-V2 (Area Architect) parameter presets per difficulty level ─────────────

@dataclass
class AreaArchitectLevelConfig:
    """Game-parameter preset for A-V2 Area Architect at one difficulty band."""
    room_rows_range: Tuple[int, int]
    room_cols_range: Tuple[int, int]
    target_width_range: Tuple[int, int]
    target_height_range: Tuple[int, int]
    level_types: List[str]          # allowed level-type names
    hints_allowed: int

_AREA_ARCHITECT_CONFIGS: Dict[int, AreaArchitectLevelConfig] = {
    1: AreaArchitectLevelConfig(
        room_rows_range=(3, 4), room_cols_range=(4, 5),
        target_width_range=(2, 3), target_height_range=(2, 3),
        level_types=["fillRectangle"],
        hints_allowed=3,
    ),
    2: AreaArchitectLevelConfig(
        room_rows_range=(4, 5), room_cols_range=(5, 7),
        target_width_range=(3, 5), target_height_range=(2, 4),
        level_types=["fillRectangle", "formulaRectangle"],
        hints_allowed=2,
    ),
    3: AreaArchitectLevelConfig(
        room_rows_range=(4, 6), room_cols_range=(5, 8),
        target_width_range=(3, 6), target_height_range=(3, 5),
        level_types=["formulaRectangle", "mysterySide"],
        hints_allowed=2,
    ),
    4: AreaArchitectLevelConfig(
        room_rows_range=(5, 7), room_cols_range=(6, 9),
        target_width_range=(4, 7), target_height_range=(3, 5),
        level_types=["formulaRectangle", "mysterySide", "lShapeDemo"],
        hints_allowed=1,
    ),
    5: AreaArchitectLevelConfig(
        room_rows_range=(5, 8), room_cols_range=(7, 10),
        target_width_range=(5, 8), target_height_range=(4, 6),
        level_types=["mysterySide", "lShapeDemo"],
        hints_allowed=1,
    ),
}


def area_architect_config_to_params(level: int) -> Dict[str, Any]:
    """Convert AreaArchitectLevelConfig → flat dict for Flutter (A-V2)."""
    cfg = _AREA_ARCHITECT_CONFIGS.get(level, _AREA_ARCHITECT_CONFIGS[3])
    return {
        "room_rows_range": list(cfg.room_rows_range),
        "room_cols_range": list(cfg.room_cols_range),
        "target_width_range": list(cfg.target_width_range),
        "target_height_range": list(cfg.target_height_range),
        "level_types": cfg.level_types,
        "hints": cfg.hints_allowed,
    }


# ── V-V1 (Fill to Target) parameter presets per difficulty level ────────────

@dataclass
class VolumeFillLevelConfig:
    """Game-parameter preset for V-V1 Fill to Target at one difficulty band."""
    capacity_ml: int
    target_ml_options: List[int]
    tolerance_ml: int
    normal_pour_step: int
    fast_pour_step: int
    fine_tune_step: int
    hints_allowed: int

_VOLUME_FILL_CONFIGS: Dict[int, VolumeFillLevelConfig] = {
    1: VolumeFillLevelConfig(
        capacity_ml=500,
        target_ml_options=[100, 150, 200, 250, 300],  # Easy multiples of 50
        tolerance_ml=5,   # Tight tolerance - near exact
        normal_pour_step=100,
        fast_pour_step=50,
        fine_tune_step=10,
        hints_allowed=3,
    ),
    2: VolumeFillLevelConfig(
        capacity_ml=500,
        target_ml_options=[110, 160, 210, 260, 310],  # Requires 10ml steps
        tolerance_ml=3,
        normal_pour_step=100,
        fast_pour_step=50,
        fine_tune_step=10,
        hints_allowed=2,
    ),
    3: VolumeFillLevelConfig(
        capacity_ml=500,
        target_ml_options=[120, 170, 230, 290, 370],  # Requires precision
        tolerance_ml=2,
        normal_pour_step=100,
        fast_pour_step=50,
        fine_tune_step=10,
        hints_allowed=2,
    ),
    4: VolumeFillLevelConfig(
        capacity_ml=1000,
        target_ml_options=[125, 275, 425, 575, 725],  # Requires 25ml/5ml steps
        tolerance_ml=1,
        normal_pour_step=100,
        fast_pour_step=25,
        fine_tune_step=5,
        hints_allowed=1,
    ),
    5: VolumeFillLevelConfig(
        capacity_ml=1000,
        target_ml_options=[135, 285, 465, 615, 785, 935],  # Most precise
        tolerance_ml=0,   # Exact match required
        normal_pour_step=100,
        fast_pour_step=25,
        fine_tune_step=5,
        hints_allowed=1,
    ),
}


def volume_fill_config_to_params(level: int) -> Dict[str, Any]:
    """Convert VolumeFillLevelConfig → flat dict for Flutter (V-V1)."""
    cfg = _VOLUME_FILL_CONFIGS.get(level, _VOLUME_FILL_CONFIGS[3])
    return {
        "capacity_ml": cfg.capacity_ml,
        "target_ml_options": cfg.target_ml_options,
        "tolerance_ml": cfg.tolerance_ml,
        "normal_pour_step": cfg.normal_pour_step,
        "fast_pour_step": cfg.fast_pour_step,
        "fine_tune_step": cfg.fine_tune_step,
        "hints": cfg.hints_allowed,
    }


# ── V-V2 (Volume Compare) parameter presets per difficulty level ─────────────

@dataclass
class VolumeCompareLevelConfig:
    """Game-parameter preset for V-V2 Volume Compare at one difficulty band."""
    question_types: List[str]          # 'most', 'least', 'same'
    size_differences: List[float]      # available size ratios
    container_types: List[str]         # container image names
    option_count: int                  # number of options per question
    hints_allowed: int

_VOLUME_COMPARE_CONFIGS: Dict[int, VolumeCompareLevelConfig] = {
    1: VolumeCompareLevelConfig(
        question_types=['most'],
        size_differences=[0.4, 0.65, 0.95],
        container_types=['cup1', 'glass1'],
        option_count=3,
        hints_allowed=3,
    ),
    2: VolumeCompareLevelConfig(
        question_types=['most', 'least'],
        size_differences=[0.4, 0.65, 0.95],
        container_types=['cup1', 'glass1', 'jug1'],
        option_count=3,
        hints_allowed=2,
    ),
    3: VolumeCompareLevelConfig(
        question_types=['most', 'least', 'same'],
        size_differences=[0.4, 0.65, 0.95],
        container_types=['cup1', 'glass1', 'jug1', 'jug2'],
        option_count=3,
        hints_allowed=2,
    ),
    4: VolumeCompareLevelConfig(
        question_types=['most', 'least', 'same'],
        size_differences=[0.4, 0.65, 0.95],
        container_types=['cup1', 'glass1', 'jug1', 'jug2', 'jug3'],
        option_count=4,
        hints_allowed=1,
    ),
    5: VolumeCompareLevelConfig(
        question_types=['least', 'same'],
        size_differences=[0.4, 0.65, 0.95],
        container_types=['cup1', 'glass1', 'jug1', 'jug2', 'jug3'],
        option_count=4,
        hints_allowed=1,
    ),
}


def volume_compare_config_to_params(level: int) -> Dict[str, Any]:
    """Convert VolumeCompareLevelConfig → flat dict for Flutter (V-V2)."""
    cfg = _VOLUME_COMPARE_CONFIGS.get(level, _VOLUME_COMPARE_CONFIGS[3])
    return {
        "question_types": cfg.question_types,
        "size_differences": cfg.size_differences,
        "container_types": cfg.container_types,
        "option_count": cfg.option_count,
        "hints": cfg.hints_allowed,
    }


# ── Generic config dispatcher ───────────────────────────────────────────────

# ── W-W1 (Weight Match Target) parameter presets per difficulty level ────────

@dataclass
class WeightMatchLevelConfig:
    """Game-parameter preset for W-W1 Match the Target at one difficulty band."""
    available_weight_grams: List[int]  # which weights are in tray
    max_target_grams: int              # ceiling for target
    max_pieces: int                    # max weight tiles to combine
    hints_allowed: int

_WEIGHT_MATCH_CONFIGS: Dict[int, WeightMatchLevelConfig] = {
    1: WeightMatchLevelConfig(
        available_weight_grams=[10, 50],
        max_target_grams=100,
        max_pieces=2,
        hints_allowed=3,
    ),
    2: WeightMatchLevelConfig(
        available_weight_grams=[10, 50, 100],
        max_target_grams=200,
        max_pieces=3,
        hints_allowed=2,
    ),
    3: WeightMatchLevelConfig(
        available_weight_grams=[10, 50, 100, 200],
        max_target_grams=350,
        max_pieces=4,
        hints_allowed=2,
    ),
    4: WeightMatchLevelConfig(
        available_weight_grams=[10, 50, 100, 200, 500],
        max_target_grams=500,
        max_pieces=4,
        hints_allowed=1,
    ),
    5: WeightMatchLevelConfig(
        available_weight_grams=[10, 50, 100, 200, 500],
        max_target_grams=700,
        max_pieces=5,
        hints_allowed=0,
    ),
}


def weight_match_config_to_params(level: int) -> Dict[str, Any]:
    """Convert WeightMatchLevelConfig → flat dict for Flutter (W-W1)."""
    cfg = _WEIGHT_MATCH_CONFIGS.get(level, _WEIGHT_MATCH_CONFIGS[3])
    return {
        "available_weight_grams": cfg.available_weight_grams,
        "max_target_grams": cfg.max_target_grams,
        "max_pieces": cfg.max_pieces,
        "hints": cfg.hints_allowed,
    }


# ── W-W2 (Weight Equal Sides) parameter presets per difficulty level ──────────

@dataclass
class WeightEqualLevelConfig:
    """Game-parameter preset for W-W2 Equal Sides at one difficulty band."""
    available_weight_grams: List[int]
    max_target_grams: int
    max_pieces: int
    hints_allowed: int

_WEIGHT_EQUAL_CONFIGS: Dict[int, WeightEqualLevelConfig] = {
    1: WeightEqualLevelConfig(
        available_weight_grams=[10, 50],
        max_target_grams=100,
        max_pieces=2,
        hints_allowed=3,
    ),
    2: WeightEqualLevelConfig(
        available_weight_grams=[10, 50, 100],
        max_target_grams=200,
        max_pieces=3,
        hints_allowed=2,
    ),
    3: WeightEqualLevelConfig(
        available_weight_grams=[10, 50, 100, 200],
        max_target_grams=350,
        max_pieces=4,
        hints_allowed=2,
    ),
    4: WeightEqualLevelConfig(
        available_weight_grams=[50, 100, 200, 500],
        max_target_grams=500,
        max_pieces=4,
        hints_allowed=1,
    ),
    5: WeightEqualLevelConfig(
        available_weight_grams=[10, 50, 100, 200, 500],
        max_target_grams=700,
        max_pieces=5,
        hints_allowed=0,
    ),
}


def weight_equal_config_to_params(level: int) -> Dict[str, Any]:
    """Convert WeightEqualLevelConfig → flat dict for Flutter (W-W2)."""
    cfg = _WEIGHT_EQUAL_CONFIGS.get(level, _WEIGHT_EQUAL_CONFIGS[3])
    return {
        "available_weight_grams": cfg.available_weight_grams,
        "max_target_grams": cfg.max_target_grams,
        "max_pieces": cfg.max_pieces,
        "hints": cfg.hints_allowed,
    }


# ── Generic config dispatcher ───────────────────────────────────────────────

def config_to_params(domain: str, variant: str, level: int) -> Dict[str, Any]:
    """
    Dispatch to the correct config-to-params function based on domain/variant.
    Falls back to bridge params for backward compatibility.
    """
    if domain == "area" and variant == "A-V1":
        return area_tile_config_to_params(level)
    if domain == "area" and variant == "A-V2":
        return area_architect_config_to_params(level)
    if domain == "volume" and variant == "V-V1":
        return volume_fill_config_to_params(level)
    if domain == "volume" and variant == "V-V2":
        return volume_compare_config_to_params(level)
    if domain == "weight" and variant == "W-W1":
        return weight_match_config_to_params(level)
    if domain == "weight" and variant == "W-W2":
        return weight_equal_config_to_params(level)
    # Default: length / bridge
    return bridge_config_to_params(level)


# ── Full round-evaluation pipeline ──────────────────────────────────────────

@dataclass
class RoundOutcome:
    """Input: what happened in one round."""
    correct: bool
    attempts: int
    hints_used: int
    time_seconds: float

@dataclass
class IRTResult:
    """Output: updated IRT state + next-round parameters."""
    theta_before: float
    theta_after: float
    beta: float
    p_expected: float
    outcome: int               # 1 or 0
    difficulty_level: int      # updated band 1-5
    next_params: Dict[str, Any]  # flat dict for Flutter


def evaluate_round(
    theta: float,
    difficulty_level: int,
    round_outcome: RoundOutcome,
    rounds_played: int,
    domain: str = "length",
    variant: str = "L-V4",
) -> IRTResult:
    """
    Core IRT evaluation for one game round.

    1. Maps current level → β
    2. Determines binary outcome (correct on first/second attempt = 1, else 0)
    3. Updates θ
    4. Computes new difficulty level and corresponding game parameters
    """
    beta = level_to_beta(difficulty_level)
    
    # Outcome: correct with ≤ 2 attempts counts as success for IRT
    outcome = 1 if round_outcome.correct and round_outcome.attempts <= 2 else 0

    p_expected = irt_probability(theta, beta)
    theta_new = irt_update_theta(theta, beta, outcome, rounds_played)
    new_level = theta_to_level(theta_new)
    next_params = config_to_params(domain, variant, new_level)

    return IRTResult(
        theta_before=theta,
        theta_after=theta_new,
        beta=beta,
        p_expected=p_expected,
        outcome=outcome,
        difficulty_level=new_level,
        next_params=next_params,
    )


# ── Session-level summary helpers ────────────────────────────────────────────

def compute_session_stats(round_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Aggregate statistics from the round_history list stored in GameSession.
    Useful for analytics/dashboard.
    """
    if not round_history:
        return {
            "total_rounds": 0,
            "accuracy": 0.0,
            "avg_attempts": 0.0,
            "avg_time": 0.0,
            "theta_trend": [],
            "difficulty_trend": [],
        }

    total = len(round_history)
    correct = sum(1 for r in round_history if r.get("correct", False))
    avg_attempts = sum(r.get("attempts", 1) for r in round_history) / total
    avg_time = sum(r.get("time_s", 0) for r in round_history) / total
    theta_trend = [r.get("theta_after", 0.0) for r in round_history]
    difficulty_trend = [theta_to_level(t) for t in theta_trend]

    return {
        "total_rounds": total,
        "accuracy": correct / total,
        "avg_attempts": round(avg_attempts, 2),
        "avg_time": round(avg_time, 1),
        "theta_trend": theta_trend,
        "difficulty_trend": difficulty_trend,
    }
