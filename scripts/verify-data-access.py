"""Verify compiled Development Tracking container and data-role boundaries; no Azure calls."""
import argparse
import copy
import json
from pathlib import Path


def require(value, message):
    if not value:
        raise ValueError(message)


def verify(template, parameters):
    p = parameters['parameters']
    require(p['deployTrackingDataAccess']['value'] is False, 'Saved data deployment switch must remain false')
    require(p['cosmosAccountName']['value'] == 'cosmos-adt-platform-dev' and p['cosmosDatabaseName']['value'] == 'ReferenceProjects', 'Existing shared account/database only')
    require(p['trackingContainerName']['value'] == 'parameterpilot-tracking', 'Owner-approved container name required')
    require(p['trackingPrincipalId']['value'] == '6c046dfa-2416-4706-893d-7cc000afecf0', 'Verified Tracking identity required')
    module = next(r for r in template['resources'] if 'tracking-data-access' in r.get('name', ''))
    require(module['condition'] == "[and(parameters('deployTrackingDataAccess'), equals(parameters('environment'), 'dev'))]", 'Development opt-in gate required')
    resources = module['properties']['template']['resources']
    types = {r['type'] for r in resources}
    require(len(resources) == 3 and types == {'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers', 'Microsoft.DocumentDB/databaseAccounts/sqlRoleDefinitions', 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments'}, 'No shared parent resources or other grants')
    container = next(r for r in resources if r['type'].endswith('/containers'))
    require(container['properties'] == {'resource': {'id': "[parameters('containerName')]", 'partitionKey': {'paths': ['/tankId'], 'kind': 'Hash', 'version': 2}}, 'options': {}}, 'Partition, no TTL and no dedicated throughput must be preserved')
    definition = next(r for r in resources if r['type'].endswith('/sqlRoleDefinitions'))
    permissions = definition['properties']['permissions']
    prefix = 'Microsoft.DocumentDB/databaseAccounts/'
    expected = {prefix + 'readMetadata', *[prefix + 'sqlDatabases/containers/items/' + action for action in ['create', 'read', 'replace', 'upsert', 'delete']], prefix + 'sqlDatabases/containers/executeQuery', prefix + 'sqlDatabases/containers/readChangeFeed'}
    require(len(permissions) == 1 and set(permissions[0]['dataActions']) == expected, 'Exact CRUD/query/metadata actions only; no wildcard or stored procedures')
    assignment = next(r for r in resources if r['type'].endswith('/sqlRoleAssignments'))
    a = assignment['properties']
    require(a['principalId'] == "[parameters('trackingPrincipalId')]", 'No substitute identity')
    require(a['scope'] == "[format('{0}/dbs/{1}/colls/{2}', resourceId('Microsoft.DocumentDB/databaseAccounts', parameters('accountName')), parameters('databaseName'), parameters('containerName'))]", 'Container scope required')
    require(a['roleDefinitionId'] == "[resourceId('Microsoft.DocumentDB/databaseAccounts/sqlRoleDefinitions', parameters('accountName'), guid(resourceId('Microsoft.DocumentDB/databaseAccounts', parameters('accountName')), 'parameterpilot-tracking-runtime'))]", 'Assignment must use reviewed role')
    return resources


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('template')
    parser.add_argument('parameters')
    args = parser.parse_args()
    template = json.loads(Path(args.template).read_text(encoding='utf-8-sig'))
    parameters = json.loads(Path(args.parameters).read_text(encoding='utf-8-sig'))
    verify(template, parameters)
    mutations = [
        ('/containers', lambda r: r['properties']['resource']['partitionKey'].update(paths=['/streamId'])),
        ('/containers', lambda r: r['properties']['options'].update(throughput=400)),
        ('/containers', lambda r: r['properties']['resource'].update(defaultTtl=3600)),
        ('/sqlRoleAssignments', lambda r: r['properties'].update(scope='/')),
        ('/sqlRoleDefinitions', lambda r: r['properties']['permissions'][0]['dataActions'].append('Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/*')),
    ]
    for suffix, mutate in mutations:
        changed = copy.deepcopy(template)
        module = next(r for r in changed['resources'] if 'tracking-data-access' in r.get('name', ''))
        mutate(next(r for r in module['properties']['template']['resources'] if r['type'].endswith(suffix)))
        try:
            verify(changed, parameters)
        except ValueError:
            continue
        raise AssertionError('Unsafe mutation accepted: ' + suffix)
    print('PASS: Tracking container-scoped role, no shared capacity changes, and five unsafe mutations rejected')
