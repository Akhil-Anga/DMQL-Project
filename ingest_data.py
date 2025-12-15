import os
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Database URL must match docker-compose.yml
DB_URL = "postgresql+psycopg2://admin:admin123@localhost:5432/healthcare_db"
# DB_URL = "postgresql://postgres:Ramaseshu1%40@localhost:5432/postgres"
# Path to the raw CSV
RAW_CSV_PATH = "Data/healthcare_dataset.csv"


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

    if not os.path.exists(RAW_CSV_PATH):
        print(f"❌ CSV not found at {RAW_CSV_PATH}")
        return

    # 2. Read raw CSV
    print(f"📂 Reading raw data from {RAW_CSV_PATH} ...")
    df = pd.read_csv(RAW_CSV_PATH)
    print("Raw shape:", df.shape)

    # 3. Rename columns from original headers → snake_case
    df = df.rename(columns={
        "Name": "patient_name",
        "Age": "age",
        "Gender": "gender",
        "Blood Type": "blood_type",
        "Doctor": "doctor_name",
        "Hospital": "hospital_name",
        "Insurance Provider": "insurance_provider",
        "Medical Condition": "condition_name",
        "Date of Admission": "date_of_admission",
        "Discharge Date": "discharge_date",
        "Room Number": "room_number",
        "Admission Type": "admission_type",
        "Billing Amount": "billing_amount",
        "Medication": "medication_name",
        "Test Results": "test_result",
    })

    # 4. Basic cleaning / type conversions
    for col in ["date_of_admission", "discharge_date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "billing_amount" in df.columns:
        df["billing_amount"] = pd.to_numeric(df["billing_amount"], errors="coerce")
        df = df[df["billing_amount"] > 0]

    for col in ["admission_type", "test_result"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    print("After basic cleaning:", df.shape)

    # =========================================================
    # 5. Dimension tables (built from the cleaned dataframe)
    # =========================================================

    # 5.1 Patient dimension
    patient_df = (
        df[["patient_name", "age", "gender", "blood_type"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    patient_df = patient_df.rename(columns={
        "patient_name": "name"
    })
    patient_df.insert(0, "patient_id", range(1, len(patient_df) + 1))
    print("Patients:", patient_df.shape)

    # Mapping (name, age, gender, blood_type) -> patient_id
    patient_key = patient_df.set_index(
        ["name", "age", "gender", "blood_type"]
    )["patient_id"].to_dict()

    # 5.2 Doctor dimension
    doctor_df = (
        df[["doctor_name"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    doctor_df.insert(0, "doctor_id", range(1, len(doctor_df) + 1))
    print("Doctors:", doctor_df.shape)

    doctor_key = doctor_df.set_index("doctor_name")["doctor_id"].to_dict()

    # 5.3 Hospital dimension
    hospital_df = (
        df[["hospital_name"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    hospital_df.insert(0, "hospital_id", range(1, len(hospital_df) + 1))
    print("Hospitals:", hospital_df.shape)

    hospital_key = hospital_df.set_index("hospital_name")["hospital_id"].to_dict()

    # 5.4 Insurance Provider dimension
    insurance_df = (
        df[["insurance_provider"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    insurance_df = insurance_df.rename(columns={
        "insurance_provider": "provider_name"
    })
    insurance_df.insert(0, "insurance_id", range(1, len(insurance_df) + 1))
    print("Insurance providers:", insurance_df.shape)

    insurance_key = insurance_df.set_index("provider_name")["insurance_id"].to_dict()

    # 5.5 Medical Condition dimension
    condition_df = (
        df[["condition_name"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    condition_df.insert(0, "condition_id", range(1, len(condition_df) + 1))
    print("Medical conditions:", condition_df.shape)

    condition_key = condition_df.set_index("condition_name")["condition_id"].to_dict()

    # 5.6 Medication dimension
    medication_df = (
        df[["medication_name"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )
    medication_df.insert(0, "medication_id", range(1, len(medication_df) + 1))
    print("Medications:", medication_df.shape)

    medication_key = medication_df.set_index("medication_name")["medication_id"].to_dict()

    # =========================================================
    # 6. Fact table: Admission / Visit
    # =========================================================
    admission_df = df[[
        "patient_name",
        "age",
        "gender",
        "blood_type",
        "doctor_name",
        "hospital_name",
        "insurance_provider",
        "condition_name",
        "date_of_admission",
        "discharge_date",
        "room_number",
        "admission_type",
        "billing_amount",
        "medication_name",
    ]].copy()

    # Map natural keys → surrogate IDs
    admission_df["patient_id"] = admission_df[[
        "patient_name", "age", "gender", "blood_type"
    ]].apply(
        lambda row: patient_key.get(
            (row["patient_name"], row["age"], row["gender"], row["blood_type"])
        ),
        axis=1,
    )
    admission_df["doctor_id"] = admission_df["doctor_name"].map(doctor_key)
    admission_df["hospital_id"] = admission_df["hospital_name"].map(hospital_key)
    admission_df["insurance_id"] = admission_df["insurance_provider"].map(
        lambda x: insurance_key.get(x)
    )
    admission_df["condition_id"] = admission_df["condition_name"].map(condition_key)
    admission_df["medication_id"] = admission_df["medication_name"].map(medication_key)

    # Drop rows where any FK mapping failed (should normally be none)
    admission_df = admission_df.dropna(
        subset=["patient_id", "doctor_id", "hospital_id",
                "insurance_id", "condition_id"]
    )

    # Surrogate admission_id
    admission_df.insert(0, "admission_id", range(1, len(admission_df) + 1))

    # Final columns that match the admission table schema
    admission_df = admission_df[[
        "admission_id",
        "patient_id",
        "doctor_id",
        "hospital_id",
        "insurance_id",
        "condition_id",
        "medication_id",       # remove this line if your table has no medication_id FK
        "date_of_admission",
        "discharge_date",
        "room_number",
        "admission_type",
        "billing_amount",
    ]]

    print("Admissions (fact):", admission_df.shape)

    # =========================================================
    # 7. Test Result table
    # =========================================================
    if "test_result" in df.columns:
        test_result_df = df[["test_result"]].copy().reset_index(drop=True)
        test_result_df.insert(0, "test_result_id", range(1, len(test_result_df) + 1))
        # Align admission_id 1:1 with original row order
        test_result_df["admission_id"] = admission_df["admission_id"].values
        test_result_df = test_result_df[["test_result_id", "admission_id", "test_result"]]
        print("Test results:", test_result_df.shape)
    else:
        test_result_df = None
        print("No 'test_result' column found; skipping test_result table.")

    # =========================================================
    # 8. Write everything to PostgreSQL
    # =========================================================
    try:
        with engine.begin() as conn:
            print("🧱 Inserting patients...")
            patient_df.to_sql("patient", conn, if_exists="append", index=False)

            print("🧱 Inserting doctors...")
            doctor_df.to_sql("doctor", conn, if_exists="append", index=False)

            print("🧱 Inserting hospitals...")
            hospital_df.to_sql("hospital", conn, if_exists="append", index=False)

            print("🧱 Inserting insurance providers...")
            insurance_df.to_sql("insurance_provider", conn, if_exists="append", index=False)

            print("🧱 Inserting medical conditions...")
            condition_df.to_sql("medical_condition", conn, if_exists="append", index=False)

            print("🧱 Inserting medications...")
            medication_df.to_sql("medication", conn, if_exists="append", index=False)

            print("🧱 Inserting admissions...")
            admission_df.to_sql("admission", conn, if_exists="append", index=False)

            if test_result_df is not None:
                print("🧱 Inserting test results...")
                test_result_df.to_sql("test_result", conn, if_exists="append", index=False)

        print("🎉 Data ingestion completed successfully.")

    except SQLAlchemyError as e:
        print("❌ Error while inserting into PostgreSQL:")
        print(e)


if __name__ == "__main__":
    main()
