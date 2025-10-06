import mysql.connector
from mysql.connector import Error
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'database': 'fantasy_soccer',
    'user': 'root',
    'password': 'NewPassword',
    'port': 3306
}

def get_db_connection():
    """Establishes and returns a new MySQL database connection."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        return None

def add_fpl_id_column():
    """Add fpl_id column to player table"""
    connection = get_db_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # Add fpl_id column
        cursor.execute("ALTER TABLE player ADD COLUMN fpl_id BIGINT")
        logger.info("Added fpl_id column to player table")
        
        # Update existing records to set fpl_id = id
        cursor.execute("UPDATE player SET fpl_id = id")
        logger.info("Updated existing records with fpl_id = id")
        
        connection.commit()
        logger.info("Successfully added fpl_id column")
        
        cursor.close()
        connection.close()
        return True
        
    except Error as e:
        logger.error(f"Error adding fpl_id column: {e}")
        if connection.is_connected():
            cursor.close()
            connection.close()
        return False

if __name__ == '__main__':
    logger.info("Adding fpl_id column to player table...")
    if add_fpl_id_column():
        logger.info("✅ Successfully added fpl_id column!")
    else:
        logger.error("❌ Failed to add fpl_id column")
