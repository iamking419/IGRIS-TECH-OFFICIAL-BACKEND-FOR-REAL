import re
import sys
from sqlalchemy import text
from database import engine


def test_connection():
    """Performs a safe connectivity check to verify database connection."""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            row = result.fetchone()
            if row and row[0] == 1:
                print("Database connection: OK")
                return 0
            else:
                print("Database connection: FAILED (Unexpected response)")
                return 1
    except Exception as e:
        # Sanitize any password in error messages
        err_msg = str(e)
        sanitized = re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", err_msg)
        print("Database connection: FAILED")
        print(f"Error details: {sanitized}")
        return 1


if __name__ == "__main__":
    sys.exit(test_connection())

