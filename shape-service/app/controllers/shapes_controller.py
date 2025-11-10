from database.database import get_database
from fastapi import HTTPException

class ShapesController:
    def __init__(self):
        self.db = get_database()

    async def get_shapes(self):
        shapes = []
        pipeline = [
            {
                "$match": {}
            }
        ]
        cursor = self.db.shapes.aggregate(pipeline)
        if cursor:
            async for document in cursor:
                document['_id'] = str(document['_id'])
                shapes.append(document)
            return shapes
        raise HTTPException(status_code=404, detail="Shape not found")
    
    async def get_image_by_id(self, image_id: str):
        shape = await self.db.shapes.find_one({"id": image_id})
        if shape:
            data = {
                "id": shape["id"],
                "name": shape["name"],
                "description": shape["description"],
                "image_url": shape["image_url"],
            }
            return data
        raise HTTPException(status_code=404, detail="Shape not found")


