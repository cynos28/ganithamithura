"""
Initialize Length Game Parameters in Database
==============================================
Run this script to set up default adaptive parameters for all length game variants.

Usage:
    python scripts/init_length_game_params.py
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import sys
import os

# Add parent directory to path to import models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.models.games import GameParameters


async def init_database():
    """Initialize database connection."""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    await init_beanie(
        database=client.ganithamithura,
        document_models=[GameParameters]
    )
    print("✅ Database connected")


async def setup_length_params():
    """Create or update length game parameters."""
    
    # Default parameters for length domain with all variants
    length_params = {
        "current_variant": "L-V1",
        "hints": 2,
        
        # V1 (Ruler Explorer) - measuring single objects with ruler
        "object_size_range": [5, 15],      # cm range for objects
        "choice_spread": 3,                 # ±1-3 cm for wrong choices
        
        # V2 (Compare) - comparing two objects
        "min_size_difference": 3,           # minimum cm difference between objects
        
        # V3 (Calculate & Win) - unit conversion (mm ↔ cm ↔ m)
        "allow_decimals": False,            # whether to use decimal values
        "value_range_mm": [30, 150],        # mm value range
        "value_range_m": [0.05, 0.25],      # m value range
        
        # V4 (Bridge) - combining planks to build bridge
        "bridge_target_range": [10, 18],    # target bridge length range (cm)
        "plank_sizes": [3, 4, 5, 6, 7, 8, 9],  # available plank sizes (cm)
        "plank_count": 7,                   # number of planks to choose from
    }
    
    # Check if length params already exist
    existing = await GameParameters.find_one(GameParameters.domain == "length")
    
    if existing:
        print("📝 Updating existing length parameters...")
        existing.params = length_params
        await existing.save()
        print("✅ Length parameters updated")
    else:
        print("➕ Creating new length parameters...")
        doc = GameParameters(domain="length", params=length_params)
        await doc.insert()
        print("✅ Length parameters created")
    
    print("\n📊 Current Length Parameters:")
    print(f"   Variant: {length_params['current_variant']}")
    print(f"   Hints: {length_params['hints']}")
    print(f"   V1 - Object Size Range: {length_params['object_size_range']} cm")
    print(f"   V2 - Min Size Diff: {length_params['min_size_difference']} cm")
    print(f"   V3 - Allow Decimals: {length_params['allow_decimals']}")
    print(f"   V4 - Bridge Target: {length_params['bridge_target_range']} cm")
    print(f"   V4 - Plank Count: {length_params['plank_count']}")


async def main():
    """Main execution."""
    print("🚀 Initializing Length Game Parameters...\n")
    
    try:
        await init_database()
        await setup_length_params()
        print("\n✨ Setup complete!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
