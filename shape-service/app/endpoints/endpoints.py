from fastapi import APIRouter, UploadFile, File, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.controllers.shapes_detection import ShapesDetectionController
from app.controllers.user_controller import UserController
from app.models.model import UserCreate
from app.controllers.shapes_controller import ShapesController
from app.services.auth_service import get_current_user
from app.controllers.game_controller import GameController
from app.models.model import UserCreate, GameAnswer


router = APIRouter()

shapes_detection_controller = ShapesDetectionController()
user_controller = UserController()
shapes_controller = ShapesController()
game_controller = GameController()

@router.post("/detect-shape/")
async def detect_shape(request: Request, image_file: UploadFile = File(None)):
    return await shapes_detection_controller.detect_shape(request, image_file)

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    return await user_controller.login(form_data)


@router.post("/register")
async def register_user(user_data: UserCreate):
    return await user_controller.register(user_data)

@router.get("/shapes/")
async def get_shapes():
    return await shapes_controller.get_shapes()

@router.get("/images/{image_id}")
async def get_image_by_id(image_id: str):
    return await shapes_controller.get_image_by_id(image_id)

@router.get("/game/start")
async def start_game(user: dict = Depends(get_current_user)):
    return await game_controller.start_game(user)

@router.post("/game/check-answers")
async def check_answers(game_answer: GameAnswer, user: dict = Depends(get_current_user)):
    return await game_controller.check_answers(game_answer, user)

