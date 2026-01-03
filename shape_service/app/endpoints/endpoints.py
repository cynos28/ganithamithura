from fastapi import APIRouter, UploadFile, File, Request, Depends
from app.controllers.shapes_detection import ShapesDetectionController
from app.controllers.shapes_controller import ShapesController
from authentication_service.auth_service import get_current_user
from app.controllers.game_controller import GameController
from app.controllers.report_controller import ReportController
from app.models.model import GameAnswer, UserBadgeList


router = APIRouter()

shapes_detection_controller = ShapesDetectionController()
shapes_controller = ShapesController()
game_controller = GameController()
report_controller = ReportController()

@router.post("/detect-shape/")
async def detect_shape(request: Request, image_file: UploadFile = File(None)):
    return await shapes_detection_controller.detect_shape(request, image_file)

@router.get("/shapes/")
async def get_shapes():
    return await shapes_controller.get_shapes()

@router.get("/shapes/{shape_type}")
async def get_shapes_by_type(shape_type: str):
    return await shapes_controller.get_shapes_by_type(shape_type)

@router.get("/images/{image_id}")
async def get_image_by_id(image_id: str):
    return await shapes_controller.get_image_by_id(image_id)

@router.get("/game/start")
async def start_game(game_id: str = None):
    # TEMPORARY: Bypass authentication for testing - hardcoded user
    mock_user = {"user_name": "user1"}
    return await game_controller.start_game(mock_user, game_id)

@router.post("/game/check-answers")
async def check_answers(game_answer: GameAnswer):
    # TEMPORARY: Bypass authentication for testing - hardcoded user
    mock_user = {"user_name": "user1"}
    return await game_controller.check_answers(game_answer, mock_user)

@router.get("/game/badges", response_model=UserBadgeList)
async def get_all_users_badges(user: dict = Depends(get_current_user)):
    return await game_controller.get_all_users_badges()

@router.get("/game/report")
async def get_user_game_report(user: dict = Depends(get_current_user)):
    return await report_controller.get_user_game_report(user)
