# python
from fastapi import HTTPException, UploadFile, File, Request
from fastapi.concurrency import run_in_threadpool
from app.services.shape_predict import get_shape_from_image

class ShapesDetectionController:
    def __init__(self):
        pass
    async def detect_shape(self,request: Request, image_file: UploadFile = File(None)):
        try:
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                payload = await request.json()
                image_url = payload.get("image_url")
                if not image_url:
                    raise HTTPException(status_code=400, detail="400: No image provided as a file or a URL")
                shape = await run_in_threadpool(get_shape_from_image, str(image_url))
            elif image_file:
                shape = await run_in_threadpool(get_shape_from_image, image_file.file)
            else:
                raise HTTPException(status_code=400, detail="400: No image provided as a file or a URL")
            return {"shape": shape}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
