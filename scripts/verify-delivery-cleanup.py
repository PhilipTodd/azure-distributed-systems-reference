"""Read-only final closed-host, temporary identity and SQL cleanup assertions."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('probe', ROOT / 'scripts/run-workload-access-verification.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def main():
    state = probe.load()
    if not state.get('cleaned') or state.get('modifiedRoleAssignments') or state.get('roleAssignmentIds'):
        raise RuntimeError('Verification journal still needs cleanup')
    hosts = {}
    for service in ['aquarium', 'tracking']:
        app = probe.rest('get', probe.app_id(service) + '?api-version=2024-11-01')
        config = probe.az('webapp', 'config', 'show', '-g', probe.RG, '-n', 'api-adt-' + service + '-dev')
        if app['properties']['enabled'] or app['properties']['publicNetworkAccess'] != 'Disabled':
            raise RuntimeError('Host not disabled/closed')
        if app['identity']['principalId'] != probe.IDENTITIES[service] or app['identity'].get('userAssignedIdentities'):
            raise RuntimeError('Host identity not restored')
        if config['ipSecurityRestrictionsDefaultAction'] != 'Deny' or config['scmIpSecurityRestrictionsDefaultAction'] != 'Deny':
            raise RuntimeError('Ingress default denial changed')
        for key, value in state['apps'][service]['configuration'].items():
            if config.get(key) != value:
                raise RuntimeError('Host configuration not restored')
        hosts[service] = {'enabled': False, 'publicNetworkAccess': 'Disabled', 'mainAndScmDefaultAction': 'Deny', 'systemPrincipalId': app['identity']['principalId'], 'userAssignedIdentities': [], 'selectedConfigurationMatchesOriginal': True}
    identities = probe.az('identity', 'list', '-g', probe.RG)
    if any(item['name'].startswith('id-adt-pp-devcheck-') for item in identities):
        raise RuntimeError('Temporary verification identity remains')
    with probe.sql_connect() as connection:
        cur = connection.cursor()
        remaining_objects = [row[0] for row in cur.execute("SELECT o.name FROM sys.objects o JOIN sys.schemas s ON s.schema_id=o.schema_id WHERE s.name=N'Aquarium'") if row[0].startswith(('__Stage1', '__MigrationAccess_'))]
        remaining_users = [row[0] for row in cur.execute('SELECT name FROM sys.database_principals') if row[0].startswith(('__Stage3Developer_', '__DeveloperProbe_'))]
        if remaining_objects or remaining_users:
            raise RuntimeError('Temporary SQL object/principal remains')
        memberships = {role: [row[0] for row in cur.execute('SELECT member.name FROM sys.database_role_members rm JOIN sys.database_principals member ON member.principal_id=rm.member_principal_id WHERE rm.role_principal_id=DATABASE_PRINCIPAL_ID(?)', role)] for role in ['AquariumMigrations', 'AquariumDeveloper']}
        if memberships != {'AquariumMigrations': ['github-parameterpilot-migrations-dev'], 'AquariumDeveloper': ['sg-adt-parameterpilot-developers-dev']}:
            raise RuntimeError('Unexpected SQL role member')
    result = {'date': '2026-11-03', 'hosts': hosts, 'temporaryDeveloperIdentityAbsent': True, 'syntheticSqlObjectsAndUsersAbsent': True, 'sqlMemberships': memberships, 'currentVerificationJournalCleaned': True}
    (ROOT / 'docs/infrastructure/evidence/delivery-final-state-2026-11-03.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print('PASS: both hosts disabled/closed and restored; temporary identity/SQL probes absent; SQL role members exact')


if __name__ == '__main__':
    main()
