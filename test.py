import sys
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Adjust if your docker-compose uses different values
DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5432/healthcare_db"


# ---------------------------------------------------
# 1. Connection helper
# ---------------------------------------------------
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


# ---------------------------------------------------
# 2. Table existence check
# ---------------------------------------------------
def check_tables(engine):
    print("\n🔍 Checking if required tables exist...")

    required_tables = {
        "patient",
        "doctor",
        "hospital",
        "insurance_provider",
        "medical_condition",
        "medication",
        "admission",
        "test_result",
    }

    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public';
                """
            )
        )
        existing = {row[0] for row in result}

    missing = required_tables - existing
    if missing:
        print("❌ Missing tables:", ", ".join(sorted(missing)))
    else:
        print("✅ All required tables exist:", ", ".join(sorted(required_tables)))


# ---------------------------------------------------
# 3. Row counts per table
# ---------------------------------------------------
def print_row_counts(engine):
    print("\n📊 Row counts per table:")

    tables = [
        "patient",
        "doctor",
        "hospital",
        "insurance_provider",
        "medical_condition",
        "medication",
        "admission",
        "test_result",
    ]

    with engine.connect() as conn:
        for table in tables:
            try:
                count = conn.execute(text(f"SELECT COUNT(*) FROM {table};")).scalar()
                print(f"  - {table:18s}: {count} rows")
            except SQLAlchemyError as e:
                print(f"  - {table:18s}: ❌ error querying table:", e)


# ---------------------------------------------------
# 4. FK integrity checks
# ---------------------------------------------------
def check_fk_integrity(engine):
    """
    Simple FK checks:
      - every admission has valid patient / doctor / hospital / insurance / condition
      - every test_result has a valid admission_id
    """
    print("\n🔗 Checking FK integrity for admissions and test results...")

    checks = {
        "admission → patient": """
            SELECT a.admission_id
            FROM admission a
            LEFT JOIN patient p ON a.patient_id = p.patient_id
            WHERE p.patient_id IS NULL
            LIMIT 5;
        """,
        "admission → doctor": """
            SELECT a.admission_id
            FROM admission a
            LEFT JOIN doctor d ON a.doctor_id = d.doctor_id
            WHERE d.doctor_id IS NULL
            LIMIT 5;
        """,
        "admission → hospital": """
            SELECT a.admission_id
            FROM admission a
            LEFT JOIN hospital h ON a.hospital_id = h.hospital_id
            WHERE h.hospital_id IS NULL
            LIMIT 5;
        """,
        "admission → insurance_provider": """
            SELECT a.admission_id
            FROM admission a
            LEFT JOIN insurance_provider i ON a.insurance_id = i.insurance_id
            WHERE i.insurance_id IS NULL
            LIMIT 5;
        """,
        "admission → medical_condition": """
            SELECT a.admission_id
            FROM admission a
            LEFT JOIN medical_condition c ON a.condition_id = c.condition_id
            WHERE c.condition_id IS NULL
            LIMIT 5;
        """,
        "test_result → admission": """
            SELECT t.test_result_id
            FROM test_result t
            LEFT JOIN admission a ON t.admission_id = a.admission_id
            WHERE a.admission_id IS NULL
            LIMIT 5;
        """,
    }

    with engine.connect() as conn:
        for label, query in checks.items():
            df = pd.read_sql(text(query), conn)
            if df.empty:
                print(f"  ✅ {label} OK")
            else:
                print(f"  ❌ {label} has orphan rows! Sample:")
                print(df)


# ---------------------------------------------------
# 5. Sample analytical query
# ---------------------------------------------------
def sample_analysis_query(engine):
    """
    Example analysis:
      - Top 5 medical conditions by total billing amount,
        broken down by hospital.
    """
    print("\n📈 Sample analysis: Top 5 conditions by total billing amount (hospital-level)")

    query = """
        SELECT
            c.condition_name,
            h.hospital_name,
            COUNT(*) AS total_admissions,
            SUM(a.billing_amount) AS total_billing,
            ROUND(AVG(a.billing_amount), 2) AS avg_billing
        FROM admission a
        JOIN medical_condition c ON a.condition_id = c.condition_id
        JOIN hospital h ON a.hospital_id = h.hospital_id
        GROUP BY c.condition_name, h.hospital_name
        ORDER BY total_billing DESC
        LIMIT 10;
    """

    with engine.connect() as conn:
        df = pd.read_sql(text(query), conn)

    if df.empty:
        print("No data found. Did you run ingest_data.py?")
    else:
        print(df.to_string(index=False))


# ---------------------------------------------------
# 6. Main
# ---------------------------------------------------
def main():
    engine = get_engine()
    check_tables(engine)
    print_row_counts(engine)
    check_fk_integrity(engine)
    sample_analysis_query(engine)


if __name__ == "__main__":
    main()
