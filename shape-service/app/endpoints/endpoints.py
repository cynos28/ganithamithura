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
    """
    Detects shapes in an uploaded image.

    Args:
        request: The incoming HTTP request.
        image_file: The image file to be analyzed.

    Returns:
        A JSON response containing the shape detection results.
    """
    return await shapes_detection_controller.detect_shape(request, image_file)

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Provides an access token for an existing user.

    Args:
        form_data: The user's login credentials (username and password).

    Returns:
        A JSON response with the access token and token type.
    """
    return await user_controller.login(form_data)


@router.post("/register")
async def register_user(user_data: UserCreate):
    """
    Registers a new user in the system.

    Args:
        user_data: The data for the new user to be created.

    Returns:
        A JSON response confirming the user registration.
    """
    return await user_controller.register(user_data)