from fastapi import APIRouter
from app.services.adaptive_game_service import evaluate_session
from app.models.games import GameParameters

router = APIRouter(prefix="/adaptive-games", tags=["Adaptive Measurement Games"])


@router.post("/evaluate")
async def evaluate(payload: dict):
    """Evaluates one AR measurement game attempt."""
    return await evaluate_session(payload)


@router.get("/parameters/{domain}")
async def get_params(domain: str):
    doc = await GameParameters.find_one(GameParameters.domain == domain)
    if not doc:
        return {"error": "Domain not found"}
    return doc.params
