"""Controlled Stage 1 managed-identity probe. No developer-token fallback inside workloads.
Local coordinator uses the owner's Azure CLI session; --phase cleanup is always available.
"""
import argparse
import base64
import concurrent.futures
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import time
import uuid
import hashlib
import secrets
import urllib.request
import urllib.parse
import urllib.error
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / 'tests/Stage1.AccessProbe'
RUNTIME = PROBE / '.runtime'
JOURNAL = RUNTIME / 'journal.json'
SUB = '9671ac36-9800-451a-b283-35ea87f8b419'
TENANT = 'f4fcd45c-104f-4dd3-b7bf-3475e83ce097'
RG = 'rg-parameterpilot-dev'
ARM = 'https://management.azure.com'
REGISTRY = f'/subscriptions/{SUB}/resourceGroups/rg-platform-dev/providers/Microsoft.ContainerRegistry/registries/acradtplatformdev'
REPOSITORY = 'parameterpilot/access-verification'
IDENTITIES = {'aquarium': 'e43e0132-e184-4669-8431-9f5a3ea5393e', 'tracking': '6c046dfa-2416-4706-893d-7cc000afecf0'}
CLI_PYTHON = Path(os.environ.get('ProgramFiles', 'C:/Program Files')) / 'Microsoft SDKs/Azure/CLI2/python.exe'
CLI = [str(CLI_PYTHON), '-IBm', 'azure.cli'] if CLI_PYTHON.exists() else ['az']


def command(args, **kwargs):
    result = subprocess.run(args, text=True, capture_output=True, **kwargs)
    if result.returncode:
        raise RuntimeError('Operation failed: ' + ' '.join(args[:5]) + ': ' + result.stderr[:1200])
    return result.stdout


def az(*args):
    text = command([*CLI, *args, '--only-show-errors', '-o', 'json'])
    return json.loads(text) if text.strip() else None


def quiet(*args):
    command([*CLI, *args, '--only-show-errors', '-o', 'none'])


def rest(method, path, body=None):
    args = ['rest', '--method', method, '--url', ARM + path]
    if body is not None:
        path = RUNTIME / 'request.json'
        path.write_text(json.dumps(body), encoding='utf-8')
        args += ['--body', '@' + str(path), '--headers', 'Content-Type=application/json']
    return az(*args)


def app_id(service):
    return f'/subscriptions/{SUB}/resourceGroups/{RG}/providers/Microsoft.Web/sites/api-adt-{service}-dev'


def save(state):
    RUNTIME.mkdir(parents=True, exist_ok=True)
    JOURNAL.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')


def load():
    return json.loads(JOURNAL.read_text(encoding='utf-8'))


def sql_connect():
    import pyodbc
    token = az('account', 'get-access-token', '--resource', 'https://database.windows.net/')['accessToken'].encode('utf-16-le')
    return pyodbc.connect('Driver={ODBC Driver 18 for SQL Server};Server=tcp:sql-adt-platform-dev.database.windows.net,1433;Database=ReferenceProjectsDb;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;', attrs_before={1256: struct.pack('<I', len(token)) + token}, autocommit=True, timeout=30)


def sql_security(cursor):
    return [list(r) for r in cursor.execute("SELECT p.state_desc,p.permission_name,p.class_desc,p.major_id FROM sys.database_permissions p WHERE p.grantee_principal_id=DATABASE_PRINCIPAL_ID(N'AquariumRuntime') ORDER BY p.class,p.major_id,p.permission_name")]


_OWNER_TOKENS = {}


