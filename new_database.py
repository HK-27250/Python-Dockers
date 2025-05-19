import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """
    Create and return a connection to the PostgreSQL database.
    Uses individual connection parameters instead of connection string.
    """
    try:
        # Connect using individual parameters which are more reliable
        conn = psycopg2.connect(
            dbname=os.environ.get('PGDATABASE'),
            user=os.environ.get('PGUSER'),
            password=os.environ.get('PGPASSWORD'),
            host=os.environ.get('PGHOST'),
            port=os.environ.get('PGPORT')
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

def setup_database():
    """
    Set up the database tables if they don't exist.
    """
    try:
        # Get connection
        connection = get_db_connection()
        cursor = connection.cursor()
        
        # Create students table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                roll_no TEXT UNIQUE NOT NULL,
                class TEXT
            )
        ''')
        
        # Create attendance table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS attendance (
                id SERIAL PRIMARY KEY,
                student_id INTEGER,
                date TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id)
            )
        ''')
        
        # Commit changes
        connection.commit()
        connection.close()
        
        logger.info("Database setup complete")
    except Exception as e:
        logger.error(f"Database setup error: {str(e)}")
        raise