-- Drop tables in FK-safe order
DROP TABLE IF EXISTS test_result CASCADE;
DROP TABLE IF EXISTS admission CASCADE;
DROP TABLE IF EXISTS medication CASCADE;
DROP TABLE IF EXISTS medical_condition CASCADE;
DROP TABLE IF EXISTS insurance_provider CASCADE;
DROP TABLE IF EXISTS hospital CASCADE;
DROP TABLE IF EXISTS doctor CASCADE;
DROP TABLE IF EXISTS patient CASCADE;

-- =========================
-- Dimension tables
-- =========================

-- Patient
CREATE TABLE patient (
    patient_id   SERIAL PRIMARY KEY,
    name         TEXT NOT NULL,
    age          INT  NOT NULL CHECK (age >= 0),
    gender       TEXT NOT NULL,
    blood_type   TEXT NOT NULL
);

-- Doctor
CREATE TABLE doctor (
    doctor_id   SERIAL PRIMARY KEY,
    doctor_name TEXT NOT NULL UNIQUE
);

-- Hospital
CREATE TABLE hospital (
    hospital_id   SERIAL PRIMARY KEY ,
    hospital_name TEXT NOT NULL UNIQUE
);

-- Insurance Provider
CREATE TABLE insurance_provider (
    insurance_id  SERIAL PRIMARY KEY,
    provider_name TEXT NOT NULL UNIQUE
);

-- Medical Condition
CREATE TABLE medical_condition (
    condition_id   SERIAL PRIMARY KEY ,
    condition_name TEXT NOT NULL UNIQUE
);

-- Medication
CREATE TABLE medication (
    medication_id   SERIAL PRIMARY KEY ,
    medication_name TEXT NOT NULL UNIQUE
);

-- =========================
-- Fact table: Admission / Visit
-- =========================

CREATE TABLE admission (
    admission_id      BIGSERIAL PRIMARY KEY,
    patient_id        INT NOT NULL REFERENCES patient(patient_id),
    doctor_id         INT NOT NULL REFERENCES doctor(doctor_id),
    hospital_id       INT NOT NULL REFERENCES hospital(hospital_id),
    insurance_id      INT NOT NULL REFERENCES insurance_provider(insurance_id),
    condition_id      INT NOT NULL REFERENCES medical_condition(condition_id),
    medication_id     INT REFERENCES medication(medication_id),
    date_of_admission TIMESTAMPTZ NOT NULL,
    discharge_date    TIMESTAMPTZ,
    room_number       INT,
    admission_type    TEXT NOT NULL,
    billing_amount    NUMERIC(12,2) NOT NULL CHECK (billing_amount > 0)
);

-- =========================
-- Test result table
-- =========================

CREATE TABLE test_result (
    test_result_id BIGSERIAL PRIMARY KEY,
    admission_id   BIGINT NOT NULL REFERENCES admission(admission_id),
    test_result    TEXT NOT NULL
);
