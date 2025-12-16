from common.database.database import get_database
from fastapi import HTTPException

class ShapesController:
    def __init__(self):
        self.db = get_database()
    
    
    async def get_shapes(self):
        """
        Retrieves all shapes from the database.

        Returns:
            list: A list of dictionaries, where each dictionary represents a shape.

        Raises:
            HTTPException: If no shapes are found in the database.
        """
        shapes = []
        cursor = self.db.shapes.find({})
        async for document in cursor:
            document['_id'] = str(document['_id'])
            shapes.append(document)
        
        if not shapes:
            raise HTTPException(status_code=404, detail="No shapes found")
        return shapes

    async def get_shapes_by_type(self, shape_type: str):
        """
        Retrieves all shapes of a specific type from the database.

        Args:
            shape_type (str): The type of the shapes to retrieve (e.g., "2d", "3d").

        Returns:
            list: A list of dictionaries, where each dictionary represents a shape.
        """
        shapes = []
        cursor = self.db.shapes.find({"type": shape_type})
        async for document in cursor:
            document['_id'] = str(document['_id'])
            shapes.append(document)
        
        if not shapes:
            raise HTTPException(status_code=404, detail=f"No {shape_type} shapes found")
        return shapes
    
    async def get_image_by_id(self, image_id: str):
        """
        Retrieves a single shape by its ID.

        Args:
            image_id (str): The ID of the image to retrieve.

        Returns:
            dict: A dictionary containing the shape's data (id, name, description, image_url).

        Raises:
            HTTPException: If no shape with the given ID is found in the database.
        """
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


