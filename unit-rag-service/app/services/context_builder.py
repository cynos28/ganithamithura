"""
Build contextual information from AR measurements for question generation
"""

from app.models.schemas import MeasurementType, MeasurementContext, ARMeasurementRequest


class ContextBuilder:
    """Builds learning context from AR measurements"""
    
    # Default object names if not provided
    DEFAULT_OBJECTS = {
        MeasurementType.LENGTH: ["pencil", "ruler", "book", "desk", "board"],
        MeasurementType.CAPACITY: ["bottle", "cup", "glass", "jar", "container"],
        MeasurementType.WEIGHT: ["apple", "bag", "book", "box", "object"],
        MeasurementType.AREA: ["paper", "desk", "board", "book", "surface"],
    }
    
    # Topic mapping
    TOPIC_MAP = {
        MeasurementType.LENGTH: "Length",
        MeasurementType.CAPACITY: "Capacity",
        MeasurementType.WEIGHT: "Weight",
        MeasurementType.AREA: "Area",
    }
    
    def build_context(self, request: ARMeasurementRequest) -> MeasurementContext:
        """Build context from AR measurement"""
        
        # Determine object name
        object_name = request.object_name or self._get_default_object(request.measurement_type)
        
        # Get topic
        topic = self.TOPIC_MAP[request.measurement_type]
        
        # Suggest grade level based on measurement complexity
        suggested_grade = self._suggest_grade(request.value, request.unit, request.measurement_type)
        
        # Build context description
        context_description = f"Student measured {object_name}: {request.value}{request.unit}"
        
        # Build personalized prompt snippet
        personalized_prompt = self._build_prompt_snippet(
            object_name, request.value, request.unit, request.measurement_type
        )
        
        # Generate difficulty hints
        difficulty_hints = self._generate_difficulty_hints(
            request.value, request.unit, request.measurement_type
        )
        
        return MeasurementContext(
            measurement_type=request.measurement_type,
            value=request.value,
            unit=request.unit,
            object_name=object_name,
            context_description=context_description,
            topic=topic,
            suggested_grade=suggested_grade,
            difficulty_hints=difficulty_hints,
            personalized_prompt=personalized_prompt,
        )
    
    def _get_default_object(self, measurement_type: MeasurementType) -> str:
        """Get a default object name for the measurement type"""
        import random
        return random.choice(self.DEFAULT_OBJECTS[measurement_type])
    
    def _suggest_grade(self, value: float, unit: str, measurement_type: MeasurementType) -> int:
        """Suggest appropriate grade level based on measurement complexity"""
        
        # Simple heuristics based on value ranges
        if measurement_type == MeasurementType.LENGTH:
            if value < 30 and unit in ["cm", "mm"]:
                return 1  # Small measurements for younger students
            elif value < 100:
                return 2
            elif value < 1000:
                return 3
            else:
                return 4
        
        elif measurement_type == MeasurementType.CAPACITY:
            if value < 500 and unit == "ml":
                return 1
            elif value < 2000:
                return 2
            else:
                return 3
        
        elif measurement_type == MeasurementType.WEIGHT:
            if value < 500 and unit == "g":
                return 1
            elif value < 2000:
                return 2
            else:
                return 3
        
        elif measurement_type == MeasurementType.AREA:
            if value < 100:
                return 2
            elif value < 1000:
                return 3
            else:
                return 4
        
        return 1  # Default
    
    def _build_prompt_snippet(
        self, object_name: str, value: float, unit: str, measurement_type: MeasurementType
    ) -> str:
        """Build a personalized prompt snippet for the LLM"""
        
        snippets = {
            MeasurementType.LENGTH: f"Your {object_name} is {value}{unit} long.",
            MeasurementType.CAPACITY: f"Your {object_name} holds {value}{unit}.",
            MeasurementType.WEIGHT: f"Your {object_name} weighs {value}{unit}.",
            MeasurementType.AREA: f"Your {object_name} has an area of {value}{unit}.",
        }
        
        return snippets.get(measurement_type, f"You measured {value}{unit}")
    
    def _generate_difficulty_hints(
        self, value: float, unit: str, measurement_type: MeasurementType
    ) -> list:
        """Generate hints for question difficulty progression"""
        
        hints = []
        
        # Basic conversion questions
        if measurement_type == MeasurementType.LENGTH:
            if unit == "cm":
                hints.extend(["conversion_to_mm", "conversion_to_m"])
            elif unit == "m":
                hints.extend(["conversion_to_cm", "conversion_to_km"])
        
        elif measurement_type == MeasurementType.CAPACITY:
            if unit == "ml":
                hints.append("conversion_to_l")
            elif unit == "l":
                hints.append("conversion_to_ml")
        
        elif measurement_type == MeasurementType.WEIGHT:
            if unit == "g":
                hints.append("conversion_to_kg")
            elif unit == "kg":
                hints.append("conversion_to_g")
        
        # Always add these progression hints
        hints.extend([
            "multiplication",  # e.g., "3 of these objects"
            "addition",        # e.g., "2 objects together"
            "comparison",      # e.g., "which is longer/heavier"
            "estimation",      # e.g., "about how many"
        ])
        
        return hints


# Singleton instance
context_builder = ContextBuilder()
