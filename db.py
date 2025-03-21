import psycopg2
from psycopg2 import sql
import bcrypt

# Database connection settings
DB_NAME = "rental_management"
DB_USER = "janice"
DB_PASSWORD = "Coraggiosa"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect_db():
    """Establish a database connection."""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        print("Database connected successfully!")
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None

def check_user_credentials(username, password, role):
    """Check if a user's credentials are valid."""
    conn = connect_db()  # Reuse the database connection function
    if not conn:
        return False, None, None
    
    try:
        cursor = conn.cursor()

        # Ensure case insensitivity and trim any spaces
        query = sql.SQL("SELECT username, password_hash FROM users WHERE TRIM(username) = %s AND LOWER(role) = LOWER(%s)")
        cursor.execute(query, (username.strip(), role))

        result = cursor.fetchone()
        if result:
            db_username, db_hashed_password = result
            if bcrypt.checkpw(password.encode(), db_hashed_password.encode() if isinstance(db_hashed_password, str) else db_hashed_password):
                return True, db_username, db_hashed_password  

        return False, None, None  

    except Exception as e:
        print(f"Database Error: {e}")
        return False, None, None
    finally:
        conn.close()

if __name__ == "__main__":
    conn = connect_db()
