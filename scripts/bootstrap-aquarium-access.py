"""Development SQL access bootstrap; read-only by default, Entra tokens held in memory."""
import argparse
import json
import os
import struct
import subprocess
import uuid
from pathlib import Path

SUBSCRIPTION = '9671ac36-9800-451a-b283-35ea87f8b419'
TENANT = 'f4fcd45c-104f-4dd3-b7bf-3475e83ce097'
ROOT = Path(__file__).resolve().parents[1]


def az(*args):
    completed = subprocess.run(['az', *args, '--only-show-errors', '-o', 'json'], capture_output=True, text=True, shell=os.name == 'nt')
    if completed.returncode:
        raise RuntimeError('Azure CLI operation failed; credential output suppressed.')
    return json.loads(completed.stdout)


def connect():
    import pyodbc
    account = az('account', 'show')
    if account['id'] != SUBSCRIPTION or account['tenantId'] != TENANT:
        raise RuntimeError('Unexpected Azure tenant/subscription.')
    identity = az('webapp', 'show', '--subscription', SUBSCRIPTION, '-g', 'rg-parameterpilot-dev', '-n', 'api-adt-aquarium-dev')['identity']['principalId']
    identity = str(uuid.UUID(identity))
    principal = az('ad', 'sp', 'show', '--id', identity)
    if principal['id'] != identity:
        raise RuntimeError('Managed identity object mismatch')
    client_id = str(uuid.UUID(principal['appId']))
    token = az('account', 'get-access-token', '--resource', 'https://database.windows.net/')['accessToken'].encode('utf-16-le')
    packed = struct.pack('<I', len(token)) + token
    connection = pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:sql-adt-platform-dev.database.windows.net,1433;Database=ReferenceProjectsDb;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;', attrs_before={1256: packed}, autocommit=True, timeout=30)
    return connection, identity, client_id


