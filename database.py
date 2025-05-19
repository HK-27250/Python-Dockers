# Import required modules
import os                          # For accessing environment variables like database credentials
import logging                     # For logging info, debug messages etc.
import psycopg2                    # PostgreSQL adapter for Python to connect and interact with PostgreSQL databases
from psycopg2.extras import RealDictCursor  # Optional: allows query results to be returned as dictionaries (not used here but imported)

# Initialize logging configuration to display debug and higher-level messages in the console
logging.basicConfig(level=logging.DEBUG)

def get_db_connection():
    """
    Create and return a connection to the PostgreSQL database.
    The connection details are fetched from environment variables for security.
    """
    # Use DATABASE_URL environment variable directly if provided
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        conn = psycopg2.connect(database_url)
    else:
        conn = psycopg2.connect(
            dbname=os.environ.get('PGDATABASE'),    # Database name from environment variable
            user=os.environ.get('PGUSER'),          # Database user from environment variable
            password=os.environ.get('PGPASSWORD'),  # Database password from environment variable
            host=os.environ.get('PGHOST'),          # Database host address from environment variable
            port=os.environ.get('PGPORT')           # Database port from environment variable
        )
    return conn  # Return the established database connection


def setup_database():
    """
    Set up the required database tables for the application if they don't already exist.
    This includes:
      - 'students' table to store student information.
      - 'attendance' table to record attendance status for each student.
    """
    # Get a connection to the database using the helper function
    connection = get_db_connection()

    # Create a cursor object to execute SQL commands
    cursor = connection.cursor()

    # SQL command to create the 'students' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,            -- Auto-incrementing primary key (unique student ID)
            name TEXT NOT NULL,               -- Student's name (cannot be null)
            roll_no TEXT UNIQUE NOT NULL,     -- Student's roll number (must be unique and cannot be null)
            class TEXT                        -- Student's class information (can be null)
        )
    ''')

    # SQL command to create the 'attendance' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id SERIAL PRIMARY KEY,                    -- Auto-incrementing primary key (unique attendance ID)
            student_id INTEGER,                       -- Reference to 'students.id'
            date TEXT NOT NULL,                       -- Date of attendance record (cannot be null)
            status TEXT NOT NULL,                     -- Attendance status like 'Present' or 'Absent' (cannot be null)
            FOREIGN KEY (student_id) REFERENCES students(id) -- Set 'student_id' as a foreign key linked to 'students.id'
        )
    ''')

    # Commit the changes to the database (make table creation permanent)
    connection.commit()

    # Close the database connection to free resources
    connection.close()

    # Log an informational message indicating database setup is complete
    logging.info("Database setup complete")

