-- security.sql
-- Role-Based Access Control (RBAC) setup for healthcare_db

-----------------------------------------
-- 1. Create roles
-----------------------------------------

-- Read-only analyst role
CREATE ROLE analyst LOGIN PASSWORD 'analyst123';

-- Read-write application user
CREATE ROLE app_user LOGIN PASSWORD 'appuser123';

-----------------------------------------
-- 2. Revoke default PUBLIC access (optional but recommended)
-----------------------------------------
REVOKE ALL ON DATABASE healthcare_db FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;

-----------------------------------------
-- 3. Grant privileges to analyst (read-only)
-----------------------------------------

GRANT CONNECT ON DATABASE healthcare_db TO analyst;
GRANT USAGE ON SCHEMA public TO analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst;

-- Ensure future tables are also readable by analyst
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO analyst;

-----------------------------------------
-- 4. Grant privileges to app_user (read/write)
-----------------------------------------

GRANT CONNECT ON DATABASE healthcare_db TO app_user;
GRANT USAGE, CREATE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- Ensure future tables stay writable by app_user
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
