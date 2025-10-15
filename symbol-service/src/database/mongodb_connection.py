import os
from typing import Optional
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

logger = logging.getLogger(__name__)


class MongoDBConnection:
    """MongoDB connection manager using singleton pattern"""

    _instance: Optional['MongoDBConnection'] = None
    _client: Optional[MongoClient] = None
    _database: Optional[Database] = None

    def __new__(cls) -> 'MongoDBConnection':
        if cls._instance is None:
            cls._instance = super(MongoDBConnection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True

    def _get_connection_string(self) -> str:
        """Get MongoDB connection string from environment variables"""
        return os.getenv(
            'MONGO_URI',
            os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
        )

    def _get_database_name(self) -> str:
        """Get database name from environment variables"""
        return os.getenv('MONGODB_DATABASE', 'ganithamithura_symbols')

    def connect(self) -> bool:
        """Establish connection to MongoDB"""
        try:
            if self._client is None:
                # Get connection details each time we connect
                connection_string = self._get_connection_string()
                database_name = self._get_database_name()

                self._client = MongoClient(
                    connection_string,
                    serverSelectionTimeoutMS=5000,  # 5 second timeout
                    connectTimeoutMS=5000,
                    maxPoolSize=50,
                    minPoolSize=5
                )

                # Test the connection
                self._client.admin.command('ping')
                self._database = self._client[database_name]
                logger.info(f"Connected to MongoDB database: {database_name}")
                return True

        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            self._client = None
            self._database = None
            return False

        return True

    def disconnect(self) -> None:
        """Close MongoDB connection"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("Disconnected from MongoDB")

    def get_database(self) -> Optional[Database]:
        """Get the database instance"""
        if self._database is None:
            if not self.connect():
                return None
        return self._database

    def get_collection(self, collection_name: str) -> Optional[Collection]:
        """Get a specific collection from the database"""
        database = self.get_database()
        if database is None:
            return None
        return database[collection_name]

    def is_connected(self) -> bool:
        """Check if connected to MongoDB"""
        if self._client is None:
            return False
        try:
            self._client.admin.command('ping')
            return True
        except Exception:
            return False


# Global instance for easy access
mongodb_connection = MongoDBConnection()


def get_db_connection() -> MongoDBConnection:
    """Get the global MongoDB connection instance"""
    return mongodb_connection


def get_database() -> Optional[Database]:
    """Get the database instance"""
    return mongodb_connection.get_database()


def get_collection(collection_name: str) -> Optional[Collection]:
    """Get a specific collection"""
    return mongodb_connection.get_collection(collection_name)