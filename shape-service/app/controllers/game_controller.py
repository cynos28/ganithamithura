from database.database import get_database
from fastapi import HTTPException
from datetime import datetime, timedelta



class GameController:
    async def start_game(self, user: dict):
        try:
            db = get_database()
            users_collection = db["users"]
            games_collection = db["games"]

            user_data = await users_collection.find_one({"user_name": user["user_name"]})
            if not user_data:
                raise HTTPException(status_code=404, detail="User not found")

            level_progress = user_data.get("level_progress", {})
            passed_levels = [int(level) for level, data in level_progress.items() if data.get("status") == "pass"]
            current_level = max(passed_levels) + 1 if passed_levels else 1

            game_data = await games_collection.find_one({"level": current_level})
            if not game_data:
                # If no game data for the next level, maybe the user has completed all levels
                # For now, let's return the last level's data
                last_level_data = await games_collection.find_one({"level": max(passed_levels) if passed_levels else 1})
                if not last_level_data:
                    raise HTTPException(status_code=404, detail="No game data found")
                last_level_data.pop("_id", None)
                return last_level_data

            game_data.pop("_id", None)
            return game_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    