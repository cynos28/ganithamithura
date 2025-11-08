from fastapi import APIRouter, UploadFile, File, Request, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.controllers.shapes_detection import ShapesDetectionController
from app.controllers.user_controller import UserController
from app.models.model import UserCreate



router = APIRouter()

shapes_detection_controller = ShapesDetectionController()
user_controller = UserController()

@router.post("/detect-shape/")
async def detect_shape(request: Request, image_file: UploadFile = File(None)):
    return await shapes_detection_controller.detect_shape(request, image_file)

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    return await user_controller.login(form_data)


@router.post("/register")
async def register_user(user_data: UserCreate):
    return await user_controller.register(user_data)