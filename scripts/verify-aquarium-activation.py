"""Owner-authorised APIM health check of the GitHub verification image."""
import importlib.util
from ipaddress import IPv4Address
import json
from pathlib import Path
import time

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('probe', ROOT / 'scripts/run-workload-access-verification.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
hosting_spec = importlib.util.spec_from_file_location('hosting', ROOT / 'scripts/run-hosting-verification.py')
hosting = importlib.util.module_from_spec(hosting_spec)
hosting_spec.loader.exec_module(hosting)
SITE = p.app_id('aquarium')
API = '?api-version=2024-11-01'
APIM_VERSION = '?api-version=2024-05-01'
ROUTE = 'pp-step7-aquarium-health'
BACKEND = 'https://api-adt-aquarium-dev.azurewebsites.net'
EXPECTED_RUN = 'github-41735129057-1'
APP = ('-g', p.RG, '-n', 'api-adt-aquarium-dev')
IMAGE = 'acradtplatformdev.azurecr.io/parameterpilot/aquarium-api@sha256:ac70bc6440656be94d273835bc14894bcbf873a43ba064e84cef9ade0e12e28f'
SETTINGS = {
    'WEBSITES_PORT': '8080',
    'DOCKER_REGISTRY_SERVER_URL': 'https://acradtplatformdev.azurecr.io',
    'WEBSITE_WARMUP_PATH': '/health',
    'WEBSITE_WARMUP_STATUSES': '200',
}
CONFIG_KEYS = ('linuxFxVersion', 'healthCheckPath')
ACCESS_KEYS = ('ipSecurityRestrictions', 'ipSecurityRestrictionsDefaultAction',
               'scmIpSecurityRestrictions', 'scmIpSecurityRestrictionsDefaultAction',
               'scmIpSecurityRestrictionsUseMain', 'acrUseManagedIdentityCreds')


def configuration():
    config = p.rest('get', SITE + '/config/web' + API)['properties']
    return {key: config.get(key) for key in CONFIG_KEYS + ACCESS_KEYS}


def selected_settings():
    query = '[?' + ' || '.join(f"name=='{key}'" for key in SETTINGS) + '].{name:name,value:value}'
    return {row['name']: row['value'] for row in p.az('webapp', 'config', 'appsettings', 'list', *APP, '--query', query)}


def main():
    account = p.az('account', 'show')
    if account['id'] != p.SUB or account['user']['type'] != 'user':
        raise RuntimeError('Expected owner session on the Development subscription')
    site = p.rest('get', SITE + API)['properties']
    before = configuration()
    if (site['enabled'] or site.get('publicNetworkAccess') != 'Disabled'
            or before['linuxFxVersion'] or not before['acrUseManagedIdentityCreds']
            or any(before[key] != 'Deny' for key in ('ipSecurityRestrictionsDefaultAction', 'scmIpSecurityRestrictionsDefaultAction'))
            or any(rule.get('action') == 'Allow' for key in ('ipSecurityRestrictions', 'scmIpSecurityRestrictions') for rule in before[key] or [])):
        raise RuntimeError('Aquarium baseline differs from the approved closed host')
    settings = selected_settings()
    logs_path = SITE + '/config/logs' + API
    logs_before = p.rest('get', logs_path)['properties']
    gateway = hosting.arm('GET', hosting.APIM + APIM_VERSION)
    addresses = [str(IPv4Address(ip)) for ip in gateway['properties']['publicIPAddresses']]
    if gateway['sku']['name'] != 'Developer' or not addresses:
        raise RuntimeError('Expected the approved Developer APIM gateway with IPv4 addresses')
    api = hosting.APIM + '/apis/' + ROUTE
    existing = hosting.arm('GET', hosting.APIM + '/apis' + APIM_VERSION)['value']
    if any(item['name'] == ROUTE or item['properties']['path'] == ROUTE for item in existing):
        raise RuntimeError('The temporary API name or route is already in use')
    policy_path = hosting.APIM + '/policies/policy' + APIM_VERSION
    shared_policy = hosting.arm('GET', policy_path)['properties']['value']
    rules = [{'name': f'step7-apim-{index}', 'ipAddress': ip + '/32', 'action': 'Allow', 'priority': 100 + index}
             for index, ip in enumerate(addresses)]
    p.RUNTIME.mkdir(parents=True, exist_ok=True)
    snapshot = p.RUNTIME / 'step7-aquarium-snapshot.json'
    snapshot.write_text(json.dumps({'configuration': before, 'selectedSettings': settings, 'logging': logs_before, 'temporaryApi': api}, indent=2))
    evidence = {'date': '2026-11-04', 'image': IMAGE, 'healthPassed': False, 'restored': False, 'apimSourceAddresses': addresses}
    api_created = False
    try:
        hosting.arm('PUT', api + APIM_VERSION, {'properties': {'displayName': 'Temporary Aquarium health verification',
                    'path': ROUTE, 'protocols': ['https'], 'subscriptionRequired': False, 'serviceUrl': BACKEND}})
        api_created = True
        hosting.arm('PUT', api + '/operations/health' + APIM_VERSION, {'properties': {
                    'displayName': 'Health', 'method': 'GET', 'urlTemplate': '/health', 'responses': []}})
        hosting.arm('PUT', api + '/policies/policy' + APIM_VERSION, {'properties': {
                    'format': 'rawxml', 'value': hosting.policy('aquarium', BACKEND)}})
        p.rest('patch', SITE + '/config/web' + API, {'properties': {
            'linuxFxVersion': 'DOCKER|' + IMAGE, 'healthCheckPath': '/health',
            'ipSecurityRestrictions': rules, 'ipSecurityRestrictionsDefaultAction': 'Deny',
            'scmIpSecurityRestrictionsUseMain': False, 'scmIpSecurityRestrictions': [],
            'scmIpSecurityRestrictionsDefaultAction': 'Deny'}})
        p.quiet('webapp', 'config', 'appsettings', 'set', *APP, '--settings', *[f'{k}={v}' for k, v in SETTINGS.items()])
        p.quiet('webapp', 'log', 'config', *APP, '--docker-container-logging', 'filesystem')
        p.rest('patch', SITE + API, {'properties': {'enabled': True, 'publicNetworkAccess': 'Enabled'}})
        deadline = time.monotonic() + 540
        p.quiet('webapp', 'start', *APP)
        print('Aquarium start requested with APIM-only access and SCM denied.', flush=True)
        url = gateway['properties']['gatewayUrl'] + '/' + ROUTE + '/health'
        while time.monotonic() < deadline:
            status, body = hosting.request(url)
            evidence['gatewayStatus'] = status
            if status == 200 and isinstance(body, dict) and body.get('role') == 'aquarium' and body.get('run') == EXPECTED_RUN:
                evidence.update(healthPassed=True, runMarker=EXPECTED_RUN, started=body.get('started'))
                evidence['directBackendStatus'] = hosting.request(BACKEND + '/health')[0]
                if evidence['directBackendStatus'] != 403:
                    raise RuntimeError('Direct Aquarium request did not return the expected 403')
                print('APIM health returned HTTP 200 with the expected image marker. Direct access returned 403.', flush=True)
                break
            time.sleep(20)
    except Exception as error:
        evidence['failureType'] = type(error).__name__
        raise
    finally:
        try:
            try:
                p.quiet('webapp', 'stop', *APP)
            finally:
                p.rest('patch', SITE + API, {'properties': {'enabled': False, 'publicNetworkAccess': 'Disabled'}})
            restore = {key: before[key] or '' for key in CONFIG_KEYS}
            restore.update({key: before[key] for key in ACCESS_KEYS if key != 'acrUseManagedIdentityCreds'})
            p.rest('patch', SITE + '/config/web' + API, {'properties': restore})
            remove = sorted(SETTINGS.keys() - settings.keys())
            if remove:
                p.quiet('webapp', 'config', 'appsettings', 'delete', *APP, '--setting-names', *remove)
            if settings:
                p.quiet('webapp', 'config', 'appsettings', 'set', *APP, '--settings', *[f'{k}={v}' for k, v in settings.items()])
            p.rest('put', logs_path, {'properties': logs_before})
            after = configuration()
            for key in CONFIG_KEYS:
                after[key] = after[key] or None
                before[key] = before[key] or None
            site = p.rest('get', SITE + API)['properties']
            evidence['loggingRestored'] = p.rest('get', logs_path)['properties'] == logs_before
            evidence['restored'] = after == before and selected_settings() == settings and not site['enabled'] and site['publicNetworkAccess'] == 'Disabled' and evidence['loggingRestored']
            if not evidence['restored']:
                raise RuntimeError('Aquarium restoration readback differs from the snapshot')
            print('Aquarium disabled and original settings verified.', flush=True)
        finally:
            try:
                if api_created:
                    hosting.arm('DELETE', api + APIM_VERSION + '&deleteRevisions=true')
                    remaining = hosting.arm('GET', hosting.APIM + '/apis' + APIM_VERSION)['value']
                    evidence['temporaryApiRemoved'] = not any(item['name'] == ROUTE for item in remaining)
                    evidence['sharedPolicyPreserved'] = hosting.arm('GET', policy_path)['properties']['value'] == shared_policy
                    if not evidence['temporaryApiRemoved'] or not evidence['sharedPolicyPreserved']:
                        raise RuntimeError('APIM cleanup verification failed')
            finally:
                path = ROOT / 'docs/infrastructure/evidence/step-7-aquarium-apim-health-2026-11-04.json'
                path.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    if not evidence['healthPassed']:
        raise RuntimeError('APIM did not return the expected health response within the activation window')


if __name__ == '__main__':
    main()
