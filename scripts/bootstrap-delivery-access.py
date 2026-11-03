"""Approved Development delivery identity bootstrap. No passwords/client secrets.

Default is a local plan. --apply --phase directory|github|federation makes the
named changes. Azure assignments remain in main.bicep; SQL has its own script.
GitHub mode invokes git credential fill: announce that operation before use.
"""
import argparse
import json
import subprocess
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUB = '9671ac36-9800-451a-b283-35ea87f8b419'
TENANT = 'f4fcd45c-104f-4dd3-b7bf-3475e83ce097'
OWNER = '7233cead-7a49-4ab1-80f9-6066a03d193f'
REPO = 'PhilipTodd/azure-distributed-systems-reference'
GROUP = 'sg-adt-parameterpilot-developers-dev'
APPS = {'dev': 'github-parameterpilot-deploy-dev', 'dev-migrations': 'github-parameterpilot-migrations-dev'}
CLI_PATH = Path('C:/Program Files/Microsoft SDKs/Azure/CLI2/python.exe')
CLI = [str(CLI_PATH), '-IBm', 'azure.cli'] if CLI_PATH.exists() else ['az']
EVIDENCE = ROOT / 'docs/infrastructure/evidence/delivery-identities-2026-11-03.json'


def az(*args):
    result = subprocess.run([*CLI, *args, '--only-show-errors', '-o', 'json'], capture_output=True, text=True)
    if result.returncode:
        # CLI stderr can include request bodies; do not print credential material.
        raise RuntimeError('Azure operation failed: ' + ' '.join(args[:3]))
    return json.loads(result.stdout) if result.stdout.strip() else None


def body_call(*args, body):
    with tempfile.TemporaryDirectory(prefix='pp-delivery-') as folder:
        path = Path(folder) / 'body.json'
        path.write_text(json.dumps(body), encoding='utf-8')
        return az(*args, '--body', '@' + str(path))


def require_account():
    account = az('account', 'show')
    if account['id'] != SUB or account['tenantId'] != TENANT:
        raise RuntimeError('Unexpected tenant/subscription')
    if az('ad', 'signed-in-user', 'show')['id'] != OWNER:
        raise RuntimeError('Run using the authorised owner session')


def directory():
    result = json.loads(EVIDENCE.read_text(encoding='utf-8')) if EVIDENCE.exists() else {'date': '2026-11-03', 'tenantId': TENANT, 'subscriptionId': SUB, 'applications': {}}
    for environment, name in APPS.items():
        matches = az('ad', 'app', 'list', '--filter', "displayName eq '" + name + "'")
        if len(matches) > 1:
            raise RuntimeError('Ambiguous application name')
        app = matches[0] if matches else az('ad', 'app', 'create', '--display-name', name, '--sign-in-audience', 'AzureADMyOrg')
        if app.get('passwordCredentials') or app.get('keyCredentials'):
            raise RuntimeError('Existing application has credentials; manual review required')
        owners = az('ad', 'app', 'owner', 'list', '--id', app['id'])
        if OWNER not in [owner['id'] for owner in owners]:
            az('ad', 'app', 'owner', 'add', '--id', app['id'], '--owner-object-id', OWNER)
        principals = az('ad', 'sp', 'list', '--filter', "appId eq '" + app['appId'] + "'")
        if len(principals) > 1:
            raise RuntimeError('Ambiguous application principal')
        principal = principals[0] if principals else az('ad', 'sp', 'create', '--id', app['appId'])
        record = result['applications'].get(environment, {})
        if record and (record['applicationObjectId'] != app['id'] or record['principalId'] != principal['id']):
            raise RuntimeError('Recorded directory object changed; reconcile explicitly')
        record.update({'name': name, 'applicationObjectId': app['id'], 'clientId': app['appId'], 'principalId': principal['id']})
        result['applications'][environment] = record
        # Save each successful operation so interrupted runs remain recoverable.
        EVIDENCE.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    groups = az('ad', 'group', 'list', '--filter', "displayName eq '" + GROUP + "'")
    if len(groups) > 1:
        raise RuntimeError('Ambiguous developer group')
    group = groups[0] if groups else az('ad', 'group', 'create', '--display-name', GROUP, '--mail-nickname', GROUP)
    if not group.get('securityEnabled') or group.get('mailEnabled'):
        raise RuntimeError('Existing group has unexpected type')
    for kind in ('owner', 'member'):
        current = az('ad', 'group', kind, 'list', '--group', group['id'])
        if OWNER not in [item['id'] for item in current]:
            option = '--owner-object-id' if kind == 'owner' else '--member-id'
            az('ad', 'group', kind, 'add', '--group', group['id'], option, OWNER)
        if kind == 'member' and any(item['id'] != OWNER for item in current):
            raise RuntimeError('Unexpected developer group members; review before grants')
    result['developerGroup'] = {'name': GROUP, 'objectId': group['id'], 'initialMember': OWNER}
    EVIDENCE.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    return result


