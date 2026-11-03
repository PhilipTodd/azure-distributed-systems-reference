-- Development bootstrap only. Run through scripts/bootstrap-aquarium-access.py.
-- This creates security objects, not domain tables or application migrations.
SET NOCOUNT ON;
SET XACT_ABORT ON;
IF DB_NAME() <> N'ReferenceProjectsDb'
    THROW 51000, 'Unexpected database; bootstrap refused.', 1;
DECLARE @clientId uniqueidentifier = '$(AquariumClientId)';
IF @clientId = '00000000-0000-0000-0000-000000000000'
    THROW 51000, 'A verified managed identity is required.', 1;
BEGIN TRANSACTION;
IF DATABASE_PRINCIPAL_ID(N'AquariumSchemaOwner') IS NULL
    CREATE ROLE [AquariumSchemaOwner] AUTHORIZATION [dbo];
IF SCHEMA_ID(N'Aquarium') IS NULL
    EXEC(N'CREATE SCHEMA [Aquarium] AUTHORIZATION [AquariumSchemaOwner]');
IF (SELECT principal_id FROM sys.schemas WHERE name=N'Aquarium') <> DATABASE_PRINCIPAL_ID(N'AquariumSchemaOwner')
    THROW 51000, 'Existing Aquarium schema has another owner; no reassignment performed.', 1;
IF DATABASE_PRINCIPAL_ID(N'AquariumRuntime') IS NULL
    CREATE ROLE [AquariumRuntime] AUTHORIZATION [dbo];
IF DATABASE_PRINCIPAL_ID(N'AquariumMigrations') IS NULL
    CREATE ROLE [AquariumMigrations] AUTHORIZATION [dbo];
IF EXISTS(SELECT 1 FROM sys.database_principals WHERE name IN (N'AquariumSchemaOwner',N'AquariumRuntime',N'AquariumMigrations') AND type <> 'R')
    THROW 51000, 'Conflicting security principal; bootstrap refused.', 1;
IF DATABASE_PRINCIPAL_ID(N'api-adt-aquarium-dev') IS NULL
BEGIN
    -- For managed identities SID is the verified client/application ID, not the object ID.
    -- SID/TYPE avoids granting broad Microsoft Graph permissions to the SQL server.
    DECLARE @create nvarchar(max) = N'CREATE USER [api-adt-aquarium-dev] WITH SID = '
        + CONVERT(varchar(34), CONVERT(binary(16), @clientId), 1)
        + N', TYPE = E, DEFAULT_SCHEMA = [Aquarium]';
    EXEC(@create);
END;
IF NOT EXISTS(SELECT 1 FROM sys.database_principals WHERE name=N'api-adt-aquarium-dev' AND type='E' AND sid=CONVERT(binary(16), @clientId))
    THROW 51000, 'Existing SQL user does not match the verified identity.', 1;
GRANT CONNECT TO [api-adt-aquarium-dev];
IF NOT EXISTS(SELECT 1 FROM sys.database_role_members WHERE role_principal_id=DATABASE_PRINCIPAL_ID(N'AquariumRuntime') AND member_principal_id=DATABASE_PRINCIPAL_ID(N'api-adt-aquarium-dev'))
    ALTER ROLE [AquariumRuntime] ADD MEMBER [api-adt-aquarium-dev];
DENY CREATE TABLE, CREATE VIEW, CREATE PROCEDURE, CREATE FUNCTION, CREATE TYPE,
    ALTER ANY SCHEMA, ALTER ANY USER, ALTER ANY ROLE TO [AquariumRuntime];
DENY ALTER ON SCHEMA::[Aquarium] TO [AquariumRuntime];
-- Narrow migration capability, deliberately with no principal/member assigned.
GRANT CREATE TABLE, CREATE VIEW, CREATE PROCEDURE, CREATE FUNCTION, CREATE TYPE TO [AquariumMigrations];
GRANT ALTER ON SCHEMA::[Aquarium] TO [AquariumMigrations];
-- No schema-wide DML grants: future EF history must not become runtime-writable.
-- Add object-level runtime grants with the reviewed application migrations.
COMMIT TRANSACTION;
