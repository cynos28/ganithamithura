"""
Game domain models — GameParameters (per-domain config) & GameSession
(per-student IRT session tracking for the Build-a-Bridge adaptive engine).

IRT (Item Response Theory) — Simplified 1PL Rasch Model
========================================================
We model each student with a single latent ability θ and each item
(round) with a difficulty β.  The probability of a correct response is:

    P(correct | θ, β) = 1 / (1 + exp(−(θ − β)))

After every round we update θ with a lightweight online rule:

    θ_new = θ_old + α × (outcome − P_expected)

where α is a learning rate and outcome ∈ {0, 1}.
"""

from beanie import Document, Indexed
from pydantic import Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ─────────────────────────────────────────────────────────────────────────────
# GAME PARAMETERS  — one document per domain (length / area / volume / weight)
# ─────────────────────────────────────────────────────────────────────────────

class GameParameters(Document):
    """Stores domain-level game configuration (shared by all students)."""
    domain: Indexed(str, unique=True)  # "length", "area", …
    params: Dict[str, Any] = Field(default_factory=dict)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "game_parameters"
        indexes = ["domain"]


# ─────────────────────────────────────────────────────────────────────────────
# GAME SESSION — one per (student × domain × variant) for IRT tracking
# ─────────────────────────────────────────────────────────────────────────────

class GameSession(Document):
    """
    Persistent IRT state for a single student playing a specific game variant.

    Fields
    ------
    theta : float
        Current estimated ability on the logit scale (default 0.0 = average).
    difficulty_level : int
        Discrete difficulty band 1-5 mapped from θ for parameter selection.
    rounds_played : int
        Total rounds completed across all play sessions.
    round_history : list[dict]
        Last N round outcomes used for short-term trend analysis.
    """
    student_id: Indexed(str)
    domain: str = "length"        # e.g. "length"
    variant: str = "L-V4"         # e.g. "L-V4"

    # ── IRT state ──
    theta: float = Field(default=0.0, description="IRT ability estimate (logit scale)")
    difficulty_level: int = Field(default=1, ge=1, le=5, description="Current difficulty band")

    # ── Aggregates ──
    rounds_played: int = Field(default=0)
    total_correct: int = Field(default=0)
    total_attempts: int = Field(default=0)
    total_hints: int = Field(default=0)
    total_stars: int = Field(default=0)

    # ── History (last 20 rounds) ──
    round_history: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Recent round outcomes [{correct, attempts, hints, time_s, beta, theta_after}]",
    )

    # ── Timestamps ──
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "game_sessions"
        indexes = [
            "student_id",
            "domain",
            "variant",
            [("student_id", 1), ("domain", 1), ("variant", 1)],
        ]