def verify(cursor):
    checks = {}
    suffix = uuid.uuid4().hex[:12]
    probe = '[Aquarium].[__AccessProbe_' + suffix + ']'
    history = '[Aquarium].[__MigrationProbe_' + suffix + ']'
    others = list(cursor.execute("SELECT s.name,t.name FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id WHERE s.name IN (N'BlastPlanning',N'ticketing')"))
    impersonated = False
    try:
        cursor.execute('SET XACT_ABORT OFF; BEGIN TRANSACTION;')
        cursor.execute('CREATE TABLE ' + probe + ' (Id int NOT NULL PRIMARY KEY, Value int NOT NULL);')
        cursor.execute('CREATE TABLE ' + history + ' (Id int NOT NULL);')
        cursor.execute('GRANT SELECT, INSERT, UPDATE, DELETE ON OBJECT::' + probe + ' TO [AquariumRuntime];')
        cursor.execute("EXECUTE AS USER = N'api-adt-aquarium-dev';")
        impersonated = True
        cursor.execute('INSERT INTO ' + probe + ' VALUES (1,10);')
        cursor.execute('UPDATE ' + probe + ' SET Value=11 WHERE Id=1;')
        checks['objectScopedCrudAllowed'] = cursor.execute('SELECT Value FROM ' + probe + ' WHERE Id=1').fetchone()[0] == 11
        cursor.execute('DELETE FROM ' + probe + ' WHERE Id=1;')
        checks['deleteAllowed'] = cursor.execute('SELECT COUNT(*) FROM ' + probe).fetchone()[0] == 0
        checks['noDatabaseOwner'] = cursor.execute("SELECT IS_ROLEMEMBER('db_owner')").fetchone()[0] == 0
        checks['noDatabaseWideReaderWriter'] = tuple(cursor.execute("SELECT IS_ROLEMEMBER('db_datareader'),IS_ROLEMEMBER('db_datawriter')").fetchone()) == (0, 0)
        checks['noMigrationRole'] = cursor.execute("SELECT IS_ROLEMEMBER('AquariumMigrations')").fetchone()[0] == 0
        def denied(statement):
            import pyodbc
            try:
                cursor.execute(statement)
            except pyodbc.Error as error:
                return any('(' + str(code) + ')' in str(error) for code in [229, 262, 2760, 15151])
            return False
        checks['migrationProbeReadDenied'] = denied('SELECT TOP(0) * FROM ' + history)
        checks['migrationProbeWriteDenied'] = denied('INSERT INTO ' + history + ' VALUES (1)')
        checks['ddlDenied'] = denied('CREATE TABLE [Aquarium].[__Forbidden_' + suffix + '] (Id int)')
        for schema, table in others:
            quoted = '[' + schema.replace(']', ']]') + '].[' + table.replace(']', ']]') + ']'
            checks['crossProductDenied:' + schema + '.' + table] = denied('SELECT TOP(0) * FROM ' + quoted)
        for permission in ['ALTER ANY USER', 'ALTER ANY ROLE', 'ALTER ANY SCHEMA', 'CONTROL', 'CREATE TABLE']:
            checks['databaseDenied:' + permission] = cursor.execute("SELECT HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE',?)", permission).fetchone()[0] == 0
    finally:
        if impersonated:
            cursor.execute('REVERT;')
        cursor.execute('IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION; SET XACT_ABORT ON;')
    if not all(checks.values()):
        raise RuntimeError('SQL permission verification failed: ' + json.dumps(checks))
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--repair-legacy-object-id-sid', action='store_true', help='Repair only the known previous object-ID mapping, preserving runtime-only role membership')
    parser.add_argument('--verify', action='store_true', help='Use synthetic objects and grants inside a rolled-back transaction')
    parser.add_argument('--evidence', type=Path)
    args = parser.parse_args()
    connection, identity, client_id = connect()
    with connection:
        cursor = connection.cursor()
        if args.repair_legacy_object_id_sid:
            if not args.apply:
                parser.error('Repair requires --apply')
            existing = cursor.execute("SELECT CONVERT(varchar(36),CONVERT(uniqueidentifier,sid)),type FROM sys.database_principals WHERE name=N'api-adt-aquarium-dev'").fetchone()
            if existing and existing[0].lower() == identity and existing[1] == 'E':
                roles = [r[0] for r in cursor.execute("SELECT r.name FROM sys.database_role_members m JOIN sys.database_principals r ON m.role_principal_id=r.principal_id WHERE m.member_principal_id=DATABASE_PRINCIPAL_ID(N'api-adt-aquarium-dev')")]
                owned = cursor.execute("SELECT (SELECT COUNT(*) FROM sys.schemas WHERE principal_id=DATABASE_PRINCIPAL_ID(N'api-adt-aquarium-dev')) + (SELECT COUNT(*) FROM sys.objects WHERE principal_id=DATABASE_PRINCIPAL_ID(N'api-adt-aquarium-dev'))").fetchone()[0]
                direct = [tuple(r) for r in cursor.execute("SELECT permission_name,state_desc FROM sys.database_permissions WHERE grantee_principal_id=DATABASE_PRINCIPAL_ID(N'api-adt-aquarium-dev')")]
                if roles != ['AquariumRuntime'] or owned != 0 or direct != [('CONNECT','GRANT')]:
                    raise RuntimeError('Unexpected legacy user ownership/permissions; repair refused')
                sid = '0x' + uuid.UUID(client_id).bytes_le.hex()
                cursor.execute("SET XACT_ABORT ON; BEGIN TRANSACTION; DROP USER [api-adt-aquarium-dev]; CREATE USER [api-adt-aquarium-dev] WITH SID=" + sid + ", TYPE=E, DEFAULT_SCHEMA=[Aquarium]; GRANT CONNECT TO [api-adt-aquarium-dev]; ALTER ROLE [AquariumRuntime] ADD MEMBER [api-adt-aquarium-dev]; COMMIT TRANSACTION;")
        if args.apply:
            text = (ROOT / 'infra/sql/001-bootstrap-aquarium-access.sql').read_text(encoding='utf-8').replace('$(AquariumClientId)', client_id)
            cursor.execute(text)
            while cursor.nextset():
                pass
        row = cursor.execute("SELECT CONVERT(varchar(36),CONVERT(uniqueidentifier,sid)),type_desc FROM sys.database_principals WHERE name=N'api-adt-aquarium-dev'").fetchone()
        checks = verify(cursor) if args.verify else None
        runtime_roles = [r[0] for r in cursor.execute("SELECT r.name FROM sys.database_role_members m JOIN sys.database_principals r ON m.role_principal_id=r.principal_id WHERE m.member_principal_id=DATABASE_PRINCIPAL_ID(N'api-adt-aquarium-dev')")]
        migration_members = cursor.execute("SELECT COUNT(*) FROM sys.database_role_members WHERE role_principal_id=DATABASE_PRINCIPAL_ID(N'AquariumMigrations')").fetchone()[0]
        schema_objects = cursor.execute("SELECT COUNT(*) FROM sys.objects WHERE schema_id=SCHEMA_ID(N'Aquarium') AND is_ms_shipped=0").fetchone()[0]
        persisted_object_grants = cursor.execute("SELECT COUNT(*) FROM sys.database_permissions WHERE grantee_principal_id=DATABASE_PRINCIPAL_ID(N'AquariumRuntime') AND class=1").fetchone()[0]
        if row and set(runtime_roles) != {'AquariumRuntime'}:
            raise RuntimeError('Unexpected runtime role membership')
        result = {'mode': 'Applied' if args.apply else 'ReadOnly', 'principalObjectId': identity, 'clientId': client_id, 'containedUser': {'sidClientId': row[0], 'type': row[1]} if row else None, 'permissionChecksUnderExecuteAs': checks, 'remaining': 'No domain tables, production object DML grants or migration principal; actual managed-identity SQL login not tested', 'syntheticProbeTransaction': 'Rolled back' if args.verify else 'Not run', 'runtimeRoles': runtime_roles, 'migrationRoleMemberCount': migration_members, 'aquariumSchemaObjectCount': schema_objects, 'persistedRuntimeObjectGrantCount': persisted_object_grants}
        if row and row[0].lower() != client_id:
            raise RuntimeError('SQL identity SID mismatch')
        if args.evidence:
            args.evidence.parent.mkdir(parents=True, exist_ok=True)
            args.evidence.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(result, indent=2))
    connection.close()


if __name__ == '__main__':
    main()
