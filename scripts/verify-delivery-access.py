"""Validate compiled delivery access against privilege escalation and scope drift."""
import argparse
import copy
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verify(template, parameters):
    p = parameters['parameters']
    require(p['deployDeliveryAccess']['value'] is False, 'Saved delivery deployment switch must be false')
    require(p['deploymentPrincipalId']['value'] == '' and p['developerGroupId']['value'] == '', 'Saved principal IDs must require explicit bootstrap input')
    modules = {fragment: next(resource for resource in template['resources'] if fragment in resource.get('name', '')) for fragment in ['delivery-role-definitions', 'delivery-access-', 'registry-access-', 'developer-cosmos-access-']}
    for module in modules.values():
        require(module['condition'] == "[and(parameters('deployDeliveryAccess'), equals(parameters('environment'), 'dev'))]", 'All delivery changes require Development opt-in')
    roles = modules['delivery-role-definitions']['properties']['template']['resources']
    require(len(roles) == 2 and all(role['type'] == 'Microsoft.Authorization/roleDefinitions' for role in roles), 'Exactly two custom release roles')
    expected_actions = [
        {'Microsoft.Web/sites/read', 'Microsoft.Web/sites/config/read', 'Microsoft.Web/sites/config/write', 'Microsoft.Web/sites/restart/action'},
        {'Microsoft.Web/staticSites/read', 'Microsoft.Web/staticSites/listsecrets/action'},
    ]
    for role, expected in zip(roles, expected_actions):
        permissions = role['properties']['permissions']
        require(len(permissions) == 1 and set(permissions[0]['actions']) == expected, 'Exact release actions required; no host creation, broad wildcard or IAM')
        require(not permissions[0]['dataActions'], 'No release data-plane grant')
        require(role['properties']['assignableScopes'] == ["[subscriptionResourceId('Microsoft.Resources/resourceGroups', parameters('applicationResourceGroupName'))]"], 'Release role assignable scope must be PP RG')
    access = modules['delivery-access-']['properties']['template']['resources']
    require(len(access) == 4 and all(r['type'] == 'Microsoft.Authorization/roleAssignments' for r in access), 'PP access must only add four assignment declarations')
    for resource in access:
        props = resource['properties']
        require(props['principalId'] in ["[parameters('deploymentPrincipalId')]", "[parameters('developerGroupId')]"], 'Only approved release/group principals')
        require(props['principalType'] == ('Group' if 'developerGroupId' in props['principalId'] else 'ServicePrincipal'), 'Explicit principal type required')
    registry_template = modules['registry-access-']['properties']['template']
    require(registry_template['variables']['readerRoleId'] == "[subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b93aa761-3e63-49ed-ac28-beffa264f7ac')]", 'Exact ABAC Reader role required')
    require(registry_template['variables']['writerRoleId'] == "[subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '2a1e307c-b015-4ebd-883e-5b7698a07328')]", 'Exact ABAC Writer role required')
    registry = registry_template['resources']
    require(len(registry) == 2 and all(r['type'] == 'Microsoft.Authorization/roleAssignments' for r in registry), 'Registry configuration/capacity must not change')
    for assignment in registry:
        props = assignment['properties']
        require(props['conditionVersion'] == '2.0', 'ABAC condition required')
        condition = props['condition']
        require('StringEqualsIgnoreCase' in condition and 'StringLike' not in condition and '*' not in condition, 'Exact repository match only')
        require('repositories/metadata/read' in condition and 'repositories/content/read' in condition, 'Reader actions must both be conditioned')
        if 'copy' not in assignment:
            require('parameterpilot/aquarium-api' in condition and 'parameterpilot/tracking-api' in condition, 'Publisher exactly the two PP repositories')
            require('repositories/metadata/write' in condition and 'repositories/content/write' in condition, 'Writer actions must both be conditioned')
    cosmos = modules['developer-cosmos-access-']['properties']['template']['resources']
    require(len(cosmos) == 2 and {r['type'].rsplit('/', 1)[-1] for r in cosmos} == {'sqlRoleDefinitions', 'sqlRoleAssignments'}, 'Cosmos data roles only, no account/container/capacity writes')
    definition = next(r for r in cosmos if r['type'].endswith('/sqlRoleDefinitions'))
    prefix = 'Microsoft.DocumentDB/databaseAccounts/'
    expected = {prefix + 'readMetadata', prefix + 'sqlDatabases/containers/items/read', prefix + 'sqlDatabases/containers/executeQuery', prefix + 'sqlDatabases/containers/readChangeFeed'}
    require(definition['properties']['permissions'] == [{'dataActions': list(definition['properties']['permissions'][0]['dataActions'])}] and set(definition['properties']['permissions'][0]['dataActions']) == expected, 'Developer Cosmos must be read-only')
    assignment = next(r for r in cosmos if r['type'].endswith('/sqlRoleAssignments'))
    require(assignment['properties']['scope'] == "[format('{0}/dbs/{1}/colls/{2}', resourceId('Microsoft.DocumentDB/databaseAccounts', parameters('accountName')), parameters('databaseName'), parameters('containerName'))]", 'Developer Cosmos scope must be one container')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('template', type=Path)
    parser.add_argument('parameters', type=Path)
    args = parser.parse_args()
    template = json.loads(args.template.read_text(encoding='utf-8-sig'))
    parameters = json.loads(args.parameters.read_text(encoding='utf-8-sig'))
    verify(template, parameters)
    mutations = []
    changed = copy.deepcopy(template)
    module = next(r for r in changed['resources'] if 'delivery-role-definitions' in r.get('name', ''))
    module['properties']['template']['resources'][0]['properties']['permissions'][0]['actions'].append('Microsoft.Authorization/roleAssignments/write')
    mutations.append((changed, parameters))
    changed = copy.deepcopy(template)
    module = next(r for r in changed['resources'] if 'registry-access-' in r.get('name', ''))
    module['properties']['template']['resources'][0]['properties'].pop('conditionVersion')
    mutations.append((changed, parameters))
    changed = copy.deepcopy(template)
    module = next(r for r in changed['resources'] if 'developer-cosmos-access-' in r.get('name', ''))
    module['properties']['template']['resources'][0]['properties']['permissions'][0]['dataActions'].append('Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/create')
    mutations.append((changed, parameters))
    changed_params = copy.deepcopy(parameters)
    changed_params['parameters']['deployDeliveryAccess']['value'] = True
    mutations.append((template, changed_params))
    for changed, changed_params in mutations:
        try:
            verify(changed, changed_params)
        except (ValueError, KeyError):
            continue
        raise RuntimeError('Unsafe privilege mutation was accepted')
    print('PASS: delivery access scope/action/ABAC boundaries and four unsafe mutations rejected')


if __name__ == '__main__':
    main()
