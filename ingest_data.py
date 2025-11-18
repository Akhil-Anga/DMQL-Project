import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Database URL must match docker-compose.yml
DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5432/healthcare_db"

# Path to the raw CSV (put Healthcare.csv inside the Data/ folder)
RAW_CSV_PATH = "Data/Healthcare.csv"


def main():
    # 1. Create engine and test connection
    try:
        engine = create_engine(DB_URL)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Connected to PostgreSQL.")
    except SQLAlchemyError as e:
        print("❌ Failed to connect to PostgreSQL:", e)
        return

    # 2. Read raw CSV
    print(f"📂 Reading raw data from {RAW_CSV_PATH} ...")
    df = pd.read_csv(RAW_CSV_PATH)

    # 3. Rename columns to snake_case
    df = df.rename(columns={
        "PatientId": "patient_id_raw",
        "AppointmentID": "appointment_id",
        "Gender": "gender",
        "ScheduledDay": "scheduled_datetime",
        "AppointmentDay": "appointment_datetime",
        "Neighbourhood": "neighborhood",
        "Scholarship": "scholarship",
        "Hipertension": "hypertension",
        "Diabetes": "diabetes",
        "Alcoholism": "alcoholism",
        "Handcap": "handicap",
        "SMS_received": "sms_received",
        "No-show": "no_show",
        "Age": "age"
    })

    # 4. Parse datetimes
    df["scheduled_datetime"] = pd.to_datetime(df["scheduled_datetime"])
    df["appointment_datetime"] = pd.to_datetime(df["appointment_datetime"])

    # 5. Clean age (remove negative ages if any)
    df = df[df["age"] >= 0]

    # 6. Map no_show to boolean
    df["no_show"] = df["no_show"].map({"No": False, "Yes": True})

    # 7. Cast flags to bool
    for col in ["scholarship", "hypertension", "diabetes", "alcoholism", "sms_received"]:
        df[col] = df[col].astype(bool)

    # 8. Neighborhoods (distinct)
    neighborhoods = (
        df[["neighborhood"]]
        .drop_duplicates()
        .rename(columns={"neighborhood": "name"})  # must match table column
        .copy()
    )

    with engine.begin() as conn:
        print("🧱 Inserting neighborhoods...")
        neighborhoods.to_sql("neighborhood", conn, if_exists="append", index=False)

        # get mapping name -> id from DB
        neigh_df = pd.read_sql("SELECT neighborhood_id, name FROM neighborhood", conn)
        neigh_map = dict(zip(neigh_df["name"], neigh_df["neighborhood_id"]))

    df["neighborhood_id"] = df["neighborhood"].map(neigh_map)

    # 9. Patients (distinct by patient_id_raw)
    patients = df[[
        "patient_id_raw", "gender", "age",
        "neighborhood_id", "scholarship",
        "hypertension", "diabetes", "alcoholism", "handicap"
    ]].drop_duplicates(subset=["patient_id_raw"]).copy()

    patients = patients.rename(columns={
        "patient_id_raw": "external_patient_id",
        "age": "age_at_registration",
        "handicap": "handicap_level"
    })

    with engine.begin() as conn:
        print("🧱 Inserting patients...")
        patients.to_sql("patient", conn, if_exists="append", index=False)

        # build mapping from external_patient_id -> internal patient_id
        pat_df = pd.read_sql("SELECT patient_id, external_patient_id FROM patient", conn)
        pat_map = dict(zip(pat_df["external_patient_id"], pat_df["patient_id"]))

    # 10. Appointments
    appointments = df[[
        "appointment_id", "patient_id_raw",
        "scheduled_datetime", "appointment_datetime",
        "sms_received", "no_show"
    ]].copy()

    # Map external patient_id_raw to internal patient_id (FK)
    appointments["patient_id"] = appointments["patient_id_raw"].map(pat_map)

    # Drop any rows where mapping failed (should be none, but safe)
    appointments = appointments.dropna(subset=["patient_id"])

    # Convert patient_id to integer (from float due to NaN handling)
    appointments["patient_id"] = appointments["patient_id"].astype(int)

    # Drop the raw external id; keep only internal FK
    appointments = appointments.drop(columns=["patient_id_raw"])

    with engine.begin() as conn:
        print("🧱 Inserting appointments...")
        appointments.to_sql("appointment", conn, if_exists="append", index=False)

    print("🎉 Data ingestion completed successfully.")


if __name__ == "__main__":
    main()
