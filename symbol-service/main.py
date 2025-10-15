import os
import sys
from dotenv import load_dotenv
import logging

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.database import get_db_connection, get_database
from config.database_config import DatabaseConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize database with proper configuration"""
    load_dotenv()

    # Get database configuration
    db_config = DatabaseConfig.from_env()
    logger.info(f"Connecting to database: {db_config.database_name}")

    # Connect to database
    db_connection = get_db_connection()

    if not db_connection.connect():
        logger.error("Failed to connect to MongoDB")
        return False

    # Get database instance
    db = get_database()
    if db is None:
        logger.error("Failed to get database instance")
        return False

    logger.info("✅ Database connection successful")
    return True


def main():
    """Main function to initialize database connection"""
    print("🚀 Starting Ganithamithura Symbols Application\n")

    # Initialize database with configuration
    if not initialize_database():
        print("❌ Database connection failed")
        sys.exit(1)


if __name__ == "__main__":
    main()