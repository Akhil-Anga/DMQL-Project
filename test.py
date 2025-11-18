import sys
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Adjust if your docker-compose uses different values
DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5432/healthcare_db"


def get_engine():
    try:
        engine = create_engine(DB_URL)
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful.")
        return engine
    except SQLAlchemyError as e:
        print("❌ Failed to connect to database:", e)
        sys.exit(1)


def check_tables(engine):
    print("\n🔍 Checking if required tables exist...")
    required_tables = {"neighborhood", "patient", "appointment"}

    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public';
            """)
        )
        existing = {row[0] for row in result}

    missing = required_tables - existing
    if missing:
        print("❌ Missing tables:", ", ".join(missing))
    else:
        print("✅ All required tables exist:", ", ".join(required_tables))


def print_row_counts(engine):
    print("\n📊 Row counts per table:")

    with engine.connect() as conn:
        for table in ["neighborhood", "patient", "appointment"]:
            try:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table};")).scalar()
                print(f"  - {table}: {count} rows")
            except SQLAlchemyError as e:
                print(f"  - {table}: ❌ error querying table:", e)


def check_fk_integrity(engine):
    """
    Check that every appointment has a valid patient_id.
    (Should be guaranteed by FK constraint, but nice for demo.)
    """
    print("\n🔗 Checking FK integrity: appointments → patient...")

    query = """
        SELECT a.appointment_id
        FROM appointment a
        LEFT JOIN patient p ON a.patient_id = p.patient_id
        WHERE p.patient_id IS NULL
        LIMIT 5;
    """

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)

    if df.empty:
        print("✅ All appointments have a valid patient_id.")
    else:
        print("❌ Found appointments with invalid patient_id! Sample:")
        print(df)


def sample_analysis_query(engine):
    """
    Example analytical query:
    - no-show rate by neighborhood (top 5)
    """
    print("\n📈 Sample analysis: top 5 neighborhoods by no-show rate")

    query = """
        SELECT n.name AS neighborhood,
               COUNT(*) AS total_appointments,
               SUM(CASE WHEN a.no_show = TRUE THEN 1 ELSE 0 END) AS no_shows,
               ROUND(100.0 * SUM(CASE WHEN a.no_show = TRUE THEN 1 ELSE 0 END) 
                     / COUNT(*), 2) AS no_show_rate_percent
        FROM appointment a
        JOIN patient p ON a.patient_id = p.patient_id
        JOIN neighborhood n ON p.neighborhood_id = n.neighborhood_id
        GROUP BY n.name
        HAVING COUNT(*) >= 50     -- ignore tiny groups
        ORDER BY no_show_rate_percent DESC
        LIMIT 5;
    """

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)

    if df.empty:
        print("No data found. Did you run ingest_data.py?")
    else:
        print(df.to_string(index=False))


def main():
    engine = get_engine()
    check_tables(engine)
    print_row_counts(engine)
    check_fk_integrity(engine)
    sample_analysis_query(engine)


if __name__ == "__main__":
    main()
