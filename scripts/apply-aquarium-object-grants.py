"""Apply reviewed Aquarium object grants through the owner bootstrap, not migrations.

Default is validation/preview. Manifest entries: name, type (TABLE/VIEW/PROCEDURE),
runtime (explicit permission list), developer (SELECT or empty). Empty in Stage 1.
Never grants schema-wide DML or grants rights to the migration identity.
"""
import argparse
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def statements(manifest):
    if (manifest.get('database'), manifest.get('schema'), manifest.get('runtimeRole'), manifest.get('developerRole')) != ('ReferenceProjectsDb', 'Aquarium', 'AquariumRuntime', 'AquariumDeveloper'):
        raise ValueError('Unexpected database/schema/roles')
    excluded = manifest['excludedObjects']
    if '__EFMigrationsHistory' not in excluded:
        raise ValueError('Migration history must be excluded')
    result = []
    seen = set()
    for entry in manifest['objects']:
        name = entry['name']
        if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,127}', name) or name.casefold() in {item.casefold() for item in excluded} or name.casefold() in seen:
            raise ValueError('Invalid, duplicate or excluded object')
        seen.add(name.casefold())
        kind = entry['type']
        allowed = {'TABLE': {'SELECT', 'INSERT', 'UPDATE', 'DELETE'}, 'VIEW': {'SELECT'}, 'PROCEDURE': {'EXECUTE'}}
        if kind not in allowed:
            raise ValueError('Unsupported object kind')
        for field, role in [('runtime', 'AquariumRuntime'), ('developer', 'AquariumDeveloper')]:
            permissions = entry[field]
            if len(set(permissions)) != len(permissions) or not set(permissions) <= (allowed[kind] if field == 'runtime' else {'SELECT'} & allowed[kind]):
                raise ValueError('Unapproved object permission')
            if permissions:
                result.append((name, kind, f'GRANT {", ".join(permissions)} ON OBJECT::[Aquarium].[{name}] TO [{role}];'))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
    planned = statements(manifest)
    if args.apply and planned:
        spec = importlib.util.spec_from_file_location('delivery', ROOT / 'scripts/bootstrap-delivery-access.py')
        delivery = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(delivery)
        delivery.require_account()
        spec = importlib.util.spec_from_file_location('probe', ROOT / 'scripts/run-workload-access-verification.py')
        probe = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(probe)
        with probe.sql_connect() as connection:
            cur = connection.cursor()
            if cur.execute('SELECT DB_NAME()').fetchone()[0] != manifest['database']:
                raise RuntimeError('Unexpected database')
            cur.execute('SET XACT_ABORT ON; BEGIN TRANSACTION;')
            try:
                for name, kind, sql in planned:
                    expected = {'TABLE': 'U', 'VIEW': 'V', 'PROCEDURE': 'P'}[kind]
                    actual = cur.execute('SELECT type FROM sys.objects WHERE schema_id=SCHEMA_ID(?) AND name=?', 'Aquarium', name).fetchone()
                    if not actual or actual[0].strip() != expected:
                        raise RuntimeError('Reviewed object missing/type mismatch')
                    cur.execute(sql)
                cur.execute('COMMIT TRANSACTION;')
            except Exception:
                cur.execute('IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION;')
                raise
    print(json.dumps({'apply': args.apply, 'grantCount': len(planned), 'statements': [item[2] for item in planned], 'revocations': 'Not automatic; removal from a manifest does not revoke an existing grant. Review explicit REVOKE with the corresponding migration.'}, indent=2))


if __name__ == '__main__':
    main()
