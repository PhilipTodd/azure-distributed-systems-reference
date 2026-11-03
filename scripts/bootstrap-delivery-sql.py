"""Controlled PP migration/developer SQL setup. Read-only unless --apply.

Uses the owner's short-lived Entra token; never SQL passwords. Domain grants are
not invented: later migrations supply reviewed object permission manifests.
"""
import argparse
import json
import uuid
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('delivery', ROOT / 'scripts/bootstrap-delivery-access.py')
delivery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delivery)


def setup(connection, state, apply):
    cursor = connection.cursor()
    if cursor.execute('SELECT DB_NAME()').fetchone()[0] != 'ReferenceProjectsDb':
        raise RuntimeError('Unexpected database')
    principals = [
        ('github-parameterpilot-migrations-dev', state['applications']['dev-migrations']['clientId'], 'E', 'AquariumMigrations'),
        ('sg-adt-parameterpilot-developers-dev', state['developerGroup']['objectId'], 'X', 'AquariumDeveloper'),
    ]
    result = {'applied': apply, 'principals': [], 'checks': {}, 'verificationMethod': 'SQL EXECUTE AS migration user and disposable developer-role user; group/OIDC authentication not exercised'}
    cursor.execute('SET XACT_ABORT ON; BEGIN TRANSACTION;')
    try:
        if not cursor.execute("SELECT 1 FROM sys.database_principals WHERE name=N'AquariumMigrations' AND type='R'").fetchone():
            raise RuntimeError('Expected migration role absent')
        if not cursor.execute("SELECT 1 FROM sys.schemas WHERE name=N'Aquarium' AND principal_id=DATABASE_PRINCIPAL_ID(N'AquariumSchemaOwner')").fetchone():
            raise RuntimeError('Expected isolated schema owner absent')
        if not cursor.execute("SELECT 1 FROM sys.database_principals WHERE name=N'AquariumDeveloper'").fetchone():
            cursor.execute('CREATE ROLE [AquariumDeveloper] AUTHORIZATION [dbo];')
        for name, identity, kind, role in principals:
            sid = uuid.UUID(identity).bytes_le
            existing = cursor.execute('SELECT type,sid FROM sys.database_principals WHERE name=?', name).fetchone()
            if existing and (existing[0] != kind or bytes(existing[1]) != sid):
                raise RuntimeError('Existing SQL principal mapping mismatch')
            if existing:
                memberships = [row[0] for row in cursor.execute('SELECT r.name FROM sys.database_role_members m JOIN sys.database_principals r ON r.principal_id=m.role_principal_id WHERE m.member_principal_id=DATABASE_PRINCIPAL_ID(?)', name)]
                if any(member != role for member in memberships):
                    raise RuntimeError('Unexpected existing SQL role membership')
                if cursor.execute('SELECT 1 FROM sys.schemas WHERE principal_id=DATABASE_PRINCIPAL_ID(?)', name).fetchone():
                    raise RuntimeError('Unexpected schema ownership')
            else:
                cursor.execute(f'CREATE USER [{name}] WITH SID=0x{sid.hex()}, TYPE={kind}, DEFAULT_SCHEMA=[Aquarium];')
            cursor.execute(f'GRANT CONNECT TO [{name}];')
            cursor.execute(f"IF NOT EXISTS(SELECT 1 FROM sys.database_role_members WHERE role_principal_id=DATABASE_PRINCIPAL_ID(N'{role}') AND member_principal_id=DATABASE_PRINCIPAL_ID(N'{name}')) ALTER ROLE [{role}] ADD MEMBER [{name}];")
            result['principals'].append({'name': name, 'identityId': identity, 'type': kind, 'role': role})
        # No grants to real tables or migration history. Probe transaction rolls back.
        result['checks'] = verify(cursor)
        cursor.execute('COMMIT TRANSACTION;' if apply else 'ROLLBACK TRANSACTION;')
    except Exception:
        cursor.execute('IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;')
        raise
    return result


