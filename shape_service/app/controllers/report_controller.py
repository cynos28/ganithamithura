from common.database.database import get_database
from fastapi import HTTPException


class ReportController:

    async def get_user_game_report(self, user: dict):
        """
        Generates a game report for the specified user.

        Args:
            user (dict): A dictionary containing user information, including "user_name".

        Returns:
            dict: A dictionary containing the user's game report, including level progress and badge.
        """
        try:
            db = get_database()
            users_collection = db["users"]

            user_data = await users_collection.find_one({"user_name": user["user_name"]})
            if not user_data:
                raise HTTPException(status_code=404, detail="User not found")

            # Extract relevant data for the report
            level_progress = user_data.get("level_progress", {})
            highest_passed_level = user_data.get("highest_passed_level", 0)
            badge = user_data.get("badge", "N/A")
            
            # remove unnecessary fields from level_progress
            for level, data in level_progress.items():
                data.pop("status", None)
                for attempt in data.get("attempt_history", []):
                    attempt.pop("wrongly_answered_questions", None)

            report = {
                "user_name": user["user_name"],
                "highest_passed_level": highest_passed_level,
                "badge": badge,
                "level_progress": level_progress,
            }

            return report
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
