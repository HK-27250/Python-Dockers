import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

def get_db_connection():
    """Create and return a database connection"""
    conn = psycopg2.connect(
        dbname=os.environ.get('PGDATABASE'),
        user=os.environ.get('PGUSER'),
        password=os.environ.get('PGPASSWORD'),
        host=os.environ.get('PGHOST'),
        port=os.environ.get('PGPORT')
    )
    return conn

def setup_database():
    """Set up the database tables if they don't exist"""
    connection = get_db_connection()
    cursor = connection.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            class TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY,
            student_id INTEGER,
            date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id)
        )
    ''')
    
    connection.commit()
    connection.close()
    logging.info("Database setup complete")
