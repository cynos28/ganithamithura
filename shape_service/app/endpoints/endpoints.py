from fastapi import APIRouter, UploadFile, File, Request, Depends
from app.controllers.shapes_detection import ShapesDetectionController
from app.controllers.shapes_controller import ShapesController
from app.controllers.game_controller import GameController
from app.controllers.report_controller import ReportController
from app.models.model import GameAnswer, UserBadgeList
import os
from jose import jwt, JWTError

SECRET_KEY = os.getenv("SECRET_KEY", "your_super_secret_key_here")
ALGORITHM = "HS256"

# If MOCK_USER_NAME is set in .env, the service runs in mock mode —
# JWT auth is bypassed entirely and all requests use the mock identity.
_MOCK_USER_NAME = os.getenv("MOCK_USER_NAME", "").strip()
_MOCK_MODE = bool(_MOCK_USER_NAME)


def get_current_user_from_request(request: Request) -> dict:
    """
    Resolve the current user from the incoming request.

    Two modes:
    1. Mock mode  — MOCK_USER_NAME is set in .env.
       JWT is ignored. All requests use the mock identity.
       Useful for local development / testing without a real auth flow.

    2. JWT mode   — MOCK_USER_NAME is NOT set in .env.
       Reads the Authorization: Bearer <token> header, decodes the JWT,
       and extracts the user's email as the user_name.
       Returns HTTP 401 if the token is missing or invalid.
    """
    if _MOCK_MODE:
        return {"user_name": _MOCK_USER_NAME}

    # JWT mode — token is required
    from fastapi import HTTPException
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token required")

    token = auth_header[len("Bearer "):]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub", "")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token payload")
        return {"user_name": email}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


router = APIRouter()

shapes_detection_controller = ShapesDetectionController()
shapes_controller = ShapesController()
game_controller = GameController()
report_controller = ReportController()


@router.get("/")
async def health():
    return {"status": "healthy", "service": "shapes"}


@router.post("/detect-shape/")
async def detect_shape(request: Request, image_file: UploadFile = File(None)):
    return await shapes_detection_controller.detect_shape(request, image_file)


@router.get("/shapes/")
async def get_shapes():
    return await shapes_controller.get_shapes()


@router.get("/shapes/type/{shape_type}")
async def get_shapes_by_type(shape_type: str):
    return await shapes_controller.get_shapes_by_type(shape_type)


@router.get("/shapes/id/{shape_id}")
async def get_shape_by_id(shape_id: str):
    return await shapes_controller.get_shape_by_id(shape_id)


@router.get("/shapes/name/{shape_name}")
async def get_shape_by_name(shape_name: str):
    return await shapes_controller.get_shape_by_name(shape_name)


@router.get("/images/{image_id}")
async def get_image_by_id(image_id: str):
    return await shapes_controller.get_image_by_id(image_id)


@router.get("/game/start")
async def start_game(request: Request, game_id: str = None):
    user = get_current_user_from_request(request)
    return await game_controller.start_game(user, game_id)


@router.post("/game/check-answers")
async def check_answers(request: Request, game_answer: GameAnswer):
    user = get_current_user_from_request(request)
    return await game_controller.check_answers(game_answer, user)


@router.get("/game/badges", response_model=UserBadgeList)
async def get_all_users_badges():
    return await game_controller.get_all_users_badges()


@router.get("/game/user-progress")
async def get_user_progress(request: Request):
    user = get_current_user_from_request(request)
    return await game_controller.get_user_progress(user)


@router.get("/game/build-match-progress")
async def get_build_match_progress(request: Request):
    user = get_current_user_from_request(request)
    return await game_controller.get_build_match_progress(user)


@router.get("/game/report")
async def get_user_game_report(request: Request):
    user = get_current_user_from_request(request)
    return await report_controller.get_user_game_report(user)
