from database.database import get_database
from fastapi import HTTPException

class ShapesController:
    def __init__(self):
        self.db = get_database()
    
    
    """
    Retrieves all shapes from the database.

    Returns:
        list: A list of dictionaries, where each dictionary represents a shape.

    Raises:
        HTTPException: If no shapes are found in the database.
    """
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
    
    """
    Retrieves a single shape by its ID.

    Args:
        image_id (str): The ID of the image to retrieve.

    Returns:
        dict: A dictionary containing the shape's data (id, name, description, image_url).

    Raises:
        HTTPException: If no shape with the given ID is found in the database.
    """
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


