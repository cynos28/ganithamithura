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
