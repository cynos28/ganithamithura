"""
Seed default GameParameters documents into MongoDB on startup.

Called from app.main → startup_event().
"""

from app.models.games import GameParameters


# ─── default parameter presets per domain ────────────────────────────────────

_DEFAULTS = {
    "length": {
        "current_variant": "L-V1",
        "hints": 2,
        # V1 (Ruler Explorer)
        "object_size_range": [5, 15],
        "choice_spread": 3,
        # V2 (Compare)
        "min_size_difference": 3,
        # V3 (Calculate & Win)
        "allow_decimals": False,
        "value_range_mm": [30, 150],
        "value_range_m": [0.05, 0.25],
        # V4 (Bridge) — IRT Level-3 defaults
        "bridge_target_range": [12, 18],
        "plank_sizes": [3, 4, 5, 6, 7, 8],
        "plank_count": 7,
        "min_solution_planks": 2,
        "max_solution_planks": 4,
    },
    "area": {
        "current_variant": "A-V1",
        "hints": 2,
        "max_rect_size": 6,
        "min_rect_size": 2,
        "grid_visible": True,
        "shape_complexity": 1,
        "target_area_range": [8, 20],
        "require_two_solutions": False,
        "max_parts": 2,
    },
    "volume": {
        "current_variant": "C-V1",
        "target_volume": 200,
        "pour_step": 50,
        "show_ghost_line": True,
        "ingredients": 1,
    },
    "weight": {
        "current_variant": "W-V1",
        "target_weight": 300,
        "tolerance": 0.15,
        "show_labels": True,
        "object_variety": 2,
    },
}


async def seed_game_parameters():
    """
    Insert default GameParameters if they don't already exist.
    Existing documents are left untouched (teacher / admin edits preserved).
    """
    for domain, params in _DEFAULTS.items():
        existing = await GameParameters.find_one(GameParameters.domain == domain)
        if existing is None:
            doc = GameParameters(domain=domain, params=params)
            await doc.insert()
            print(f"  🌱 Seeded game parameters for '{domain}'")
        else:
            print(f"  ✅ Game parameters for '{domain}' already exist — skipping")
