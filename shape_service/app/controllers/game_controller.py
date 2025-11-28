from common.database.database import get_database
from fastapi import HTTPException
from datetime import datetime, timedelta
from app.models.model import GameAnswer



class GameController:
    async def start_game(self, user: dict):
        """
        Initializes and starts a game session for a given user.

        Args:
            user (dict): A dictionary containing user information, specifically
                         "user_name" to identify the user.

        Returns:
            dict: A dictionary containing the game data for the current or next level.
                  The "_id" field is removed from the returned game data.
        """
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
    
    async def check_answers(self, game_answer: GameAnswer, user: dict):
            try:
                db = get_database()
                games_collection = db["games"]
                users_collection = db["users"]

                level = game_answer.level
                answers = game_answer.answers

                game_data = await games_collection.find_one({"level": level})
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

                return {"score": score, "total_questions": total_questions, "status": game_status, "results": results}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
 

    