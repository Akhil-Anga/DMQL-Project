-- security.sql
-- Role-Based Access Control (RBAC) for healthcare_db (8-table schema)

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'analyst') THEN
        CREATE ROLE analyst LOGIN PASSWORD 'analyst123';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'app_user') THEN
        CREATE ROLE app_user LOGIN PASSWORD 'appuser123';
    END IF;
END
$$;

-- Restrict PUBLIC
REVOKE ALL ON DATABASE healthcare_db FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;

-- Database access
GRANT CONNECT ON DATABASE healthcare_db TO analyst, app_user;

-- Schema access
GRANT USAGE ON SCHEMA public TO analyst;
GRANT USAGE, CREATE ON SCHEMA public TO app_user;

-- Table privileges (existing tables)
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- Sequence privileges (existing sequences)
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO analyst;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE, SELECT ON SEQUENCES TO app_user;
