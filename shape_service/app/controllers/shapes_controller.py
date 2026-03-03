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
        # The shapes are stored in a single document with a 'shapes' array
        document = await self.db.shapes.find_one({})
        
        if not document or 'shapes' not in document:
            raise HTTPException(status_code=404, detail="No shapes found")
        
        return document['shapes']

    async def get_shapes_by_type(self, shape_type: str):
        """
        Retrieves all shapes of a specific type from the database.

        Args:
            shape_type (str): The type of the shapes to retrieve (e.g., "2d", "3d").

        Returns:
            list: A list of dictionaries, where each dictionary represents a shape.
        """
        # Get the document containing all shapes
        document = await self.db.shapes.find_one({})
        
        if not document or 'shapes' not in document:
            raise HTTPException(status_code=404, detail="No shapes found")
        
        # Filter shapes by type
        filtered_shapes = [
            shape for shape in document['shapes'] 
            if shape.get('type') == shape_type
        ]
        
        if not filtered_shapes:
            raise HTTPException(status_code=404, detail=f"No {shape_type} shapes found")
        
        return filtered_shapes
    
    async def get_shape_by_id(self, shape_id: str):
        """
        Retrieves a single shape by its ID.

        Args:
            shape_id (str): The ID of the shape to retrieve.

        Returns:
            dict: A dictionary containing the complete shape data.

        Raises:
            HTTPException: If no shape with the given ID is found.
        """
        document = await self.db.shapes.find_one({})
        
        if not document or 'shapes' not in document:
            raise HTTPException(status_code=404, detail="No shapes found")
        
        # Find the shape with matching ID
        for shape in document['shapes']:
            if shape.get('id') == shape_id:
                return shape
        
        raise HTTPException(status_code=404, detail="Shape not found")
    
    async def get_shape_by_name(self, shape_name: str):
        """
        Retrieves a single shape by its name.

        Args:
            shape_name (str): The name of the shape to retrieve (case-insensitive).

        Returns:
            dict: A dictionary containing the complete shape data.

        Raises:
            HTTPException: If no shape with the given name is found.
        """
        document = await self.db.shapes.find_one({})
        
        if not document or 'shapes' not in document:
            raise HTTPException(status_code=404, detail="No shapes found")
        
        # Find the shape with matching name (case-insensitive)
        shape_name_lower = shape_name.lower()
        for shape in document['shapes']:
            if shape.get('name', '').lower() == shape_name_lower:
                return shape
        
        raise HTTPException(status_code=404, detail=f"Shape '{shape_name}' not found")
    
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
        document = await self.db.shapes.find_one({})
        
        if not document or 'shapes' not in document:
            raise HTTPException(status_code=404, detail="No shapes found")
        
        # Find the shape with matching ID
        for shape in document['shapes']:
            if shape.get('id') == image_id:
                return {
                    "id": shape["id"],
                    "name": shape["name"],
                    "description": shape["description"],
                    "image_url": shape["image_url"],
                }
        
        raise HTTPException(status_code=404, detail="Shape not found")