def verify(cursor):
    checks = {}
    suffix = uuid.uuid4().hex[:10]
    table = '[Aquarium].[__MigrationAccess_' + suffix + ']'
    # SAVE TRANSACTION isolates probe objects/grants from the real bootstrap.
    cursor.execute('SAVE TRANSACTION DeliveryProbe; SET XACT_ABORT OFF;')
    impersonated = False
    try:
        cursor.execute("EXECUTE AS USER=N'github-parameterpilot-migrations-dev';")
        impersonated = True
        cursor.execute('CREATE TABLE ' + table + ' (Id int NOT NULL);')
        cursor.execute('ALTER TABLE ' + table + ' ADD Value int NULL;')
        checks['migrationCreateAlterAquarium'] = True
        checks['migrationNoDbOwner'] = cursor.execute("SELECT IS_ROLEMEMBER('db_owner')").fetchone()[0] == 0
        for permission in ['ALTER ANY USER', 'ALTER ANY ROLE', 'ALTER ANY SCHEMA', 'CONTROL']:
            checks['migrationDeniedDatabase:' + permission] = cursor.execute("SELECT HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE',?)", permission).fetchone()[0] == 0
        checks['migrationDeniedDboAlter'] = cursor.execute("SELECT COALESCE(HAS_PERMS_BY_NAME('dbo','SCHEMA','ALTER'),0)").fetchone()[0] == 0
        others = list(cursor.execute("SELECT name FROM sys.schemas WHERE name IN (N'BlastPlanning',N'ticketing')"))
        for row in others:
            checks['migrationDeniedOtherSchema:' + row[0]] = cursor.execute("SELECT COALESCE(HAS_PERMS_BY_NAME(?,'SCHEMA','ALTER'),0)", row[0]).fetchone()[0] == 0
        cursor.execute('DROP TABLE ' + table + '; REVERT;')
        impersonated = False
        cursor.execute('CREATE TABLE ' + table + ' (Id int NOT NULL); INSERT INTO ' + table + ' VALUES (1);')
        cursor.execute('GRANT SELECT ON OBJECT::' + table + ' TO [AquariumDeveloper];')
        # Entra groups cannot be impersonated. Exercise the exact developer role
        # through a disposable WITHOUT LOGIN user, never the privileged owner.
        cursor.execute(f'CREATE USER [__DeveloperProbe_{suffix}] WITHOUT LOGIN; ALTER ROLE [AquariumDeveloper] ADD MEMBER [__DeveloperProbe_{suffix}];')
        cursor.execute(f"EXECUTE AS USER=N'__DeveloperProbe_{suffix}';")
        impersonated = True
        checks['developerObjectSelect'] = cursor.execute('SELECT Id FROM ' + table).fetchone()[0] == 1
        for permission in ['INSERT', 'UPDATE', 'DELETE', 'ALTER', 'CONTROL']:
            checks['developerDeniedObject:' + permission] = cursor.execute("SELECT HAS_PERMS_BY_NAME(?,'OBJECT',?)", 'Aquarium.__MigrationAccess_' + suffix, permission).fetchone()[0] == 0
        for permission in ['CREATE TABLE', 'ALTER ANY USER', 'ALTER ANY ROLE', 'CONTROL']:
            checks['developerDeniedDatabase:' + permission] = cursor.execute("SELECT HAS_PERMS_BY_NAME(DB_NAME(),'DATABASE',?)", permission).fetchone()[0] == 0
        checks['developerNoMigrationRole'] = cursor.execute("SELECT IS_ROLEMEMBER('AquariumMigrations')").fetchone()[0] == 0
        cursor.execute('REVERT;')
        impersonated = False
    finally:
        if impersonated:
            cursor.execute('REVERT;')
        cursor.execute('IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION DeliveryProbe; SET XACT_ABORT ON;')
    if not all(checks.values()):
        raise RuntimeError('SQL verification failed: ' + json.dumps(checks))
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    delivery.require_account()
    state = json.loads(delivery.EVIDENCE.read_text(encoding='utf-8'))
    probe_spec = importlib.util.spec_from_file_location('probe', ROOT / 'scripts/run-workload-access-verification.py')
    probe = importlib.util.module_from_spec(probe_spec)
    probe_spec.loader.exec_module(probe)
    with probe.sql_connect() as connection:
        result = setup(connection, state, args.apply)
    if args.apply:
        path = ROOT / 'docs/infrastructure/evidence/delivery-sql-access-2026-11-03.json'
        path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
