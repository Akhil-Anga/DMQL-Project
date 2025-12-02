## 1. Purpose of the Star Schema

The OLTP database designed in Phase 1 is fully normalized (3NF) and optimized for transactional workloads.
For analytical workloads (OLAP), however, a denormalized star schema provides:

-> Faster aggregations

-> Simpler analytical queries

-> Clearer dimensional structure

-> Better compatibility with BI tools (Tableau, PowerBI, dbt)

This document defines the star schema used for the analytical layer of the healthcare admissions dataset.

## 2. Grain of the Fact Table

Grain (very important):

Each row in the fact table represents one hospital admission (one visit by one patient).

All measures and foreign keys relate to this specific event.

This grain is consistent, atomic, and supports all analytical questions such as:

-> total billing by month/hospital

-> readmissions within 30 days

-> length of stay trends

-> condition-wise patient distribution

-> insurance usage patterns

## 3. Fact Table: fact_admission
### 3.1 Fact Table Columns
Column	Description
admission_id	Surrogate key (one row per admission)
patient_id	FK → dim_patient
doctor_id	FK → dim_doctor
hospital_id	FK → dim_hospital
insurance_id	FK → dim_insurance_provider
condition_id	FK → dim_medical_condition
medication_id	FK → dim_medication
date_of_admission	Admission date
discharge_date	Discharge date
admission_type	Emergency / Elective / Routine
room_number	Hospital room info
billing_amount	Numerical measure
length_of_stay_days	Derived measure: discharge - admission

### 3.2 Measures
-> billing_amount (numeric)
-> length_of_stay_days (derived)
-> Additional derived metrics can be added later (e.g., readmission flag)

## 4. Dimension Tables
### 4.1 dim_patient
Describes demographic information about each patient.

Column	Description
patient_id	PK
name	Cleaned patient name
age	Age at admission
gender	Male/Female/Other
blood_type	A+, O-, etc.
age_group	(Optional) derived bucket for analytics

### 4.2 dim_doctor
Describes doctors involved in patient admissions.

Column	Description
doctor_id	PK
doctor_name	Name

### 4.3 dim_hospital
Describes hospital facilities.

Column	Description
hospital_id	PK
hospital_name	Name

### 4.4 dim_insurance_provider
Describes insurance companies covering the admission.

Column	Description
insurance_id	PK
provider_name	Name

### 4.5 dim_medical_condition
Describes the primary condition that led to the hospital visit.

Column	Description
condition_id	PK
condition_name	Name

### 4.6 dim_medication
Describes medication prescribed during the admission.

Column	Description
medication_id	PK
medication_name	Name

### 4.7 dim_date (Optional but highly recommended)
Used for time-series analytics.

Can be used twice:

-> admit_date_key

-> discharge_date_key

Common attributes:

Column	Description
date_key	Integer key (YYYYMMDD)
date	Actual date
year	Year
month	Month (1–12)
day	Day of month
day_of_week	Monday, etc.
quarter	Q1–Q4

## 5. Star Schema Diagram (Text Description)
```
                    dim_patient
                         |
                         |
 dim_doctor ---- fact_admission ---- dim_hospital
                         |
                         |
        dim_medical_condition     dim_insurance_provider
                         |
                         |
                     dim_medication

               (Optional foreign keys)
                 fact_admission
                     |       |
                 dim_date  dim_date
               (admit)    (discharge)
```


You can recreate this diagram visually and save it as
erd/star_schema.png

## 6. Why This Schema Works for OLAP
-> Denormalized structure reduces join cost.

-> Fact table grain is clear and consistent.

-> Dimensions allow slicing the data by:

    patient demographics

    doctor

    hospital

    insurer

    condition

    medication

    date

-> Optimized for:

    aggregations

    dashboards

    BI reporting

    machine learning features (e.g., length of stay)

This design mirrors industry-standard healthcare analytical systems.

## 7. Summary
This OLAP star schema transforms the normalized OLTP dataset into a format suitable for advanced analytics.
The warehouse enables fast reporting, supports advanced SQL (window functions, rollups), and integrates smoothly with dbt and BI platforms.
