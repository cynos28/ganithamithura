"""
Adaptive Engine — IRT-based ability tracking for contextual questions.

Used by routes/contextual.py to select question difficulty and update
student ability after each answer.

This is the *question-level* adaptive engine (as opposed to the
game-level IRT in services/irt_engine.py which handles Build-a-Bridge rounds).
"""

import math
from app.config import settings
from app.models.database import StudentAbilityModel


def _sigmoid(x: float) -> float:
    x = max(-10.0, min(10.0, x))
    return 1.0 / (1.0 + math.exp(-x))


class AdaptiveEngine:
    """
    Simplified 1PL IRT engine for adaptive question selection.

    • get_student_state  — fetch or create StudentAbilityModel
    • select_optimal_difficulty — pick the difficulty band where the student
      has roughly a `target_success_rate` chance of answering correctly
    • update_ability — online θ update after an answer
    """

    def __init__(
        self,
        learning_rate: float = 0.3,
        target_success_rate: float = 0.7,
        min_difficulty: int = 1,
        max_difficulty: int = 5,
    ):
        self.learning_rate = learning_rate
        self.target_success_rate = target_success_rate
        self.min_difficulty = min_difficulty
        self.max_difficulty = max_difficulty

    # ── student state ────────────────────────────────────────────────────

    async def get_student_state(
        self,
        student_id: str,
        unit_id: str,
        grade_level: int = 1,
    ) -> StudentAbilityModel:
        """Return existing StudentAbilityModel or create a fresh one."""
        ability = await StudentAbilityModel.find_one(
            StudentAbilityModel.student_id == student_id,
            StudentAbilityModel.unit_id == unit_id,
        )
        if ability is None:
            ability = StudentAbilityModel(
                student_id=student_id,
                unit_id=unit_id,
                current_difficulty=self._grade_to_start_difficulty(grade_level),
                ability_score=0.0,
            )
            await ability.insert()
        return ability

    # ── difficulty selection ─────────────────────────────────────────────

    def select_optimal_difficulty(
        self,
        ability_score: float,
        grade_level: int = 1,
    ) -> int:
        """
        Pick the discrete difficulty level (1-5) where the student has
        approximately `target_success_rate` probability of success.

        Uses the 1PL model:  P = σ(θ − β)
        We want P ≈ target_success_rate, so:
            β_target = θ − ln(P / (1 − P))
        Then we map β_target onto 1-5.
        """
        # β that would give target success rate
        p = self.target_success_rate
        beta_target = ability_score - math.log(p / (1.0 - p))

        # Map β → difficulty level (β roughly in [-2, 2] → levels 1-5)
        level = round((beta_target + 2.0) * (4.0 / 4.0)) + 1
        level = max(self.min_difficulty, min(self.max_difficulty, level))

        # Clamp by grade (grade 1 shouldn't see level 5)
        max_for_grade = min(self.max_difficulty, grade_level + 2)
        level = min(level, max_for_grade)

        return level

    # ── ability update ───────────────────────────────────────────────────

    def update_ability(
        self,
        current_ability: float,
        is_correct: bool,
        question_difficulty: int,
    ) -> float:
        """
        Online IRT update of θ after one answer.

            θ_new = θ + α × (outcome − P_expected)

        Returns the new ability score.
        """
        # Map discrete level → continuous β (centred around 0)
        beta = (question_difficulty - 3) * 0.8  # level 1→-1.6, 3→0, 5→1.6

        outcome = 1.0 if is_correct else 0.0
        p_expected = _sigmoid(current_ability - beta)

        new_ability = current_ability + self.learning_rate * (outcome - p_expected)
        # Clamp to sane range
        return max(-3.0, min(3.0, new_ability))

    # ── helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _grade_to_start_difficulty(grade: int) -> int:
        """Map kindergarten grade (1-5) to a reasonable starting difficulty."""
        return max(1, min(3, grade))


# ── module-level singleton ───────────────────────────────────────────────────
adaptive_engine = AdaptiveEngine(
    learning_rate=settings.learning_rate,
    target_success_rate=settings.target_success_rate,
    min_difficulty=settings.min_difficulty,
    max_difficulty=settings.max_difficulty,
)
