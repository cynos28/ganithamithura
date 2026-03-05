"""
Adaptive-games REST endpoints
==============================

Prefix : /adaptive-games
Used by : Flutter GamesApiService

Endpoints
---------
GET  /parameters/{domain}         — fetch current game params (+ IRT state if student_id given)
POST /evaluate                    — legacy: full-session evaluation (rule-based)
POST /round-result                — NEW: per-round IRT update for L-V4
GET  /irt-state/{student_id}      — fetch the full IRT session for a student+variant
GET  /irt-stats/{student_id}      — aggregated analytics from round history
DELETE /reset-progress/{student_id} — reset student IRT progress for a domain+variant
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.models.games import GameParameters, GameSession
from app.services.irt_engine import (
    evaluate_round,
    RoundOutcome,
    theta_to_level,
    bridge_config_to_params,
    config_to_params,
    compute_session_stats,
)
from app.utils.game_rules import diagnose_performance

router = APIRouter(prefix="/adaptive-games", tags=["Adaptive Games"])


# ─── request / response schemas ─────────────────────────────────────────────

class EvaluateRequest(BaseModel):
    """Legacy full-session evaluation."""
    user_id: str
    domain: str
    attempts: int
    time: float
    target_time: float
    hints: int


class RoundResultRequest(BaseModel):
    """Per-round IRT evaluation for Build-a-Bridge (L-V4)."""
    student_id: str
    domain: str = "length"
    variant: str = "L-V4"
    correct: bool
    attempts: int = Field(ge=1)
    hints_used: int = Field(ge=0, default=0)
    time_seconds: float = Field(ge=0, default=0.0)
    stars_earned: int = Field(ge=0, le=3, default=0)


class RoundResultResponse(BaseModel):
    theta: float
    difficulty_level: int
    p_expected: float
    next_params: Dict[str, Any]
    rounds_played: int


class IRTStateResponse(BaseModel):
    student_id: str
    domain: str
    variant: str
    theta: float
    difficulty_level: int
    rounds_played: int
    total_correct: int
    total_attempts: int
    total_hints: int
    total_stars: int
    next_params: Dict[str, Any]


class IRTStatsResponse(BaseModel):
    student_id: str
    variant: str
    total_rounds: int
    accuracy: float
    avg_attempts: float
    avg_time: float
    theta_trend: List[float]
    difficulty_trend: List[int]


# ─── GET /parameters/{domain} ───────────────────────────────────────────────

@router.get("/parameters/{domain}")
async def get_parameters(
    domain: str,
    student_id: Optional[str] = Query(None, description="If provided, merge IRT-adapted L-V4 params"),
    variant: Optional[str] = Query(None, description="Game variant (e.g. L-V4)"),
):
    """
    Return game parameters for a domain.

    If *student_id* and *variant* are supplied **and** an IRT session
    exists for that student, the L-V4-specific keys are overridden with
    IRT-adapted values.
    """
    doc = await GameParameters.find_one(GameParameters.domain == domain)
    if not doc:
        raise HTTPException(404, f"No parameters found for domain '{domain}'")

    params = dict(doc.params)  # shallow copy

    # Merge IRT-adapted params when a student session exists
    if student_id and variant:
        session = await GameSession.find_one(
            GameSession.student_id == student_id,
            GameSession.domain == domain,
            GameSession.variant == variant,
        )
        if session:
            irt_params = config_to_params(domain, variant, session.difficulty_level)
            params.update(irt_params)
            params["_irt"] = {
                "theta": round(session.theta, 3),
                "difficulty_level": session.difficulty_level,
                "rounds_played": session.rounds_played,
            }

    return params


# ─── POST /evaluate  (legacy — full-session, rule-based) ────────────────────

@router.post("/evaluate")
async def evaluate_session(req: EvaluateRequest):
    """
    Legacy endpoint: diagnose full session → increase / decrease / maintain.
    Still used by non-IRT variants (L-V1).
    """
    diagnosis = diagnose_performance(
        attempts=req.attempts,
        time_spent=req.time,
        target_time=req.target_time,
        hints_used=req.hints,
    )

    # Persist updated params if we should adjust difficulty globally
    doc = await GameParameters.find_one(GameParameters.domain == req.domain)
    new_params = dict(doc.params) if doc else {}

    if diagnosis == "increase":
        _nudge_params(new_params, direction=1)
    elif diagnosis == "decrease":
        _nudge_params(new_params, direction=-1)

    if doc:
        doc.params = new_params
        doc.updated_at = datetime.utcnow()
        await doc.save()

    return {"diagnosis": diagnosis, "new_params": new_params}


def _nudge_params(params: dict, direction: int):
    """Simple rule-based adjustment for non-IRT domains."""
    rng = params.get("bridge_target_range")
    if rng and len(rng) == 2:
        params["bridge_target_range"] = [
            max(6, rng[0] + 2 * direction),
            max(10, rng[1] + 2 * direction),
        ]
    pc = params.get("plank_count")
    if pc:
        params["plank_count"] = max(4, min(10, pc + direction))


# ─── POST /round-result  (IRT per-round) ────────────────────────────────────

@router.post("/round-result", response_model=RoundResultResponse)
async def post_round_result(req: RoundResultRequest):
    """
    Receive the outcome of one Build-a-Bridge round, update the student's
    IRT ability θ, and return the next-round difficulty parameters.
    """
    # 1. Find or create the student's IRT session
    session = await GameSession.find_one(
        GameSession.student_id == req.student_id,
        GameSession.domain == req.domain,
        GameSession.variant == req.variant,
    )
    if session is None:
        session = GameSession(
            student_id=req.student_id,
            domain=req.domain,
            variant=req.variant,
        )
        await session.insert()

    # 2. Run IRT evaluation
    outcome = RoundOutcome(
        correct=req.correct,
        attempts=req.attempts,
        hints_used=req.hints_used,
        time_seconds=req.time_seconds,
    )
    result = evaluate_round(
        theta=session.theta,
        difficulty_level=session.difficulty_level,
        round_outcome=outcome,
        rounds_played=session.rounds_played,
        domain=req.domain,
        variant=req.variant,
    )

    # 3. Persist updated state
    session.theta = result.theta_after
    session.difficulty_level = result.difficulty_level
    session.rounds_played += 1
    session.total_attempts += req.attempts
    session.total_hints += req.hints_used
    session.total_stars += req.stars_earned
    if req.correct:
        session.total_correct += 1

    # Append to round history (keep last 20)
    session.round_history.append({
        "correct": req.correct,
        "attempts": req.attempts,
        "hints": req.hints_used,
        "time_s": req.time_seconds,
        "stars": req.stars_earned,
        "beta": result.beta,
        "theta_after": round(result.theta_after, 4),
        "p_expected": round(result.p_expected, 4),
        "timestamp": datetime.utcnow().isoformat(),
    })
    if len(session.round_history) > 20:
        session.round_history = session.round_history[-20:]

    session.updated_at = datetime.utcnow()
    await session.save()

    return RoundResultResponse(
        theta=round(result.theta_after, 4),
        difficulty_level=result.difficulty_level,
        p_expected=round(result.p_expected, 4),
        next_params=result.next_params,
        rounds_played=session.rounds_played,
    )


# ─── GET /irt-state/{student_id} ────────────────────────────────────────────

@router.get("/irt-state/{student_id}", response_model=IRTStateResponse)
async def get_irt_state(
    student_id: str,
    domain: str = Query("length"),
    variant: str = Query("L-V4"),
):
    """Return the full IRT session state for a student."""
    session = await GameSession.find_one(
        GameSession.student_id == student_id,
        GameSession.domain == domain,
        GameSession.variant == variant,
    )
    if not session:
        # Return defaults for new student
        default_params = config_to_params(domain, variant, 1)
        return IRTStateResponse(
            student_id=student_id,
            domain=domain,
            variant=variant,
            theta=0.0,
            difficulty_level=1,
            rounds_played=0,
            total_correct=0,
            total_attempts=0,
            total_hints=0,
            total_stars=0,
            next_params=default_params,
        )

    return IRTStateResponse(
        student_id=session.student_id,
        domain=session.domain,
        variant=session.variant,
        theta=round(session.theta, 4),
        difficulty_level=session.difficulty_level,
        rounds_played=session.rounds_played,
        total_correct=session.total_correct,
        total_attempts=session.total_attempts,
        total_hints=session.total_hints,
        total_stars=session.total_stars,
        next_params=config_to_params(session.domain, session.variant, session.difficulty_level),
    )


# ─── GET /irt-stats/{student_id} ────────────────────────────────────────────

@router.get("/irt-stats/{student_id}", response_model=IRTStatsResponse)
async def get_irt_stats(
    student_id: str,
    domain: str = Query("length"),
    variant: str = Query("L-V4"),
):
    """Aggregated analytics (accuracy, θ trend, difficulty trend)."""
    session = await GameSession.find_one(
        GameSession.student_id == student_id,
        GameSession.domain == domain,
        GameSession.variant == variant,
    )
    if not session:
        return IRTStatsResponse(
            student_id=student_id,
            variant=variant,
            total_rounds=0,
            accuracy=0.0,
            avg_attempts=0.0,
            avg_time=0.0,
            theta_trend=[],
            difficulty_trend=[],
        )

    stats = compute_session_stats(session.round_history)

    return IRTStatsResponse(
        student_id=student_id,
        variant=variant,
        total_rounds=stats["total_rounds"],
        accuracy=round(stats["accuracy"], 3),
        avg_attempts=stats["avg_attempts"],
        avg_time=stats["avg_time"],
        theta_trend=stats["theta_trend"],
        difficulty_trend=stats["difficulty_trend"],
    )


# ─── DELETE /reset-progress/{student_id} ────────────────────────────────────

@router.delete("/reset-progress/{student_id}")
async def reset_student_progress(
    student_id: str,
    domain: str = Query("length", description="Domain to reset (length/area/volume/weight)"),
    variant: Optional[str] = Query(None, description="Specific variant to reset (e.g. L-V4). If omitted, resets all variants for the domain."),
):
    """
    Reset a student's IRT progress for a specific domain and variant.
    
    This will:
    - Delete the GameSession document(s)
    - Student will start fresh with theta=0.0, difficulty_level=1
    
    Examples:
    - DELETE /reset-progress/student_001?domain=length&variant=L-V4  → Reset only L-V4
    - DELETE /reset-progress/student_001?domain=area                 → Reset all area variants
    """
    if variant:
        # Reset specific variant
        session = await GameSession.find_one(
            GameSession.student_id == student_id,
            GameSession.domain == domain,
            GameSession.variant == variant,
        )
        if session:
            await session.delete()
            return {
                "status": "success",
                "message": f"Reset progress for {student_id} in {domain}/{variant}",
                "deleted": 1,
            }
        else:
            return {
                "status": "info",
                "message": f"No progress found for {student_id} in {domain}/{variant}",
                "deleted": 0,
            }
    else:
        # Reset all variants for the domain
        sessions = await GameSession.find(
            GameSession.student_id == student_id,
            GameSession.domain == domain,
        ).to_list()
        count = len(sessions)
        for session in sessions:
            await session.delete()
        return {
            "status": "success",
            "message": f"Reset all {count} variant(s) for {student_id} in domain '{domain}'",
            "deleted": count,
        }
