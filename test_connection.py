"""
Simple script to test PostgreSQL connection.
Run this after starting docker-compose.
"""

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5432/healthcare_db"

def main():
    try:
        print("🔌 Attempting to connect to PostgreSQL...")
        engine = create_engine(DB_URL)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 'Connection OK' AS status;"))
            status = result.fetchone()[0]

        print(f"✅ Database connection successful: {status}")

    except SQLAlchemyError as e:
        print("❌ Database connection failed:")
        print(e)

if __name__ == "__main__":
    main()
