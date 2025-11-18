Healthcare Appointment No-Show — Phase 1
 --> Project Overview

This project builds the OLTP foundation for analyzing patient appointments and no-show behavior using the Medical Appointment No-Show Dataset.

Phase 1 focuses on:
-> Designing a normalized relational schema (3NF)
-> Implementing the schema in PostgreSQL
-> Building a Python ingestion pipeline using Pandas + SQLAlchemy
-> Running validation tests to ensure data quality
-> Setting up Role-Based Access Control (RBAC)

This project corresponds to Phase 1 of our DMQL course project.


⚙️ Phase 1 — How to Run Everything
1. Install Dependencies

Create/activate your virtual environment:

python3 -m venv .venv
source .venv/bin/activate

Install requirements:
pip install -r requirements.txt

2. Start PostgreSQL + pgAdmin with Docker

From the project root:
docker compose up -d
docker compose down -v

Verify containers:

docker ps

You should see:

-> healthcare_db
-> pgadmin_ui

3. Test Database Connection
python test_connection.py

Expected:
-> Attempting to connect…
Database connection successful: Connection OK

4. Run the Data Ingestion Pipeline
python ingest_data.py

This script:

Loads raw data (Data/Healthcare.csv)

Splits into normalized tables

Inserts into PostgreSQL in the correct order:

-> neighborhood
-> patient
-> appointment

Expected summary:

Inserting neighborhoods...
Inserting patients...
Inserting appointments...
Data ingestion completed successfully.

5. Run Full Validation Tests
python test.py


Includes:
-> Table existence check
-> Row counts
-> Foreign key integrity
-> A sample analytical query (top 5 no-show neighborhoods)

Example output:

neighborhood: 81 rows
patient: 62298 rows
appointment: 110521 rows
All appointments have a valid patient_id

6. Check DB Using pgAdmin

Open:

http://localhost:8080


Login (from docker-compose):

Email: admin@admin.com

Password: admin123

Add server:

Host: db

User: admin

Password: admin123

Use SQL to inspect tables:

SELECT * FROM appointment LIMIT 10;

7. Apply RBAC
docker exec -it healthcare_db psql -U admin -d healthcare_db -f /docker-entrypoint-initdb.d/security.sql


Roles included:

analyst (read-only)

app_user (read-write)

-> ERD (Crow’s Foot Notation)

Your ERD describes a fully normalized 3NF schema:

neighborhood   1 ───< patient   1 ───< appointment


See ERD/erd.png for the full diagram.

📊 3NF Justification (Summary)

1NF:
All attributes are atomic (no repeating groups, no multivalued fields).

2NF:
No partial dependencies (all tables have single-column PKs).

3NF:
All non-key attributes depend on the key, the whole key, and nothing but the key:

patient attributes depend only on patient_id

appointment attributes depend on appointment_id

neighborhood name depends on neighborhood_id

This eliminates insertion, deletion, and update anomalies from the original flat CSV file.