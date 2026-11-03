"""Read back approved access-only deployment resources; never applies changes."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('delivery', ROOT / 'scripts/bootstrap-delivery-access.py')
delivery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delivery)


def equivalent(actual, expected):
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(key in actual and equivalent(actual[key], value) for key, value in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(equivalent(a, e) for a, e in zip(actual, expected))
    return actual == expected


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('preview', type=Path)
    args = parser.parse_args()
    delivery.require_account()
    preview = json.loads(args.preview.read_text(encoding='utf-8-sig'))
    if any(change['changeType'] not in ['Create', 'NoChange', 'Ignore'] for change in preview['changes']):
        raise RuntimeError('Not an additions-only preview')
    checked = []
    for change in preview['changes']:
        if change['changeType'] != 'Create':
            continue
        resource_id = change['resourceId']
        is_cosmos = '/Microsoft.DocumentDB/' in resource_id
        api = '2024-11-15' if is_cosmos else '2022-04-01'
        actual = delivery.az('rest', '--method', 'GET', '--url', 'https://management.azure.com' + resource_id + '?api-version=' + api)
        expected = change['after']['properties']
        if not equivalent(actual['properties'], expected):
            raise RuntimeError('Live permission differs from preview: ' + resource_id)
        checked.append({'id': resource_id, 'propertiesMatchPreview': True})
    if len(checked) != 13:
        raise RuntimeError('Expected exactly 13 approved permission resources')
    builtin_registry_roles = {}
    for name, role_id, actions in [
        ('reader', 'b93aa761-3e63-49ed-ac28-beffa264f7ac', ['content/read', 'metadata/read']),
        ('writer', '2a1e307c-b015-4ebd-883e-5b7698a07328', ['content/read', 'content/write', 'metadata/read', 'metadata/write']),
    ]:
        role = delivery.az('role', 'definition', 'list', '--name', role_id)[0]
        expected = {'Microsoft.ContainerRegistry/registries/repositories/' + action for action in actions}
        permissions = role['permissions']
        if len(permissions) != 1 or set(permissions[0]['dataActions']) != expected or permissions[0]['actions'] or permissions[0]['notDataActions']:
            raise RuntimeError('Unexpected built-in registry permissions')
        builtin_registry_roles[name] = {'roleId': role_id, 'dataActions': sorted(expected)}
    identities = json.loads(delivery.EVIDENCE.read_text(encoding='utf-8'))
    new_ids = {application['principalId'] for application in identities['applications'].values()} | {identities['developerGroup']['objectId']}
    all_assignments = delivery.az('role', 'assignment', 'list', '--all')
    assigned = [item for item in all_assignments if item['principalId'] in new_ids]
    allowed_ids = {item['id'].lower() for item in checked}
    if any(item['id'].lower() not in allowed_ids for item in assigned):
        raise RuntimeError('Unexpected Azure grant to a new PP identity/group')
    result = {'date': '2026-11-03', 'deploymentName': 'pp-delivery-access-dev-20261103', 'resourcesVerified': checked, 'builtinRegistryRolesVerified': builtin_registry_roles, 'unexpectedAzureAssignments': False, 'verification': 'Read-back equality with approved additions-only preview; not effective identity execution'}
    path = ROOT / 'docs/infrastructure/evidence/delivery-permissions-deployment-2026-11-03.json'
    path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'resourcesVerified': len(checked), 'unexpectedAzureAssignments': False}))


if __name__ == '__main__':
    main()