def github_client():
    credential = subprocess.run(['git', 'credential', 'fill'], input='protocol=https\nhost=github.com\n\n', text=True, capture_output=True)
    fields = dict(line.split('=', 1) for line in credential.stdout.splitlines() if '=' in line)
    if credential.returncode or not fields.get('password'):
        raise RuntimeError('GitHub authentication unavailable')
    token = fields['password']

    def call(method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        request = urllib.request.Request('https://api.github.com' + path, data=data, method=method, headers={
            'Authorization': 'Bearer ' + token, 'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28', 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                text = response.read()
                return json.loads(text) if text else None
        except urllib.error.HTTPError as error:
            raise RuntimeError('GitHub ' + method + ' ' + path + ' returned ' + str(error.code)) from None
    return call


def github(state):
    call = github_client()
    owner = call('GET', '/users/PhilipTodd')
    environments = {entry['name']: entry for entry in call('GET', '/repos/' + REPO + '/environments')['environments']}
    recorded = {}
    for environment, application in state['applications'].items():
        path = '/repos/' + REPO + '/environments/' + environment
        # Do not overwrite unrelated existing environment protections.
        if environment in environments and environment not in state.get('githubEnvironments', {}):
            raise RuntimeError('Existing target environment needs explicit reconciliation: ' + environment)
        configured = call('PUT', path, {
            'wait_timer': 0, 'prevent_self_review': False,
            'reviewers': [{'type': 'User', 'id': owner['id']}],
            'deployment_branch_policy': {'protected_branches': False, 'custom_branch_policies': True},
            'can_admins_bypass': False})
        state.setdefault('githubEnvironments', {})[environment] = {'created': True}
        EVIDENCE.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
        policies = call('GET', path + '/deployment-branch-policies')['branch_policies']
        if any(policy['name'] != 'main' or policy.get('type', 'branch') != 'branch' for policy in policies):
            raise RuntimeError('Unexpected deployment branch/tag policy')
        if not policies:
            call('POST', path + '/deployment-branch-policies', {'name': 'main', 'type': 'branch'})
        variables = {'AZURE_CLIENT_ID': application['clientId'], 'AZURE_TENANT_ID': TENANT, 'AZURE_SUBSCRIPTION_ID': SUB}
        current = {item['name']: item for item in call('GET', path + '/variables')['variables']}
        for name, value in variables.items():
            call('PATCH' if name in current else 'POST', path + '/variables' + ('/' + name if name in current else ''), {'name': name, 'value': value})
        verified = call('GET', path)
        policies = call('GET', path + '/deployment-branch-policies')['branch_policies']
        rules = verified['protection_rules']
        reviewers = next((rule for rule in rules if rule['type'] == 'required_reviewers'), {})
        if reviewers.get('prevent_self_review') is not False or not any(item['reviewer']['id'] == owner['id'] for item in reviewers.get('reviewers', [])):
            raise RuntimeError('Required owner approval not verified')
        if len(policies) != 1 or policies[0]['name'] != 'main' or policies[0].get('type', 'branch') != 'branch':
            raise RuntimeError('Main-only policy not verified')
        if verified.get('can_admins_bypass') is not False:
            raise RuntimeError('Administrator bypass setting not verified')
        recorded[environment] = {'ownerApprovalRequired': True, 'selfApprovalAllowed': True, 'adminBypass': False, 'branch': 'main', 'variableNames': list(variables)}
        state['githubEnvironments'][environment] = recorded[environment]
        EVIDENCE.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    return recorded


def federation(state):
    for environment, application in state['applications'].items():
        if not state.get('githubEnvironments', {}).get(environment, {}).get('ownerApprovalRequired'):
            raise RuntimeError('Verify GitHub environment protection before enabling federation')
        desired = {'name': 'github-' + environment, 'issuer': 'https://token.actions.githubusercontent.com',
                   'subject': 'repo:' + REPO + ':environment:' + environment, 'audiences': ['api://AzureADTokenExchange']}
        existing = az('ad', 'app', 'federated-credential', 'list', '--id', application['applicationObjectId'])
        if any(item['name'] != desired['name'] or any(item.get(key) != desired[key] for key in ('issuer', 'subject', 'audiences')) for item in existing):
            raise RuntimeError('Unexpected existing federated trust')
        if not existing:
            body_call('rest', '--method', 'POST', '--url', 'https://graph.microsoft.com/v1.0/applications/' + application['applicationObjectId'] + '/federatedIdentityCredentials', body=desired)
        verified = az('ad', 'app', 'federated-credential', 'list', '--id', application['applicationObjectId'])
        if len(verified) != 1 or any(verified[0].get(key) != desired[key] for key in ('issuer', 'subject', 'audiences')):
            raise RuntimeError('Federated trust verification failed')
        application['federation'] = desired
        EVIDENCE.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')
    return {'federationConfigured': True, 'actualGitHubLoginVerified': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['directory', 'github', 'federation'], default='directory')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--parameters-output', type=Path, help='Write access-only ARM parameters from saved Development values and verified directory IDs; no Azure changes.')
    args = parser.parse_args()
    if args.parameters_output:
        if args.apply:
            parser.error('--parameters-output cannot be combined with --apply')
        state = json.loads(EVIDENCE.read_text(encoding='utf-8'))
        with tempfile.TemporaryDirectory(prefix='pp-parameters-') as folder:
            compiled = Path(folder) / 'parameters.json'
            compiler = Path.home() / '.azure/bin/bicep.exe'
            command = [str(compiler), 'build-params', str(ROOT / 'infra/bicep/environments/dev/main.dev.bicepparam'), '--outfile', str(compiled)] if compiler.exists() else ['bicep', 'build-params', str(ROOT / 'infra/bicep/environments/dev/main.dev.bicepparam'), '--outfile', str(compiled)]
            subprocess.run(command, check=True, capture_output=True)
            parameters = json.loads(compiled.read_text(encoding='utf-8-sig'))
        parameters['parameters'].update({
            'deployDeliveryAccess': {'value': True},
            'deploymentPrincipalId': {'value': state['applications']['dev']['principalId']},
            'developerGroupId': {'value': state['developerGroup']['objectId']},
            'deployStaticWebApp': {'value': False},
            'deployServiceFoundations': {'value': False},
            'deployTrackingDataAccess': {'value': False},
            'deployCustomerIdentity': {'value': False},
        })
        args.parameters_output.write_text(json.dumps(parameters, indent=2) + '\n', encoding='utf-8')
        print('Wrote explicit access-only parameters; no Azure changes applied.')
        return
    if not args.apply:
        print(json.dumps({'phase': args.phase, 'apply': False, 'applications': APPS, 'developerGroup': GROUP}, indent=2))
        return
    require_account()
    state = json.loads(EVIDENCE.read_text(encoding='utf-8')) if EVIDENCE.exists() else None
    if args.phase == 'directory':
        result = directory()
    elif args.phase == 'github':
        result = github(state)
    else:
        result = federation(state)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
