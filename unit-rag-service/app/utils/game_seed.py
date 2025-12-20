from app.models.games import GameParameters


INITIAL_GAME_PARAMETERS = [
    {
        "domain": "length",
        "params": {
            "current_variant": "L-V1",
            "target_range": [5, 10],
            "tolerance": 0.1,
            "required_objects": 1,
            "hints": 2
        }
    },
    {
        "domain": "capacity",
        "params": {
            "current_variant": "C-V1",
            "target_volume": 200,
            "pour_step": 50,
            "show_ghost_line": True,
            "ingredients": 1
        }
    },
    {
        "domain": "area",
        "params": {
            "current_variant": "A-V1",
            "tile_goal": 4,
            "grid_visible": True,
            "shape_complexity": 1,
            "outline": True
        }
    },
    {
        "domain": "weight",
        "params": {
            "current_variant": "W-V1",
            "target_weight": 300,
            "tolerance": 0.15,
            "show_labels": True,
            "object_variety": 2
        }
    }
]


async def seed_game_parameters():
    """
    Safely seed initial game parameters.
    Inserts only if domain does NOT exist.
    """
    for entry in INITIAL_GAME_PARAMETERS:
        domain = entry["domain"]

        existing = await GameParameters.find_one(
            GameParameters.domain == domain
        )

        if existing:
            print(f"ℹ️ Game parameters already exist for domain: {domain}")
            continue

        await GameParameters(**entry).insert()
        print(f"✅ Seeded game parameters for domain: {domain}")
