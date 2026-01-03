from common.database.database import get_database
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.models.model import GameAnswer, UserBadgeList
from app.constants.constants import BADGE_THRESHOLDS


class GameController:

    def _convert_image_urls(self, game_data: dict, base_url: str = "http://localhost:8000/shapes-patterns"):
        """Convert asset paths to backend URLs or keep as Flutter assets"""
        # For shapes in matching games
        if "shapes" in game_data:
            for shape in game_data["shapes"]:
                if "image_url" in shape:
                    # Keep the asset path as-is since Flutter has these locally
                    # The frontend will use these asset paths
                    pass
        
        # For questions with images
        if "questions" in game_data:
            for question in game_data["questions"]:
                if "image_url" in question:
                    pass
        
        # For patterns
        if "patterns" in game_data:
            for pattern in game_data["patterns"]:
                if "sequence" in pattern:
                    for item in pattern["sequence"]:
                        if item and "image_url" in item:
                            pass
        
        # For shape_pool in pattern matching
        if "shape_pool" in game_data:
            for shape in game_data["shape_pool"]:
                if "image_url" in shape:
                    pass
        
        return game_data

    async def start_game(self, user: dict, game_id: str = None):
        """
        Initializes and starts a game session for a given user.

        Args:
            user (dict): A dictionary containing user information, specifically
                         "user_name" to identify the user.
            game_id (str, optional): Optional game level ID (e.g., "level1", "level2").

        Returns:
            dict: A dictionary containing the game data for the current or next level.
        """
        try:
            db = get_database()
            users_collection = db["users"]
            games_collection = db["games"]

            user_data = await users_collection.find_one({"user_name": user["user_name"]})
            if not user_data:
                raise HTTPException(status_code=404, detail="User not found")

            # If game_id is provided, fetch that specific level
            if game_id:
                level_num = int(game_id.replace("level", "")) if "level" in game_id else int(game_id)
                # Try to find by level number first, then by game_id as fallback
                game_data = await games_collection.find_one({"level": level_num})
                if not game_data:
                    # Fallback: try to find by game_id field
                    game_data = await games_collection.find_one({"game_id": game_id})
                if not game_data:
                    raise HTTPException(status_code=404, detail=f"Game data for {game_id} not found")
                game_data.pop("_id", None)
                return self._convert_image_urls(game_data)

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
                return self._convert_image_urls(last_level_data)

            game_data.pop("_id", None)
            return self._convert_image_urls(game_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    async def check_answers(self, game_answer: GameAnswer, user: dict):
            try:
                db = get_database()
                games_collection = db["games"]
                users_collection = db["users"]

                level = game_answer.level
                answers = game_answer.answers

                # Try to find by level number first, then by game_id as fallback
                game_data = await games_collection.find_one({"level": level})
                if not game_data:
                    # Fallback: try to find by game_id field
                    game_data = await games_collection.find_one({"game_id": f"level{level}"})
                if not game_data:
                    raise HTTPException(status_code=404, detail=f"Game data for level {level} not found")

                score = 0
                results = []
                wrongly_answered_questions = []

                if level == 1:
                    correct_answers = {shape["id"]: shape["name"] for shape in game_data.get("shapes", [])}
                    for answer in answers:
                        is_correct = correct_answers.get(answer.question_id, "").lower() == answer.answer.lower()
                        if is_correct:
                            score += 1
                        else:
                            wrongly_answered_questions.append({
                                "question_id": answer.question_id,
                                "your_answer": answer.answer,
                                "correct_answer": correct_answers.get(answer.question_id, "")
                            })
                        results.append({
                            "question_id": answer.question_id,
                            "is_correct": is_correct,
                            "correct_answer": correct_answers.get(answer.question_id, "")
                        })
                    total_questions = len(correct_answers)

                elif level == 2:
                    correct_answers = game_data.get("correct_answers", {})
                    for answer in answers:
                        is_correct = correct_answers.get(answer.question_id, "").lower() == answer.answer.lower()
                        if is_correct:
                            score += 1
                        else:
                            wrongly_answered_questions.append({
                                "question_id": answer.question_id,
                                "your_answer": answer.answer,
                                "correct_answer": correct_answers.get(answer.question_id, "")
                            })
                        results.append({
                            "question_id": answer.question_id,
                            "is_correct": is_correct,
                            "correct_answer": correct_answers.get(answer.question_id, "")
                        })
                    total_questions = len(correct_answers)

                elif level == 3:
                    # Level 3 is similar to level 1 - shape matching
                    correct_answers = {shape["id"]: shape["name"] for shape in game_data.get("shapes", [])}
                    for answer in answers:
                        is_correct = correct_answers.get(answer.question_id, "").lower() == answer.answer.lower()
                        if is_correct:
                            score += 1
                        else:
                            wrongly_answered_questions.append({
                                "question_id": answer.question_id,
                                "your_answer": answer.answer,
                                "correct_answer": correct_answers.get(answer.question_id, "")
                            })
                        results.append({
                            "question_id": answer.question_id,
                            "is_correct": is_correct,
                            "correct_answer": correct_answers.get(answer.question_id, "")
                        })
                    total_questions = len(correct_answers)

                elif level == 4:
                    # Level 4 is similar to level 2 - question round
                    correct_answers = game_data.get("correct_answers", {})
                    for answer in answers:
                        is_correct = correct_answers.get(answer.question_id, "").lower() == answer.answer.lower()
                        if is_correct:
                            score += 1
                        else:
                            wrongly_answered_questions.append({
                                "question_id": answer.question_id,
                                "your_answer": answer.answer,
                                "correct_answer": correct_answers.get(answer.question_id, "")
                            })
                        results.append({
                            "question_id": answer.question_id,
                            "is_correct": is_correct,
                            "correct_answer": correct_answers.get(answer.question_id, "")
                        })
                    total_questions = len(correct_answers)

                elif level in [5, 6]:
                    # Levels 5 and 6 are pattern matching
                    for answer in answers:
                        # Find the pattern by question_id (pattern id)
                        pattern = next((p for p in game_data.get("patterns", []) if p["id"] == answer.question_id), None)
                        if pattern:
                            is_correct = pattern["correct_answer"]["name"].lower() == answer.answer.lower()
                            if is_correct:
                                score += 1
                            else:
                                wrongly_answered_questions.append({
                                    "question_id": answer.question_id,
                                    "your_answer": answer.answer,
                                    "correct_answer": pattern["correct_answer"]["name"]
                                })
                            results.append({
                                "question_id": answer.question_id,
                                "is_correct": is_correct,
                                "correct_answer": pattern["correct_answer"]["name"]
                            })
                    total_questions = len(game_data.get("patterns", []))

                else:
                    raise HTTPException(status_code=400, detail=f"Answer checking for level {level} is not implemented")

                game_status = "pass" if score == total_questions else "fail"

                attempt_data = {
                    "level": level,
                    "status": game_status,
                    "timestamp": datetime.utcnow(),
                    "score": score,
                    "total_questions": total_questions,
                    "wrongly_answered_questions": wrongly_answered_questions
                }

                user_data = await users_collection.find_one({"user_name": user["user_name"]})
                level_progress = user_data.get("level_progress", {})
                previous_status = level_progress.get(str(level), {}).get("status", "fail")

                overall_game_status = "pass" if previous_status == "pass" or game_status == "pass" else "fail"

                update_operations = {
                    "$set": {
                        f"level_progress.{level}.status": overall_game_status,
                    },
                    "$push": {f"level_progress.{level}.attempt_history": attempt_data},
                    "$unset": {
                        f"level_progress.{level}.attempts": "",
                        f"level_progress.{level}.last_attempt": ""
                    }
                }

                if overall_game_status == "pass":
                    update_operations["$max"] = {"highest_passed_level": level}

                await users_collection.update_one(
                    {"user_name": user["user_name"]},
                    update_operations,
                    upsert=True
                )

                # Fetch the user again to get the updated highest_passed_level
                user_data = await users_collection.find_one({"user_name": user["user_name"]})
                highest_passed_level = user_data.get("highest_passed_level", 0)

                badge = None
                if highest_passed_level >= BADGE_THRESHOLDS['advanced']:
                    badge = "advanced"
                elif highest_passed_level >= BADGE_THRESHOLDS['intermediate']:
                    badge = "intermediate"
                elif highest_passed_level >= BADGE_THRESHOLDS['beginner']:
                    badge = "beginner"

                if badge:
                    await users_collection.update_one(
                        {"user_name": user["user_name"]},
                        {"$set": {"badge": badge}}
                    )

                return {"score": score, "total_questions": total_questions, "status": game_status, "results": results}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
 
    async def get_all_users_badges(self) -> UserBadgeList:
        """
        Retrieves the username and badge for all users.

        Returns:
            UserBadgeList: A list of users with their username and badge.
        """
        try:
            db = get_database()
            users_collection = db["users"]
            users = []
            async for user in users_collection.find({}, {"_id": 0, "user_name": 1, "badge": 1}):
                users.append({"username": user.get("user_name"), "badge": user.get("badge", "N/A")})
            return UserBadgeList(users=users)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))