def data_request(resource, method, url, body=None, headers=None):
    if resource not in _OWNER_TOKENS:
        _OWNER_TOKENS[resource] = az('account', 'get-access-token', '--resource', resource)['accessToken']
    request_headers = {'Authorization': 'Bearer ' + _OWNER_TOKENS[resource], 'Content-Type': 'application/json'}
    request_headers.update(headers or {})
    request = urllib.request.Request(url, method=method, headers=request_headers, data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as error:
        # Error bodies may repeat test content: never log or persist them.
        return error.code, None


def configuration_url(service, key):
    return 'https://appcs-adt-' + service + '-dev.azconfig.io/kv/' + urllib.parse.quote(key, safe='') + '?api-version=1.0'


def secret_url(service, name, deleted=False):
    return 'https://kv-adt-' + service + '-dev.vault.azure.net/' + ('deletedsecrets/' if deleted else 'secrets/') + name + '?api-version=7.4'


def content_request_with_propagation(resource, method, url, body=None, headers=None):
    for attempt in range(36):
        status, value = data_request(resource, method, url, body, headers)
        if status != 403:
            return status, value
        if attempt % 6 == 0:
            print('Waiting for resource-scoped content setup permission propagation', flush=True)
        time.sleep(10)
    raise RuntimeError('Resource-scoped setup permission did not propagate within the bounded interval')


def prepare_configuration_content(state):
    run = state['runId']
    settings = {'RunId': run, 'Mode': 'configuration', 'SqlTable': f'[Aquarium].[__Stage1Probe_{run}]', 'MigrationTable': f'[Aquarium].[__Stage1MigrationProbe_{run}]', 'ForbiddenTable': f'[Aquarium].[__Stage1Forbidden_{run}]', 'OtherProductTables': [], 'SecretHashes': {}, 'ManagementTags': {}, 'RoleAssignments': {}}
    state['settings'] = settings
    state['content'] = {}
    save(state)
    for service in IDENTITIES:
        config_id = f'/subscriptions/{SUB}/resourceGroups/{RG}/providers/Microsoft.AppConfiguration/configurationStores/appcs-adt-{service}-dev'
        vault_id = f'/subscriptions/{SUB}/resourceGroups/{RG}/providers/Microsoft.KeyVault/vaults/kv-adt-{service}-dev'
        for kind, resource_id, role in [('configuration', config_id, 'App Configuration Data Owner'), ('vault', vault_id, 'Key Vault Secrets Officer')]:
            metadata = rest('get', resource_id + '?api-version=' + ('2024-06-01' if kind == 'configuration' else '2024-11-01'))
            settings['ManagementTags'][service + ':' + kind] = metadata.get('tags', {})
            expected_role = '516239f1-63e1-4d78-a4de-a74fb236a071' if kind == 'configuration' else '4633458b-17de-408a-b874-0445c86b69e6'
            roles = az('role', 'assignment', 'list', '--scope', resource_id)
            own = [r for r in roles if r['principalId'] == IDENTITIES[service] and r['scope'].lower() == resource_id.lower() and r['roleDefinitionId'].split('/')[-1] == expected_role]
            assert len(own) == 1
            settings['RoleAssignments'][service + ':' + kind] = {'Id': own[0]['id'], 'Properties': {k: own[0][k] for k in ['principalId', 'principalType', 'roleDefinitionId', 'description', 'condition', 'conditionVersion'] if k in own[0]}}
            assignment_name = str(uuid.uuid4())
            assignment_id = resource_id + '/providers/Microsoft.Authorization/roleAssignments/' + assignment_name
            state['roleAssignmentIds'].append(assignment_id)
            state.setdefault('issuedRoleAssignmentIds', []).append(assignment_id)
            save(state)
            az('role', 'assignment', 'create', '--name', assignment_name, '--assignee-object-id', '7233cead-7a49-4ab1-80f9-6066a03d193f', '--assignee-principal-type', 'User', '--role', role, '--scope', resource_id, '--description', 'Temporary PP step 2 synthetic content setup ' + run)
            print('Temporary owner content setup grant: ' + service + ' ' + kind, flush=True)
    for service in IDENTITIES:
        entry = {'key': 'Stage1:Step2:' + run + ':' + service, 'secretName': 'pp-step2-' + run, 'keyAttempted': True, 'secretAttempted': False}
        state['content'][service] = entry
        save(state)
        status, _ = content_request_with_propagation('https://azconfig.io', 'PUT', configuration_url(service, entry['key']), {'value': 'synthetic-step2-' + run + '-' + service, 'tags': {'stage1Run': run}}, {'If-None-Match': '*'})
        if status != 200:
            raise RuntimeError('Synthetic key creation failed with HTTP ' + str(status))
        entry['secretAttempted'] = True
        save(state)
        value = secrets.token_hex(32)
        settings['SecretHashes'][service] = hashlib.sha256(value.encode()).hexdigest()
        status, _ = content_request_with_propagation('https://vault.azure.net', 'PUT', secret_url(service, entry['secretName']), {'value': value, 'tags': {'stage1Run': run}})
        del value
        if status != 200:
            raise RuntimeError('Synthetic secret creation failed with HTTP ' + str(status))
        save(state)
        print('Created synthetic configuration and disposable secret for ' + service + '; no values logged', flush=True)
    return settings


def deleted_secret_metadata(service, name):
    base = 'https://kv-adt-' + service + '-dev.vault.azure.net/'
    url = base + 'deletedsecrets?api-version=7.4'
    while url:
        if not url.startswith(base):
            raise RuntimeError('Unexpected deleted-secret pagination origin')
        status, page = data_request('https://vault.azure.net', 'GET', url)
        if status != 200:
            return status, None
        for item in page.get('value', []):
            if urllib.parse.urlparse(item['id']).path.split('/')[2] == name:
                return 200, {k: item.get(k) for k in ['id', 'recoveryId', 'deletedDate', 'scheduledPurgeDate']}
        url = page.get('nextLink')
    return 404, None


def cleanup_configuration_content(state):
    summary = {}
    for service, entry in state.get('content', {}).items():
        if entry['keyAttempted']:
            for key in [entry['key'], entry['key'] + ':denied-create']:
                status, _ = data_request('https://azconfig.io', 'DELETE', configuration_url(service, key))
                if status not in [200, 204, 404]:
                    raise RuntimeError('Synthetic configuration cleanup failed with HTTP ' + str(status))
                status, _ = data_request('https://azconfig.io', 'GET', configuration_url(service, key))
                if status != 404:
                    raise RuntimeError('Synthetic configuration still present after cleanup')
        deleted = []
        if entry['secretAttempted']:
            for name in [entry['secretName'], entry['secretName'] + '-denied-create']:
                status, response = data_request('https://vault.azure.net', 'DELETE', secret_url(service, name))
                delete_status = status
                if status not in [200, 404]:
                    raise RuntimeError('Synthetic secret cleanup failed with HTTP ' + str(status))
                status, _ = data_request('https://vault.azure.net', 'GET', secret_url(service, name))
                if status != 404:
                    raise RuntimeError('Synthetic secret still active after cleanup')
                deletion_requested = delete_status == 200
                status, metadata = deleted_secret_metadata(service, name)
                for attempt in range(30):
                    if status != 404 or not deletion_requested:
                        break
                    time.sleep(2)
                    status, metadata = deleted_secret_metadata(service, name)
                if deletion_requested and status != 200:
                    raise RuntimeError('Deleted test-secret metadata not yet confirmed; retain cleanup access for retry')
                if status == 200:
                    deleted.append({k: metadata.get(k) for k in ['id', 'recoveryId', 'deletedDate', 'scheduledPurgeDate']})
                elif status != 404:
                    raise RuntimeError('Unable to verify soft-deleted test-secret state')
        summary[service] = {'configurationKeysAbsent': True, 'activeTestSecretsAbsent': True, 'softDeletedSyntheticSecrets': deleted, 'purgeAttempted': False}
    state['contentCleanup'] = summary
    save(state)


def prepare(mode="data"):
    if JOURNAL.exists() and not load().get('cleaned'):
        raise RuntimeError('A previous run requires cleanup; journal preserved')
    account = az('account', 'show')
    assert account['id'] == SUB and account['tenantId'] == TENANT
    if JOURNAL.exists():
        shutil.copyfile(JOURNAL, RUNTIME / ('journal-' + load()['runId'] + '.json'))
    state = {'mode': mode, 'runId': uuid.uuid4().hex[:12], 'createdUtc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'apps': {}, 'roleAssignmentIds': [], 'results': {}, 'cleaned': False}
    save(state)
    for service in IDENTITIES:
        app = rest('get', app_id(service) + '?api-version=2024-11-01')
        assert app['identity']['principalId'] == IDENTITIES[service]
        assert app['properties']['enabled'] is False and app['properties']['publicNetworkAccess'] == 'Disabled'
        configuration = az('webapp', 'config', 'show', '-g', RG, '-n', 'api-adt-' + service + '-dev', '--query', '{linuxFxVersion:linuxFxVersion,acrUseManagedIdentityCreds:acrUseManagedIdentityCreds,appCommandLine:appCommandLine,alwaysOn:alwaysOn}')
        selected = az('webapp', 'config', 'appsettings', 'list', '-g', RG, '-n', 'api-adt-' + service + '-dev', '--query', "[?name=='WEBSITES_PORT' || name=='DOCKER_REGISTRY_SERVER_URL'].{name:name,value:value}")
        logs = rest('get', app_id(service) + '/config/logs?api-version=2024-11-01')['properties']['httpLogs']['fileSystem']
        state['apps'][service] = {'configuration': configuration, 'selectedSettings': selected, 'httpFileLogging': logs, 'originalKind': app['kind'], 'originalEnabled': False, 'originalPublicNetworkAccess': 'Disabled', 'restored': True}
        save(state)
    if mode == 'configuration':
        settings = prepare_configuration_content(state)
    elif mode in ('certificate', 'hosting'):
        run = state['runId']
        settings = {'RunId': run, 'Mode': 'certificate', 'SqlTable': f'[Aquarium].[__Stage1Probe_{run}]', 'MigrationTable': f'[Aquarium].[__Stage1MigrationProbe_{run}]', 'ForbiddenTable': f'[Aquarium].[__Stage1Forbidden_{run}]', 'OtherProductTables': []}
        state['settings'] = settings
        save(state)  # Certificate/hosting modes perform no SQL or synthetic-data operation.
    else:
        with sql_connect() as connection:
            cur = connection.cursor()
            state['sqlSecurityBefore'] = sql_security(cur)
            run = state['runId']
            settings = {'RunId': run, 'SqlTable': f'[Aquarium].[__Stage1Probe_{run}]', 'MigrationTable': f'[Aquarium].[__Stage1MigrationProbe_{run}]', 'ForbiddenTable': f'[Aquarium].[__Stage1Forbidden_{run}]', 'OtherProductTables': []}
            for schema, table in cur.execute("SELECT s.name,t.name FROM sys.tables t JOIN sys.schemas s ON t.schema_id=s.schema_id WHERE s.name IN (N'BlastPlanning',N'ticketing')"):
                settings['OtherProductTables'].append('[' + schema.replace(']', ']]') + '].[' + table.replace(']', ']]') + ']')
            state['settings'] = settings
            save(state) # Persist cleanup names before any SQL mutation.
            cur.execute('BEGIN TRANSACTION; CREATE TABLE ' + settings['SqlTable'] + ' (Id int NOT NULL PRIMARY KEY,Value int NOT NULL); CREATE TABLE ' + settings['MigrationTable'] + ' (Id int NOT NULL); GRANT SELECT, INSERT, UPDATE, DELETE ON OBJECT::' + settings['SqlTable'] + ' TO [AquariumRuntime]; COMMIT TRANSACTION;')
    (RUNTIME / 'publish/probe-settings.json').write_text(json.dumps(settings), encoding='utf-8')
    shutil.copyfile(PROBE / 'Dockerfile', RUNTIME / 'Dockerfile')
    # Conditions restrict every repository data action to one verification repository.
    condition = "((!(ActionMatches{'Microsoft.ContainerRegistry/registries/repositories/content/read'}) AND !(ActionMatches{'Microsoft.ContainerRegistry/registries/repositories/content/write'}) AND !(ActionMatches{'Microsoft.ContainerRegistry/registries/repositories/metadata/read'}) AND !(ActionMatches{'Microsoft.ContainerRegistry/registries/repositories/metadata/write'})) OR (@Request[Microsoft.ContainerRegistry/registries/repositories:name] StringEqualsIgnoreCase '" + REPOSITORY + "'))"
    grants = [(service, principal, 'Container Registry Repository Reader', 'ServicePrincipal') for service, principal in IDENTITIES.items() if mode != 'certificate' or service == 'tracking']
    grants.append(('publisher', '7233cead-7a49-4ab1-80f9-6066a03d193f', 'Container Registry Repository Writer', 'User'))
    for label, principal, role, principal_type in grants:
        actions = ['content/read', 'metadata/read']
        if label == 'publisher':
            actions += ['content/write', 'metadata/write']
        guards = ' AND '.join("!(ActionMatches{'Microsoft.ContainerRegistry/registries/repositories/" + action + "'})" for action in actions)
        condition = "((" + guards + ") OR (@Request[Microsoft.ContainerRegistry/registries/repositories:name] StringEqualsIgnoreCase '" + REPOSITORY + "'))"
        # Azure permits only one assignment per principal/role/scope tuple.
        # CLI create can return an existing assignment while ignoring the new
        # requested name/condition. Journal and temporarily extend its read
        # condition instead; never mistake an existing grant for a new one.
        existing = az('role', 'assignment', 'list', '--scope', REGISTRY)
        expected_role_id = '2a1e307c-b015-4ebd-883e-5b7698a07328' if label == 'publisher' else 'b93aa761-3e63-49ed-ac28-beffa264f7ac'
        matching = [item for item in existing if item['principalId'] == principal and item['roleDefinitionId'].rsplit('/', 1)[-1] == expected_role_id and item['scope'].lower() == REGISTRY.lower()]
        if matching:
            if len(matching) != 1 or label == 'publisher' or not matching[0].get('condition') or matching[0].get('conditionVersion') != '2.0':
                raise RuntimeError('Existing registry grant needs explicit reconciliation')
            item = matching[0]
            original = {key: item[key] for key in ['roleDefinitionId', 'principalId', 'principalType', 'condition', 'conditionVersion']}
            if item.get('description'):
                original['description'] = item['description']
            state.setdefault('modifiedRoleAssignments', []).append({'id': item['id'], 'originalProperties': original})
            save(state)
            changed = dict(original)
            changed['condition'] = '(' + original['condition'] + ') OR (' + condition + ')'
            actual = rest('put', item['id'] + '?api-version=2022-04-01', {'properties': changed})
            if actual['properties']['condition'] != changed['condition']:
                raise RuntimeError('Temporary registry condition not applied')
            print('Temporarily extended read-only ' + label + ' repository condition; original journalled', flush=True)
            continue
        name = str(uuid.uuid4())
        resource_id = REGISTRY + '/providers/Microsoft.Authorization/roleAssignments/' + name
        state['roleAssignmentIds'].append(resource_id)
        state.setdefault('issuedRoleAssignmentIds', []).append(resource_id)
        save(state)
        created = az('role', 'assignment', 'create', '--name', name, '--assignee-object-id', principal, '--assignee-principal-type', principal_type, '--role', role, '--scope', REGISTRY, '--condition', condition, '--condition-version', '2.0', '--description', 'Temporary PP Stage 1 real-identity verification ' + state['runId'])
        if created['id'].lower() != resource_id.lower() or created.get('condition') != condition:
            raise RuntimeError('CLI did not create the exact temporary registry assignment')
        print('Created temporary repository-conditioned ' + label + ' grant', flush=True)
    print('Prepared run ' + state['runId'] + '; bounded cleanup journal saved', flush=True)


def publish():
    state = load()
    image = 'acradtplatformdev.azurecr.io/' + REPOSITORY + ':stage1-' + state['runId']
    print(command(['docker', 'build', '-t', image, str(RUNTIME)]), flush=True)
    config = RUNTIME / 'docker-auth'
    config.mkdir(exist_ok=True)
    env = os.environ.copy()
    env['DOCKER_CONFIG'] = str(config)
    try:
        for attempt in range(8):
            try:
                token = az('acr', 'login', '-n', 'acradtplatformdev', '--expose-token')['accessToken']
                command(['docker', 'login', 'acradtplatformdev.azurecr.io', '--username', '00000000-0000-0000-0000-000000000000', '--password-stdin'], input=token, env=env)
                print(command(['docker', 'push', image], env=env), flush=True)
                break
            except RuntimeError:
                if attempt == 7:
                    raise
                print('Waiting for scoped registry grant propagation', flush=True)
                time.sleep(15)
        manifest = az('acr', 'manifest', 'show-metadata', '-r', 'acradtplatformdev', '-n', REPOSITORY + ':stage1-' + state['runId'])
        state['image'] = 'acradtplatformdev.azurecr.io/' + REPOSITORY + '@' + manifest['digest']
        state['imageDigest'] = manifest['digest']
        save(state)
        print('Published immutable probe image ' + state['imageDigest'], flush=True)
    finally:
        subprocess.run(['docker', 'logout', 'acradtplatformdev.azurecr.io'], env=env, capture_output=True)
        auth_file = config / 'config.json'
        if auth_file.exists():
            auth_file.unlink()


def restore_host(service, state):
    snapshot = state['apps'][service]
    quiet('webapp', 'stop', '-g', RG, '-n', 'api-adt-' + service + '-dev')
    rest('patch', app_id(service) + '?api-version=2024-11-01', {'properties': {'enabled': False, 'publicNetworkAccess': 'Disabled'}})
    payload = RUNTIME / 'restore-configuration.json'
    payload.write_text(json.dumps(snapshot['configuration']), encoding='utf-8')
    quiet('webapp', 'config', 'set', '-g', RG, '-n', 'api-adt-' + service + '-dev', '--generic-configurations', '@' + str(payload))
    original = {r['name']: r['value'] for r in snapshot['selectedSettings']}
    remove = [k for k in ['WEBSITES_PORT', 'DOCKER_REGISTRY_SERVER_URL'] if k not in original]
    if remove:
        quiet('webapp', 'config', 'appsettings', 'delete', '-g', RG, '-n', 'api-adt-' + service + '-dev', '--setting-names', *remove)
    if original:
        quiet('webapp', 'config', 'appsettings', 'set', '-g', RG, '-n', 'api-adt-' + service + '-dev', '--settings', *[k + '=' + v for k, v in original.items()])
    quiet('webapp', 'log', 'config', '-g', RG, '-n', 'api-adt-' + service + '-dev', '--docker-container-logging', 'filesystem' if snapshot['httpFileLogging']['enabled'] else 'off')
    log_configuration = rest('get', app_id(service) + '/config/logs?api-version=2024-11-01')['properties']
    restored_logging = dict(snapshot['httpFileLogging'])
    if restored_logging.get('retentionInDays') is None:
        restored_logging['retentionInDays'] = 0  # Azure ignores null updates; explicit no-retention preserves unset policy.
    log_configuration['httpLogs']['fileSystem'] = restored_logging
    rest('put', app_id(service) + '/config/logs?api-version=2024-11-01', {'properties': log_configuration})
    observed_logging = rest('get', app_id(service) + '/config/logs?api-version=2024-11-01')['properties']['httpLogs']['fileSystem']
    snapshot['restoredLogging'] = observed_logging
    snapshot['loggingRetentionNormalization'] = {'before': snapshot['httpFileLogging'].get('retentionInDays'), 'after': observed_logging.get('retentionInDays')}
    assert observed_logging['enabled'] == snapshot['httpFileLogging']['enabled']
    assert observed_logging['retentionInMb'] == snapshot['httpFileLogging']['retentionInMb']
    if snapshot['httpFileLogging'].get('retentionInDays') is not None:
        assert observed_logging['retentionInDays'] == snapshot['httpFileLogging']['retentionInDays']
    rest('patch', app_id(service) + '?api-version=2024-11-01', {'kind': snapshot['originalKind'], 'properties': {'enabled': False, 'publicNetworkAccess': 'Disabled'}})
    after = rest('get', app_id(service) + '?api-version=2024-11-01')
    assert after['properties']['enabled'] is False and after['properties']['publicNetworkAccess'] == 'Disabled'
    actual = az('webapp', 'config', 'show', '-g', RG, '-n', 'api-adt-' + service + '-dev', '--query', '{linuxFxVersion:linuxFxVersion,acrUseManagedIdentityCreds:acrUseManagedIdentityCreds,appCommandLine:appCommandLine,alwaysOn:alwaysOn}')
    assert actual == snapshot['configuration'], 'Original container configuration not fully restored'
    snapshot['restored'] = True
    save(state)
    print(service + ': disabled and original container configuration restored', flush=True)


def read_result(service, state):
    target = RUNTIME / (service + '-containerlogs.bin')
    result = subprocess.run([*CLI, 'rest', '--method', 'post', '--url', ARM + app_id(service) + '/containerlogs?api-version=2024-11-01', '--output-file', str(target), '--only-show-errors'], capture_output=True)
    if result.returncode or not target.exists():
        return None
    raw = target.read_bytes()
    if raw.startswith(b'PK'):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            raw = b'\n'.join(z.read(name) for name in z.namelist() if not name.endswith('/'))
    for encoded in re.findall(rb'PP_ACCESS_RESULT:([A-Za-z0-9+/=]+)', raw):
        try:
            data = json.loads(base64.b64decode(encoded))
            if data['RunId'] == state['runId'] and data['Role'] == service and datetime.fromisoformat(data['StartedUtc']) >= datetime.fromisoformat(state['apps'][service]['attemptStartedUtc']):
                return data
        except (ValueError, KeyError):
            pass
    return None


def run_service(service):
    state = load()
    assert state['image'] and not state.get('cleaned')
    if service == 'aquarium' and state.get('mode', 'data') == 'data' and state['settings'].get('Mode', 'data') == 'data':
        with sql_connect() as connection:
            connection.cursor().execute('DELETE FROM ' + state['settings']['SqlTable'])
    state['apps'][service]['restored'] = False
    state['apps'][service]['attemptStartedUtc'] = datetime.now(timezone.utc).isoformat()
    save(state)
    try:
        payload = RUNTIME / 'probe-configuration.json'
        payload.write_text(json.dumps({'linuxFxVersion': 'DOCKER|' + state['image'], 'acrUseManagedIdentityCreds': True, 'alwaysOn': True}), encoding='utf-8')
        quiet('webapp', 'config', 'set', '-g', RG, '-n', 'api-adt-' + service + '-dev', '--generic-configurations', '@' + str(payload))
        quiet('webapp', 'config', 'appsettings', 'set', '-g', RG, '-n', 'api-adt-' + service + '-dev', '--settings', 'WEBSITES_PORT=8080', 'DOCKER_REGISTRY_SERVER_URL=https://acradtplatformdev.azurecr.io')
        quiet('webapp', 'log', 'config', '-g', RG, '-n', 'api-adt-' + service + '-dev', '--docker-container-logging', 'filesystem')
        rest('patch', app_id(service) + '?api-version=2024-11-01', {'properties': {'enabled': True, 'publicNetworkAccess': 'Disabled'}})
        quiet('webapp', 'start', '-g', RG, '-n', 'api-adt-' + service + '-dev')
        print(service + ': probe started; public and SCM ingress remain blocked', flush=True)
        for attempt in range(45):
            result = read_result(service, state)
            if result:
                state['results'][service] = result
                save(state)
                print(json.dumps(result, indent=2), flush=True)
                return
            if attempt % 4 == 0:
                print(service + ': waiting for managed-identity probe result', flush=True)
            time.sleep(10)
        raise RuntimeError('Probe result not available within bounded startup interval; inspect retained management logs')
    finally:
        restore_host(service, state)


def cleanup():
    state = load()
    if state.get('cleaned') and not state.get('roleAssignmentIds') and not state.get('modifiedRoleAssignments') and all(a.get('restored') for a in state.get('apps', {}).values()):
        print(json.dumps({'runId': state['runId'], 'cleaned': True, 'alreadyCleaned': True}), flush=True)
        return
    state.setdefault('issuedRoleAssignmentIds', list(state['roleAssignmentIds']))
    errors = []
    for service, snapshot in state['apps'].items():
        if not snapshot.get('restored'):
            try:
                restore_host(service, state)
            except Exception as error:
                errors.append(service + ': ' + str(error))
    if state.get('mode') == 'configuration':
        try:
            cleanup_configuration_content(state)
        except Exception as error:
            errors.append('Synthetic content cleanup: ' + str(error))
    if 'settings' in state and state.get('mode', 'data') == 'data':
        try:
            with sql_connect() as connection:
                cursor = connection.cursor()
                for key in ['SqlTable', 'MigrationTable', 'ForbiddenTable']:
                    table = state['settings'][key]
                    assert state['runId'] in table and table.startswith('[Aquarium].[__Stage1')
                    cursor.execute("IF OBJECT_ID(N'" + table + "',N'U') IS NOT NULL DROP TABLE " + table)
                assert sql_security(cursor) == state['sqlSecurityBefore']
                state['sqlProbesAndTemporaryGrantsRemoved'] = True
        except Exception as error:
            errors.append('SQL cleanup: ' + str(error))
    for item in list(state.get('modifiedRoleAssignments', [])):
        try:
            actual = rest('put', item['id'] + '?api-version=2022-04-01', {'properties': item['originalProperties']})
            if any(actual['properties'].get(key) != value for key, value in item['originalProperties'].items()):
                raise RuntimeError('Original registry condition was not restored exactly')
            state.setdefault('restoredRoleAssignments', []).append(item['id'])
            state['modifiedRoleAssignments'].remove(item)
            save(state)
        except Exception as error:
            errors.append('Registry condition restoration: ' + str(error))
    for resource_id in list(state['roleAssignmentIds']):
        if any(error.startswith('Synthetic content cleanup:') for error in errors) and not resource_id.lower().startswith(REGISTRY.lower()):
            continue  # Retain owner setup access for bounded cleanup retry; never orphan test content.
        try:
            rest('delete', resource_id + '?api-version=2022-04-01')
            state['roleAssignmentIds'].remove(resource_id)
            save(state)
        except Exception as error:
            errors.append('Temporary grant cleanup: ' + str(error))
    state['cleanupErrors'] = errors
    state['cleaned'] = not errors
    save(state)
    print(json.dumps({'runId': state['runId'], 'cleaned': state['cleaned'], 'errors': errors}, indent=2), flush=True)
    if errors:
        raise RuntimeError('Cleanup incomplete; journal preserved for retry')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', required=True, choices=['all', 'prepare', 'publish', 'run', 'cleanup', 'status'])
    parser.add_argument('--mode', choices=['data','configuration'], default='data')
    parser.add_argument('--service', choices=list(IDENTITIES))
    args = parser.parse_args()
    if args.phase == 'all':
        try:
            prepare(args.mode)
            publish()
            for service in IDENTITIES:
                run_service(service)
        finally:
            if JOURNAL.exists(): cleanup()
        state = load()
        if set(state['results']) != set(IDENTITIES) or not all(r['Passed'] for r in state['results'].values()):
            raise RuntimeError('One or more real-identity checks failed; inspect recorded results')
    elif args.phase == 'prepare': prepare(args.mode)
    elif args.phase == 'publish': publish()
    elif args.phase == 'run':
        if not args.service: parser.error('--service required')
        run_service(args.service)
    elif args.phase == 'cleanup': cleanup()
    else:
        state = load()
        print(json.dumps({'runId': state['runId'], 'results': state['results'], 'cleaned': state['cleaned']}, indent=2))
