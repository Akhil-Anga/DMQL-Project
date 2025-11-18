-- Drop tables in the right order to avoid FK issues
DROP TABLE IF EXISTS appointment CASCADE;
DROP TABLE IF EXISTS patient CASCADE;
DROP TABLE IF EXISTS neighborhood CASCADE;


-- Neighborhood table
CREATE TABLE neighborhood (
    neighborhood_id SERIAL PRIMARY KEY,
    name            TEXT NOT NULL UNIQUE
);


-- Patient table
CREATE TABLE patient (
    patient_id           BIGSERIAL PRIMARY KEY,
    external_patient_id  BIGINT NOT NULL UNIQUE,
    gender               CHAR(1) NOT NULL CHECK (gender IN ('M', 'F', 'O')),
    age_at_registration  INT NOT NULL CHECK (age_at_registration >= 0),
    neighborhood_id      INT NOT NULL REFERENCES neighborhood(neighborhood_id),
    scholarship          BOOLEAN NOT NULL,
    hypertension         BOOLEAN NOT NULL,
    diabetes             BOOLEAN NOT NULL,
    alcoholism           BOOLEAN NOT NULL,
    handicap_level       SMALLINT NOT NULL CHECK (handicap_level >= 0)
);


-- Appointment table
CREATE TABLE appointment (
    appointment_id       BIGINT PRIMARY KEY,
    patient_id           BIGINT NOT NULL REFERENCES patient(patient_id),
    scheduled_datetime   TIMESTAMPTZ NOT NULL,
    appointment_datetime TIMESTAMPTZ NOT NULL,
    sms_received         BOOLEAN NOT NULL,
    no_show              BOOLEAN NOT NULL
);
