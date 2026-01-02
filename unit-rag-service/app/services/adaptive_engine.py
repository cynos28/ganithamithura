import numpy as np
from typing import List, Dict, Any, Optional
from app.models.database import StudentAbilityModel, StudentAnswerModel, QuestionModel
from app.config import settings
from beanie.operators import In, NotIn
from bson import ObjectId


class AdaptiveEngine:
    """
    Adaptive question selection using Item Response Theory (IRT)
    Implements 1-Parameter Logistic Model (Rasch Model)
    """
    
    def __init__(self):
        self.learning_rate = settings.learning_rate
        self.target_success_rate = settings.target_success_rate
        self.min_difficulty = settings.min_difficulty
        self.max_difficulty = settings.max_difficulty
    
    def probability_correct(self, ability: float, difficulty: float) -> float:
        """
        Calculate probability of correct answer using IRT
        P(correct) = 1 / (1 + exp(-(ability - difficulty)))
        """
        return 1.0 / (1.0 + np.exp(-(ability - difficulty)))
    
    def update_ability(
        self,
        current_ability: float,
        is_correct: bool,
        question_difficulty: float
    ) -> float:
        """
        Update student ability based on answer correctness
        Uses Maximum Likelihood Estimation
        """
        prob = self.probability_correct(current_ability, question_difficulty)
        
        if is_correct:
            # Increase ability based on how surprising the success was
            delta = self.learning_rate * (1 - prob)
        else:
            # Decrease ability based on how surprising the failure was
            delta = -self.learning_rate * prob
        
        new_ability = current_ability + delta
        
        # Clamp to reasonable range
        return max(-3.0, min(3.0, new_ability))
    
    def select_optimal_difficulty(self, ability: float, grade_level: int = 1) -> int:
        """
        Select optimal question difficulty for target success rate
        
        Grade-aware difficulty calculation:
        - Grade 1: Start at difficulty 1 (very easy)
        - Grade 2: Start at difficulty 2 (easy)
        - Grade 3: Start at difficulty 3 (medium)
        - Grade 4: Start at difficulty 4 (hard)
        
        Then adjust based on student's ability score
        """
        # Clamp grade to valid range [1, 4]
        grade = max(1, min(4, grade_level))
        
        # Calculate difficulty: base on grade, adjust by ability
        # When ability = 0, difficulty matches grade level
        # Ability range [-3, 3] allows ±3 level adjustment
        raw_difficulty = float(grade) + ability
        difficulty_level = int(np.round(raw_difficulty))
        
        # Clamp to valid range [1, 5]
        clamped = max(self.min_difficulty, min(self.max_difficulty, difficulty_level))
        
        print(f"🎚️ Difficulty calc: grade={grade} + ability={ability:.2f} = {raw_difficulty:.2f} → {clamped}")
        
        return clamped
    
    async def get_student_state(
        self,
        student_id: str,
        unit_id: str,
        grade_level: int = 1
    ) -> StudentAbilityModel:
        """Get or create student ability state"""
        
        student_ability = await StudentAbilityModel.find_one(
            StudentAbilityModel.student_id == student_id,
            StudentAbilityModel.unit_id == unit_id
        )
        
        if not student_ability:
            # Create new student record with grade-appropriate starting difficulty
            # Grade 1 → difficulty 1, Grade 2 → difficulty 2, etc.
            grade = max(1, min(4, grade_level))
            
            student_ability = StudentAbilityModel(
                student_id=student_id,
                unit_id=unit_id,
                ability_score=settings.initial_ability_score,  # Start at 0.0
                current_difficulty=grade,  # Start at grade level
                concepts_mastered={}
            )
            await student_ability.insert()
        
        return student_ability
    
    async def get_next_question(
        self,
        student_id: str,
        unit_id: str,
        grade_level: Optional[int] = None
    ) -> Optional[QuestionModel]:
        """
        Select next question using adaptive algorithm
        
        Algorithm:
        1. Get student's current ability
        2. Calculate optimal difficulty
        3. Identify weak concepts
        4. Find unanswered question matching criteria
        """
        
        # Default to grade 1 if not specified
        grade = grade_level if grade_level is not None else 1
        
        # Get student state (creates new record with grade-appropriate difficulty)
        student_ability = await self.get_student_state(student_id, unit_id, grade)
        
        # Calculate optimal difficulty (grade-aware)
        target_difficulty = self.select_optimal_difficulty(student_ability.ability_score, grade)
        
        print(f"📊 Adaptive selection for student={student_id}, unit={unit_id}, grade={grade}")
        print(f"   Ability: {student_ability.ability_score:.2f}, Target difficulty: {target_difficulty}")
        
        # Get answered question IDs
        answered = await StudentAnswerModel.find(
            StudentAnswerModel.student_id == student_id,
            StudentAnswerModel.unit_id == unit_id
        ).to_list()
        # question_id in answers is stored as string, need to convert to ObjectId for comparison
        answered_ids = []
        for ans in answered:
            try:
                answered_ids.append(ObjectId(ans.question_id))
            except:
                # If it's already an ObjectId or invalid, skip
                pass
        
        # Check total questions available for this unit
        total_questions = await QuestionModel.find(
            QuestionModel.unit_id == unit_id
        ).count()
        
        print(f"   📚 Total questions for unit '{unit_id}': {total_questions}")
        print(f"   ✅ Already answered: {len(answered_ids)} questions")
        if answered_ids:
            print(f"   🔍 Answered IDs (first 3): {[str(id) for id in answered_ids[:3]]}")
        print(f"   🆕 Remaining: {total_questions - len(answered_ids)} questions")
        
        # Identify weak concepts (mastery < 0.5)
        weak_concepts = [
            concept for concept, mastery 
            in (student_ability.concepts_mastered or {}).items() 
            if mastery < 0.5
        ]
        
        print(f"   🚫 Excluding {len(answered_ids)} answered questions")
        
        # Priority 1: Questions on weak concepts at target difficulty
        if weak_concepts:
            if answered_ids:
                question = await QuestionModel.find_one(
                    QuestionModel.unit_id == unit_id,
                    QuestionModel.grade_level == grade,
                    QuestionModel.difficulty_level == target_difficulty,
                    In(QuestionModel.question_type, ["mcq", "true_false"]),
                    NotIn(QuestionModel.id, answered_ids),
                    {"concepts": {"$in": weak_concepts}}
                )
            else:
                question = await QuestionModel.find_one(
                    QuestionModel.unit_id == unit_id,
                    QuestionModel.grade_level == grade,
                    QuestionModel.difficulty_level == target_difficulty,
                    In(QuestionModel.question_type, ["mcq", "true_false"]),
                    {"concepts": {"$in": weak_concepts}}
                )
            
            if question:
                print(f"   ✅ Selected (weak concept): {str(question.id)[:12]}... (difficulty {question.difficulty_level})")
                print(f"   📝 Question: {question.question_text[:60]}...")
                return question
        
        # Priority 2: Any question at target difficulty for this unit
        if answered_ids:
            question = await QuestionModel.find_one(
                QuestionModel.unit_id == unit_id,
                QuestionModel.grade_level == grade,
                QuestionModel.difficulty_level == target_difficulty,
                In(QuestionModel.question_type, ["mcq", "true_false"]),
                NotIn(QuestionModel.id, answered_ids)
            )
        else:
            question = await QuestionModel.find_one(
                QuestionModel.unit_id == unit_id,
                QuestionModel.grade_level == grade,
                QuestionModel.difficulty_level == target_difficulty,
                In(QuestionModel.question_type, ["mcq", "true_false"])
            )
        
        if question:
            print(f"   ✅ Selected question ID: {str(question.id)[:12]}... (difficulty {question.difficulty_level})")
            print(f"   📝 Question preview: {question.question_text[:60]}...")
            return question
        
        # Priority 3: Question at adjacent difficulty for this unit
        for diff_offset in [1, -1, 2, -2]:
            adj_difficulty = target_difficulty + diff_offset
            if self.min_difficulty <= adj_difficulty <= self.max_difficulty:
                if answered_ids:
                    question = await QuestionModel.find_one(
                        QuestionModel.unit_id == unit_id,
                        QuestionModel.grade_level == grade,
                        QuestionModel.difficulty_level == adj_difficulty,
                        In(QuestionModel.question_type, ["mcq", "true_false"]),
                        NotIn(QuestionModel.id, answered_ids)
                    )
                else:
                    question = await QuestionModel.find_one(
                        QuestionModel.unit_id == unit_id,
                        QuestionModel.grade_level == grade,
                        QuestionModel.difficulty_level == adj_difficulty,
                        In(QuestionModel.question_type, ["mcq", "true_false"])
                    )
                
                if question:
                    print(f"   ✅ Selected (adjacent diff {adj_difficulty}): {str(question.id)[:12]}... ")
                    print(f"   📝 Question: {question.question_text[:60]}...")
                    return question
        
        # Fallback: Any unanswered MCQ/true_false question
        if answered_ids:
            fallback = await QuestionModel.find_one(
                In(QuestionModel.question_type, ["mcq", "true_false"]),
                NotIn(QuestionModel.id, answered_ids)
            )
        else:
            fallback = await QuestionModel.find_one(
                In(QuestionModel.question_type, ["mcq", "true_false"])
            )
        
        if fallback:
            print(f"⚠️  Using fallback question (difficulty {fallback.difficulty_level}, type: {fallback.question_type}) - no match at target {target_difficulty}")
        else:
            print(f"❌ NO MCQ/TRUE_FALSE QUESTIONS FOUND! Please generate questions from admin dashboard.")
            print(f"   Total questions in DB: {total_questions}")
            print(f"   Already answered: {len(answered_ids)}")
        
        return fallback
    
    async def process_answer(
        self,
        student_id: str,
        question: QuestionModel,
        unit_id: str,
        is_correct: bool,
        time_taken: int,
        grade_level: int = 1
    ) -> Dict[str, Any]:
        """
        Process student answer and update ability
        
        Returns feedback and updated state
        """
        
        # Get student state (grade-aware)
        student_ability = await self.get_student_state(student_id, unit_id, grade_level)
        
        # Update ability score
        new_ability = self.update_ability(
            student_ability.ability_score,
            is_correct,
            question.difficulty_level
        )
        
        # Update concept mastery
        concepts_mastered = student_ability.concepts_mastered or {}
        for concept in (question.concepts or []):
            current_mastery = concepts_mastered.get(concept, 0.5)
            
            # Update mastery (exponential moving average)
            if is_correct:
                new_mastery = current_mastery + 0.1 * (1 - current_mastery)
            else:
                new_mastery = current_mastery - 0.1 * current_mastery
            
            concepts_mastered[concept] = round(new_mastery, 3)
        
        # Update student record (grade-aware difficulty)
        student_ability.ability_score = new_ability
        student_ability.current_difficulty = self.select_optimal_difficulty(new_ability, grade_level)
        student_ability.concepts_mastered = concepts_mastered
        student_ability.total_questions += 1
        if is_correct:
            student_ability.correct_answers += 1
        
        await student_ability.save()
        
        # Record answer
        answer_record = StudentAnswerModel(
            student_id=student_id,
            question_id=str(question.id),
            unit_id=unit_id,  # Use the correct unit_id from submission
            answer_given="",  # Will be filled by caller
            is_correct=is_correct,
            time_taken=time_taken,
            difficulty_at_attempt=question.difficulty_level
        )
        
        await answer_record.insert()
        
        # Calculate mastery level (overall accuracy)
        mastery_level = (
            student_ability.correct_answers / student_ability.total_questions
            if student_ability.total_questions > 0 else 0.0
        )
        
        # Identify concepts to review
        concepts_to_review = [
            concept for concept, mastery 
            in concepts_mastered.items() 
            if mastery < 0.6
        ]
        
        return {
            "ability_score": new_ability,
            "next_difficulty": student_ability.current_difficulty,
            "mastery_level": mastery_level,
            "concepts_to_review": concepts_to_review,
            "probability_next": self.probability_correct(
                new_ability,
                student_ability.current_difficulty
            )
        }
    
    async def calculate_analytics(
        self,
        student_id: str,
        unit_id: str
    ) -> Dict[str, Any]:
        """Calculate student analytics and learning metrics"""
        
        student_ability = await StudentAbilityModel.find_one(
            StudentAbilityModel.student_id == student_id,
            StudentAbilityModel.unit_id == unit_id
        )
        
        if not student_ability:
            return {}
        
        # Get all answers
        answers = await StudentAnswerModel.find(
            StudentAnswerModel.student_id == student_id,
            StudentAnswerModel.unit_id == unit_id
        ).sort("answered_at").to_list()
        
        if not answers:
            return {}
        
        # Calculate metrics
        total_time = sum(a.time_taken for a in answers)
        accuracy = student_ability.correct_answers / len(answers)
        avg_difficulty = np.mean([a.difficulty_at_attempt for a in answers])
        
        # Learning velocity (improvement rate)
        if len(answers) >= 5:
            recent_accuracy = sum(
                1 for a in answers[-5:] if a.is_correct
            ) / 5
            early_accuracy = sum(
                1 for a in answers[:5] if a.is_correct
            ) / 5
            learning_velocity = recent_accuracy - early_accuracy
        else:
            learning_velocity = 0.0
        
        # Strong and weak concepts
        concepts = student_ability.concepts_mastered or {}
        strong_concepts = [c for c, m in concepts.items() if m >= 0.7]
        weak_concepts = [c for c, m in concepts.items() if m < 0.5]
        
        return {
            "total_time_spent": total_time,
            "questions_attempted": len(answers),
            "accuracy_rate": accuracy,
            "average_difficulty": avg_difficulty,
            "strong_concepts": strong_concepts,
            "weak_concepts": weak_concepts,
            "learning_velocity": learning_velocity,
            "recommended_difficulty": student_ability.current_difficulty,
            "ability_score": student_ability.ability_score
        }


# Singleton instance
adaptive_engine = AdaptiveEngine()
