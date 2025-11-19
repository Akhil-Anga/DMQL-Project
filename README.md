# Healthcare Appointment No-Show — Phase 1 (OLTP Database Foundation)

## DMQL Course Project – Phase 1 Submission

## Project Overview:

This project builds a complete OLTP (Online Transaction Processing) database foundation for analyzing patient appointment behavior using the Medical Appointment No-Show Dataset.

## Dataset Description

This project uses the **Medical Appointment No-Show Dataset** (Healthcare.csv), which contains information about patient appointments and whether the patient showed up.

- Source: Kaggle — Medical Appointment No Shows
- File used: `Data/Healthcare.csv`
- Rows: ~110,526
- Columns: 14

### Raw Attributes:
- PatientId
- AppointmentID
- Gender
- ScheduledDay
- AppointmentDay
- Age
- Neighbourhood
- Scholarship
- Hipertension
- Diabetes
- Alcoholism
- Handcap
- SMS_received
- No-show

### Why this dataset works for Phase 1:
- It is originally **denormalized** (flat CSV)
- Contains mixed data types (strings, timestamps, integers, boolean-like fields)
- Ideal for demonstrating **3NF decomposition** into:
  - Neighborhood
  - Patient
  - Appointment
- Suitable for OLTP modeling and ingestion pipelines

### Phase 1 includes:

-> Designing a normalized 3NF relational schema

-> Creating tables in PostgreSQL with proper constraints

-> Developing a Python data ingestion pipeline (Pandas + SQLAlchemy)

-> Running automated validation and diagnostic tests

-> Setting up Role-Based Access Control (RBAC) — (Bonus Completed!)

This README provides complete instructions for running, testing, and verifying Phase 1.

### How to Run Phase 1
#### 1. Install Dependencies

Create and activate a virtual environment:
```
python3 -m venv .venv
source .venv/bin/activate
```
Install all required packages:
```
pip install -r requirements.txt
```

#### 2. Start PostgreSQL + pgAdmin (Docker)

From the project root:
```
docker compose up -d
```

To stop everything:
```
docker compose down -v
```

Verify containers:
```
docker ps
```

You should see:

-> healthcare_db

-> gadmin_ui

#### 3. Test Database Connection

Run:
```
python test_connection.py
```

Expected:
```
Attempting to connect...
Database connection successful: Connection OK
```

#### 4. Run the Data Ingestion Pipeline
```
python ingest_data.py
```

This script:

-> Loads raw dataset → Data/Healthcare.csv

-> Cleans, transforms, and normalizes the data

-> Inserts into PostgreSQL in FK-safe order:

    1. neighborhood
    2. patient
    3. appointment

Expected output:
```
Inserting neighborhoods...
Inserting patients...
Inserting appointments...
Data ingestion completed successfully.
```

#### 5. Run Full Validation Tests
```
python test.py
```

This script checks:
-> Required tables exist
-> Row counts
-> Foreign key integrity
-> Sample analytical query

Example output:
```
neighborhood: 81 rows
patient: 62298 rows
appointment: 110521 rows
All appointments have a valid patient_id.
```

#### 6. View Database in pgAdmin

Open:

👉 http://localhost:8080

Login using values from docker-compose:

    -> Email: admin@admin.com

    -> Password: admin123

Run queries such as:
```
SELECT * FROM appointment LIMIT 10;
```

#### 7. Role-Based Access Control (RBAC)

Run the security script:
```
docker exec -it healthcare_db psql -U admin -d healthcare_db -f /docker-entrypoint-initdb.d/security.sql
```

Created roles:
    -> analyst — Read-Only Role
        1. Can connect
        2. Can read all tables
        3. Cannot insert/update/delete

    To test:
    ```
    SET ROLE analyst;
    SELECT * FROM patient LIMIT 5;   -- Works
    INSERT INTO patient VALUES (...); -- Fails (read-only)
    ```

    -> app_user — Read-Write Role
        1. Can connect
        2. Can SELECT, INSERT, UPDATE, DELETE
        3. Cannot create/drop tables

    To test:
    ```
    SET ROLE app_user;
    INSERT INTO neighborhood(name) VALUES ('TEST_AREA'); -- Works
    ```

Both roles are fully functional and validated in pgAdmin.

### Entity–Relationship Diagram (ERD)

The schema follows a clean Crow’s Foot notation:

Neighborhood  (1) ───< (N)  Patient  (1) ───< (N)  Appointment

See full diagram in:

ERD/erd.png

3NF Justification
1NF – Atomicity
    -> All fields contain atomic values
    -> No multi-valued or repeating attributes
    -> Timestamps, booleans, integers are all atomic

2NF – No Partial Dependencies
    -> All tables have a single-column primary key
    -> Therefore, no attribute can depend on part of a composite key

3NF – No Transitive Dependencies
    -> patient attributes depend only on patient_id
    -> appointment attributes depend only on appointment_id
    -> neighborhood.name depends only on neighborhood_id

This removes all anomalies from the raw CSV:

1. Insertion anomalies

2. Deletion anomalies

3. Update anomalies

The final schema is clean, minimal, and fully normalized.

