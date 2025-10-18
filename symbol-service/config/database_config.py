import os
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class DatabaseConfig:
    """Database configuration settings"""

    # MongoDB Settings
    mongodb_uri: str
    database_name: str
    connection_timeout: int
    server_selection_timeout: int
    max_pool_size: int
    min_pool_size: int

    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create database config from environment variables"""
        return cls(
            mongodb_uri=os.getenv('MONGO_URI', os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')),
            database_name=os.getenv('MONGODB_DATABASE', 'ganithamithura_symbols'),
            connection_timeout=int(os.getenv('MONGODB_CONNECTION_TIMEOUT', '5000')),
            server_selection_timeout=int(os.getenv('MONGODB_SERVER_SELECTION_TIMEOUT', '5000')),
            max_pool_size=int(os.getenv('MONGODB_MAX_POOL_SIZE', '50')),
            min_pool_size=int(os.getenv('MONGODB_MIN_POOL_SIZE', '5'))
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary for MongoDB client"""
        return {
            'host': self.mongodb_uri,
            'connectTimeoutMS': self.connection_timeout,
            'serverSelectionTimeoutMS': self.server_selection_timeout,
            'maxPoolSize': self.max_pool_size,
            'minPoolSize': self.min_pool_size
        }


# Collection names constants
class Collections:
    """Database collection names"""
    USERS = 'users'
    MATH_PROBLEMS = 'math_problems'
    USER_SESSIONS = 'user_sessions'
    LEARNING_PROGRESS = 'learning_progress'
    VOICE_RECORDINGS = 'voice_recordings'
    SYMBOLS = 'symbols'
    TUTORIALS = 'tutorials'


# Database indexes configuration
DATABASE_INDEXES = {
    Collections.USERS: [
        ('email', 1),
        ('created_at', -1)
    ],
    Collections.MATH_PROBLEMS: [
        ('difficulty_level', 1),
        ('subject', 1),
        ('created_at', -1)
    ],
    Collections.USER_SESSIONS: [
        ('user_id', 1),
        ('session_date', -1),
        ('created_at', -1)
    ],
    Collections.LEARNING_PROGRESS: [
        ('user_id', 1),
        ('subject', 1),
        ('updated_at', -1)
    ],
    Collections.VOICE_RECORDINGS: [
        ('user_id', 1),
        ('session_id', 1),
        ('created_at', -1)
    ],
    Collections.SYMBOLS: [
        ('symbol_name', 1),
        ('category', 1)
    ],
    Collections.TUTORIALS: [
        ('level', 1),
        ('subject', 1),
        ('created_at', -1)
    ]
}