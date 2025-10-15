"""
Math Tutor Configuration
Reusable configuration for grade levels, performance levels, and sublevels
"""


class TutorConfig:
    """Configuration class for Math Tutor settings"""

    # Grade levels
    GRADES = [1, 2, 3]
    DEFAULT_GRADE = 1

    # Performance levels
    PERFORMANCE_LEVELS = [1, 2, 3]
    DEFAULT_PERFORMANCE_LEVEL = 1

    # Sublevels
    SUBLEVELS = ["Starter", "Explorer", "Solver", "Champion"]
    DEFAULT_SUBLEVEL = "Starter"

    @staticmethod
    def validate_grade(grade: int) -> int:
        """
        Validate and return a valid grade level.

        Args:
            grade: Grade level to validate

        Returns:
            Valid grade level (1, 2, or 3)
        """
        if grade not in TutorConfig.GRADES:
            print(f"⚠️ Invalid grade {grade}, using default: {TutorConfig.DEFAULT_GRADE}")
            return TutorConfig.DEFAULT_GRADE
        return grade

    @staticmethod
    def validate_performance_level(performance_level: int) -> int:
        """
        Validate and return a valid performance level.

        Args:
            performance_level: Performance level to validate

        Returns:
            Valid performance level (1, 2, or 3)
        """
        if performance_level not in TutorConfig.PERFORMANCE_LEVELS:
            print(f"⚠️ Invalid performance level {performance_level}, using default: {TutorConfig.DEFAULT_PERFORMANCE_LEVEL}")
            return TutorConfig.DEFAULT_PERFORMANCE_LEVEL
        return performance_level

    @staticmethod
    def validate_sublevel(sublevel: str) -> str:
        """
        Validate and return a valid sublevel.

        Args:
            sublevel: Sublevel name to validate

        Returns:
            Valid sublevel name
        """
        if sublevel not in TutorConfig.SUBLEVELS:
            print(f"⚠️ Invalid sublevel '{sublevel}', using default: {TutorConfig.DEFAULT_SUBLEVEL}")
            return TutorConfig.DEFAULT_SUBLEVEL
        return sublevel

    @staticmethod
    def get_config_summary(grade: int, performance_level: int, sublevel: str) -> str:
        """
        Get a formatted summary of the configuration.

        Args:
            grade: Grade level
            performance_level: Performance level
            sublevel: Sublevel name

        Returns:
            Formatted configuration summary
        """
        return f"Grade {grade}, Performance Level {performance_level}, {sublevel} sublevel"


class StudentProfile:
    """Student profile with grade, performance level, and sublevel"""

    def __init__(self, grade: int = 1, performance_level: int = 1, sublevel: str = "Starter"):
        """
        Initialize student profile.

        Args:
            grade: Grade level (1, 2, or 3)
            performance_level: Performance level (1, 2, or 3)
            sublevel: Sublevel name (Starter, Explorer, Solver, or Champion)
        """
        self.grade = TutorConfig.validate_grade(grade)
        self.performance_level = TutorConfig.validate_performance_level(performance_level)
        self.sublevel = TutorConfig.validate_sublevel(sublevel)

    def to_dict(self) -> dict:
        """Convert profile to dictionary"""
        return {
            'grade': self.grade,
            'performance_level': self.performance_level,
            'sublevel': self.sublevel
        }

    def __str__(self) -> str:
        """String representation"""
        return TutorConfig.get_config_summary(self.grade, self.performance_level, self.sublevel)

    def __repr__(self) -> str:
        """Repr representation"""
        return f"StudentProfile(grade={self.grade}, performance_level={self.performance_level}, sublevel='{self.sublevel}')"
