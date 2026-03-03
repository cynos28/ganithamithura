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
            
            # Create user if doesn't exist
            if not user_data:
                print(f"Creating new user: {user['user_name']}")
                new_user = {
                    "user_name": user["user_name"],
                    "level_progress": {},
                    "highest_passed_level": 0,
                    "build_match_progress": {},
                    "highest_build_challenge": 0,
                    "badge": None,
                    "created_at": datetime.utcnow()
                }
                await users_collection.insert_one(new_user)
                user_data = new_user
            else:
                # Initialize missing fields for existing users
                needs_update = False
                update_fields = {}
                
                if "build_match_progress" not in user_data:
                    update_fields["build_match_progress"] = {}
                    needs_update = True
                
                if "highest_build_challenge" not in user_data:
                    update_fields["highest_build_challenge"] = 0
                    needs_update = True
                
                if needs_update:
                    print(f"[INFO] Initializing missing fields for user {user['user_name']}: {list(update_fields.keys())}")
                    await users_collection.update_one(
                        {"user_name": user["user_name"]},
                        {"$set": update_fields}
                    )
                    # Refetch to get the updated document
                    user_data = await users_collection.find_one({"user_name": user["user_name"]})

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

                # For Build & Match challenges (levels 7+), game data is not required
                game_data = None
                if level <= 6:
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

                elif level >= 7:
                    # Levels 7+ are Build & Match challenges
                    # These are completion-based challenges, not question-based
                    # Frontend sends {'challenge': 'completed'} when challenge is passed
                    print(f"[DEBUG] Processing Build & Match Challenge - Level: {level}, Answers: {answers}")
                    for answer in answers:
                        print(f"[DEBUG] Checking answer: question_id={answer.question_id}, answer={answer.answer}")
                        if answer.answer.lower() == "completed":
                            score += 1
                            results.append({
                                "question_id": answer.question_id,
                                "is_correct": True,
                                "correct_answer": "completed"
                            })
                    total_questions = 1  # Each build challenge is a single completion
                    print(f"[DEBUG] Build Challenge Score: {score}/{total_questions}")
                    
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
                if not user_data:
                    # Create user if doesn't exist
                    print(f"Creating new user during check_answers: {user['user_name']}")
                    user_data = {
                        "user_name": user["user_name"],
                        "level_progress": {},
                        "highest_passed_level": 0,
                        "build_match_progress": {},
                        "highest_build_challenge": 0,
                        "badge": None,
                        "created_at": datetime.utcnow()
                    }
                    await users_collection.insert_one(user_data)
                    # Refetch to ensure we have the DB version
                    user_data = await users_collection.find_one({"user_name": user["user_name"]})
                else:
                    # Initialize missing fields for existing users
                    needs_update = False
                    update_fields = {}
                    
                    if "build_match_progress" not in user_data:
                        update_fields["build_match_progress"] = {}
                        needs_update = True
                    
                    if "highest_build_challenge" not in user_data:
                        update_fields["highest_build_challenge"] = 0
                        needs_update = True
                    
                    if needs_update:
                        print(f"[INFO] Initializing missing fields for user {user['user_name']}: {list(update_fields.keys())}")
                        await users_collection.update_one(
                            {"user_name": user["user_name"]},
                            {"$set": update_fields}
                        )
                        # Refetch to get the updated document
                        user_data = await users_collection.find_one({"user_name": user["user_name"]})
                
                # Determine if this is a Build & Match challenge (level >= 7) or a regular game (level <= 6)
                if level >= 7:
                    # Build & Match challenge - save to build_match_progress
                    challenge_num = level - 6  # Convert level 7 -> challenge 1, level 8 -> challenge 2, etc.
                    build_progress = user_data.get("build_match_progress", {})
                    challenge_data = build_progress.get(str(challenge_num), {})
                    previous_status = challenge_data.get("status", "fail")
                    existing_attempts = challenge_data.get("attempt_history", [])
                    
                    overall_status = "pass" if previous_status == "pass" or game_status == "pass" else "fail"
                    
                    # Append new attempt to existing history
                    updated_attempts = existing_attempts + [attempt_data]
                    
                    # Build update operations
                    update_operations = {
                        "$set": {
                            f"build_match_progress.{challenge_num}": {
                                "status": overall_status,
                                "attempt_history": updated_attempts
                            }
                        }
                    }
                    
                    # Track highest completed build challenge
                    if overall_status == "pass":
                        # Initialize highest_build_challenge if it doesn't exist
                        current_highest = user_data.get("highest_build_challenge", 0)
                        if challenge_num > current_highest:
                            update_operations["$set"]["highest_build_challenge"] = challenge_num
                    
                    print(f"[DEBUG] Updating Build & Match Challenge {challenge_num} for user {user['user_name']} - Status: {overall_status}")
                    print(f"[DEBUG] Update operations: {update_operations}")
                    
                else:
                    # Regular shape game - save to level_progress
                    level_progress = user_data.get("level_progress", {})
                    previous_status = level_progress.get(str(level), {}).get("status", "fail")

                    overall_status = "pass" if previous_status == "pass" or game_status == "pass" else "fail"

                    update_operations = {
                        "$set": {
                            f"level_progress.{level}.status": overall_status,
                        },
                        "$push": {f"level_progress.{level}.attempt_history": attempt_data},
                        "$unset": {
                            f"level_progress.{level}.attempts": "",
                            f"level_progress.{level}.last_attempt": ""
                        }
                    }

                    if overall_status == "pass":
                        update_operations["$max"] = {"highest_passed_level": level}

                    print(f"Updating user {user['user_name']} - Level: {level}, Status: {overall_status}, Score: {score}/{total_questions}")
                
                print(f"[DEBUG] About to update database for user {user['user_name']}")
                try:
                    await users_collection.update_one(
                        {"user_name": user["user_name"]},
                        update_operations,
                        upsert=True
                    )
                    print(f"[DEBUG] Database update successful")
                except Exception as db_error:
                    print(f"[ERROR] Database update failed: {db_error}")
                    print(f"[ERROR] Update operations were: {update_operations}")
                    raise

                # Fetch the user again to get the updated highest_passed_level
                user_data = await users_collection.find_one({"user_name": user["user_name"]})
                highest_passed_level = user_data.get("highest_passed_level", 0)
                
                print(f"User {user['user_name']} highest_passed_level is now: {highest_passed_level}")

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
    
    async def get_user_progress(self, user: dict):
        """
        Get user's current level and progress information.
        
        Args:
            user: Dictionary containing user information (user_name)
            
        Returns:
            Dictionary with user progress including highest passed level and level details
        """
        try:
            db = get_database()
            users_collection = db["users"]
            
            user_name = user.get("user_name")
            user_doc = await users_collection.find_one({"user_name": user_name})
            
            if not user_doc:
                # Return default progress for new user - only level 1 is unlocked
                return {
                    "highest_passed_level": 0,
                    "levels": [
                        {
                            "level": i,
                            "is_locked": i > 1,
                            "is_passed": False,
                            "status": "locked" if i > 1 else "available",
                            "attempts": 0,
                            "best_score": 0,
                            "total_questions": 0
                        }
                        for i in range(1, 7)  # 6 shape game levels only
                    ]
                }
            
            # Get user's level progress
            level_progress = user_doc.get("level_progress", {})
            highest_passed = user_doc.get("highest_passed_level", 0)
            
            print(f"get_user_progress for {user_name}: highest_passed_level={highest_passed}")
            print(f"Level progress data: {level_progress}")
            
            # Build level info for 6 shape game levels
            levels_info = []
            
            for level_num in range(1, 7):
                level_data = level_progress.get(str(level_num), {})
                level_status = level_data.get("status", "fail")
                level_passed = level_status == "pass"
                
                # Count attempts from attempt_history
                attempt_history = level_data.get("attempt_history", [])
                attempts = len(attempt_history)
                
                # Get best score from attempt history
                best_score = 0
                total_questions = 0
                if attempt_history:
                    best_score = max(a.get("score", 0) for a in attempt_history)
                    total_questions = attempt_history[-1].get("total_questions", 0) if attempt_history else 0
                
                # Determine if level is locked
                # Level 1 is always unlocked
                # Other levels require the previous level to be passed
                is_locked = level_num > 1 and highest_passed < (level_num - 1)
                
                print(f"Level {level_num}: passed={level_passed}, locked={is_locked}, status={level_status}")
                
                levels_info.append({
                    "level": level_num,
                    "is_locked": is_locked,
                    "is_passed": level_passed,
                    "status": "passed" if level_passed else ("locked" if is_locked else "available"),
                    "attempts": attempts,
                    "best_score": best_score,
                    "total_questions": total_questions
                })
            
            return {
                "highest_passed_level": highest_passed,
                "levels": levels_info
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching user progress: {str(e)}")
    
    async def get_build_match_progress(self, user: dict):
        """
        Get user's Build & Match challenge progress.
        
        Args:
            user: Dictionary containing user information (user_name)
            
        Returns:
            Dictionary with build challenge progress including highest completed challenge
        """
        try:
            db = get_database()
            users_collection = db["users"]
            
            user_name = user.get("user_name")
            user_doc = await users_collection.find_one({"user_name": user_name})
            
            if not user_doc:
                # Return default progress for new user - only challenge 1 is unlocked
                return {
                    "highest_build_challenge": 0,
                    "challenges": [
                        {
                            "challenge": i,
                            "is_locked": i > 1,
                            "is_passed": False,
                            "status": "locked" if i > 1 else "available",
                            "attempts": 0
                        }
                        for i in range(1, 8)  # 7 build challenges
                    ]
                }
            
            # Get user's build match progress
            build_progress = user_doc.get("build_match_progress", {})
            highest_build = user_doc.get("highest_build_challenge", 0)
            
            print(f"get_build_match_progress for {user_name}: highest_build_challenge={highest_build}")
            print(f"Build match progress data: {build_progress}")
            
            # Build challenge info for all 7 challenges
            challenges_info = []
            
            for challenge_num in range(1, 8):
                challenge_data = build_progress.get(str(challenge_num), {})
                challenge_status = challenge_data.get("status", "fail")
                challenge_passed = challenge_status == "pass"
                
                # Count attempts from attempt_history
                attempt_history = challenge_data.get("attempt_history", [])
                attempts = len(attempt_history)
                
                # Determine if challenge is locked
                # Challenge 1 is always unlocked
                # Other challenges require the previous challenge to be completed
                is_locked = challenge_num > 1 and highest_build < (challenge_num - 1)
                
                print(f"Build Challenge {challenge_num}: passed={challenge_passed}, locked={is_locked}, status={challenge_status}")
                
                challenges_info.append({
                    "challenge": challenge_num,
                    "is_locked": is_locked,
                    "is_passed": challenge_passed,
                    "status": "passed" if challenge_passed else ("locked" if is_locked else "available"),
                    "attempts": attempts
                })
            
            return {
                "highest_build_challenge": highest_build,
                "challenges": challenges_info
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching build match progress: {str(e)}")