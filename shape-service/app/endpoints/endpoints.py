from fastapi import APIRouter, UploadFile, File, Request
from app.controllers.shapes_detection import ShapesDetectionController



router = APIRouter()

shapes_detection_controller = ShapesDetectionController()


@router.post("/detect-shape/")
async def detect_shape(request: Request, image_file: UploadFile = File(None)):
    return await shapes_detection_controller.detect_shape(request, image_file)