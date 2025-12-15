# Healthcare Admissions Database Schema

## DMQL Course Project

## Project Overview:

This project builds a complete OLTP (Online Transaction Processing) database foundation for analyzing patient appointment behavior using the Medical Appointment No-Show Dataset.

## Dataset Description

This project uses the **Healthcare Dataset** (Healthcare_dataset.csv), which contains information about patient appointments and whether the patient showed up.

- Source: Kaggle — Healthcare Dataset
- File used: `Data/Healthcare_dataset.csv`
- Rows: ~10,000
- Columns: 15

## This project is an end-to-end data system built in three phases:

- **Phase 1 (OLTP):** PostgreSQL OLTP schema + data ingestion
- **Phase 2 (OLAP):** dbt staging + star schema (fact/dim views) + advanced SQL + performance tuning
- **Phase 3 (Application Layer):** Streamlit Dashboard (Dockerized)

---

## 1) Tech Stack

- **PostgreSQL** (Docker)
- **pgAdmin** (Docker)
- **Python** (data ingestion script)
- **dbt-postgres** (transformations + analytical layer)
- **Phase 3 App:** Streamlit

---

## 2) Repository Structure (High Level)

- `docker-compose.yml` → spins up Postgres + pgAdmin
- `schema.sql` / `security.sql` → OLTP schema + permissions
- `ingest_data.py` → loads dataset into OLTP tables
- `dbt_healthcare/` → dbt project for transformations
- `sql/advanced_queries.sql` → advanced analytical queries
- `performance/performance_tuning.md` → performance tuning report
- `reports/star_schema.md` + `ERD/star_schema.png` → star schema documentation/diagram
- `app/` → Streamlit dashboard
---

## 3) Prerequisites

### Required
- **Docker Desktop** installed and running
- **Python 3.10+** (or Anaconda/Miniconda)
---

## 4) Phase 1 — Create Schema + Ingest Data
- From the repository root:
```
docker compose up -d
```
- Check containers:
```
docker ps
```
- Run ingestion locally
```
python ingest_data.py
python test.py
```
- pgAdmin URL + login
```
http://localhost:8080

SELECT COUNT(*) FROM public.admission
```

## Phase 2 — dbt (Analytical Layer / Star Schema)
- Create/Activate dbt environment
```
conda activate dbt_env
```
- Run dbt models
```
cd dbt_healthcare
dbt run
```
- dbt debug (proves profile + connection)
- dbt test (quality checks)

## Phase 3 — Application Layer
- Step 1 — Start all services (Postgres + pgAdmin + Streamlit)
```
docker compose up -d --build
```
- step 2 - Confirm containers are running
```
docker ps
```
- step 3 - Open the services
- Streamlit Dashboard: http://localhost:8501
- pgAdmin: http://localhost:8080
- Postgres: localhost:5432 (used internally by services + optional local access)

- step 4 - Create a .env file in the repo root
```
DB_HOST=healthcare_db
DB_PORT=5432
DB_NAME=healthcare_db
DB_USER=admin
DB_PASSWORD=admin
DB_SCHEMA=public
```

- step 5 - Start Postgres + pgAdmin
```
docker compose up -d
```

- step 6 - Ingest data into OLTP tables
```
python ingest_data.py
```

- step 7 - Build OLAP views (dbt)
```
conda activate dbt_env
cd dbt_healthcare
dbt run
```

- step 8 - Start Streamlit
```
cd ..
cd app
streamlit run app.py
```

- Note: Steps 5–8 are only required if running ingestion/dbt outside Docker. For a full one-command startup, use docker compose up -d --build.

Then open:
#### http://localhost:8501

## Screenshots & Demo Video
- 1. Streamlit Dashboard - screenshots/Dashboard_overview.png
- 2. Streamlit Dashboard – Interaction  - screenshots/Dashboard_filter_Interaction.png
- 3. Docker Containers Running - screenshots/Docker_Running & Data_Ingestion.png
- 4. pgAdmin Connected to Database - screenshots/Pageadmin_Connection.png

- Demo video link: https://youtu.be/etqXDjIADYY

## Stop / Reset the Project
 - Stop containers
 ```
docker compose down
```
 - Full reset
 ```
docker compose down -v
```
