"""Bounded PP-only B1/APIM verification; no business data or credential persistence.

Start leaves hosts running for browser verification. Watch enforces a 15-minute
lease and memory cutoff and always cleans up. Cleanup can be retried independently.
"""
import argparse
import concurrent.futures
from datetime import datetime, timezone, timedelta
import importlib.util
import json
from pathlib import Path
import time
import urllib.request
import urllib.error
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('probe', ROOT / 'scripts/run-workload-access-verification.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)
p.PROBE = ROOT / 'tests/Stage1.HostingProbe'
p.RUNTIME = p.PROBE / '.runtime'
p.JOURNAL = p.RUNTIME / 'journal.json'
APIM = f'/subscriptions/{p.SUB}/resourceGroups/rg-platform-dev/providers/Microsoft.ApiManagement/service/apim-adt-platform-dev'
PLAN = f'/subscriptions/{p.SUB}/resourceGroups/rg-platform-dev/providers/Microsoft.Web/serverfarms/asp-platform-dev'
EVIDENCE = ROOT / 'docs/infrastructure/evidence/hosting-ingress-verification-2026-11-03.json'
TOKEN = None


def arm(method, path, body=None):
    global TOKEN
    if TOKEN is None:
        TOKEN = p.az('account', 'get-access-token', '--resource', 'https://management.azure.com/')['accessToken']
    request = urllib.request.Request(p.ARM + path, method=method,
        headers={'Authorization': 'Bearer ' + TOKEN, 'Content-Type': 'application/json'},
        data=json.dumps(body).encode() if body is not None else None)
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = response.read().decode('utf-8-sig')
            return json.loads(data) if data else None
    except urllib.error.HTTPError as error:
        # Management policy errors contain no user tokens; return only code/message.
        data = error.read().decode('utf-8-sig')
        try:
            detail = json.loads(data).get('error', {})
            message = str(detail.get('message', ''))[:1000]
        except ValueError:
            message = ''
        raise RuntimeError(f'ARM {method} {error.code}: {message}') from None


def request(url, token=None):
    headers = {'Authorization': 'Bearer ' + token} if token else {}
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=40) as response:
            data = response.read()
            try: value = json.loads(data)
            except ValueError: value = None
            return response.status, value
    except urllib.error.HTTPError as error:
        return error.code, None
    except (TimeoutError, urllib.error.URLError):
        return 598, None


def metrics(start):
    # Azure rejects a sub-minute timespan for PT1M. Round the start down.
    requested = datetime.fromisoformat(start.replace('Z', '+00:00'))
    start = min(requested, datetime.now(timezone.utc) - timedelta(minutes=2)).replace(second=0, microsecond=0).strftime('%Y-%m-%dT%H:%M:%SZ')
    end = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    result = arm('GET', PLAN + '/providers/microsoft.insights/metrics?api-version=2018-01-01&metricnames=MemoryPercentage,CpuPercentage&timespan=' + start + '/' + end + '&interval=PT1M&aggregation=Average,Maximum')
    return {item['name']['value']: [point for series in item['timeseries'] for point in series['data'] if 'average' in point] for item in result['value']}


def policy(service, backend):
    audience = 'bcbab13c-f80e-4dc3-8e12-f94bc2491461' if service == 'aquarium' else 'df2085cf-7b78-4c21-99fb-70f46b48490a'
    scope_prefix = 'Aquarium' if service == 'aquarium' else 'Tracking'
    return f'''<policies><inbound>
      <!-- Deliberately no inbound base: shared bootstrap is fail-closed 503.
           This isolated verification API supplies its complete inbound policy. -->
      <cors allow-credentials="false"><allowed-origins><origin>http://localhost:4200</origin><origin>https://parameterpilot.com</origin><origin>https://www.parameterpilot.com</origin></allowed-origins><allowed-methods><method>GET</method><method>POST</method></allowed-methods><allowed-headers><header>authorization</header><header>content-type</header></allowed-headers></cors>
      <choose><when condition='@(!context.Request.Url.Path.EndsWith("/health"))'>
        <validate-jwt header-name="Authorization" require-scheme="Bearer" require-signed-tokens="true" require-expiration-time="true" failed-validation-httpcode="401" clock-skew="60">
          <openid-config url="https://parameterpilotdev.ciamlogin.com/0e9365ce-9928-49a0-a455-73c5ad29cf34/v2.0/.well-known/openid-configuration" />
          <audiences><audience>{audience}</audience></audiences>
          <required-claims>
            <claim name="tid"><value>0e9365ce-9928-49a0-a455-73c5ad29cf34</value></claim>
            <claim name="azp"><value>fc5f67a2-e6a2-4e3f-a49b-2b2410a6060b</value></claim>
            <claim name="scp" match="any" separator=" "><value>@(context.Request.Method == "POST" ? "{scope_prefix}.Write" : "{scope_prefix}.Read")</value></claim>
          </required-claims>
        </validate-jwt>
      </when></choose>
      <set-backend-service base-url="{escape(backend)}" />
    </inbound><backend><forward-request timeout="60" /></backend><outbound /><on-error /></policies>'''


def start():
    print(p.command(['dotnet', 'publish', str(p.PROBE / 'Stage1.HostingProbe.csproj'), '-c', 'Release', '-o', str(p.RUNTIME / 'publish'), '--no-restore']), flush=True)
    p.prepare('hosting')  # Isolated journal; no SQL or Cosmos operations.
    state = p.load()
    state['apimApis'] = []
    state['originalGlobalPolicy'] = arm('GET', APIM + '/policies/policy?api-version=2024-05-01')['properties']['value']
    state['baselineMetrics'] = metrics((datetime.now(timezone.utc) - timedelta(minutes=15)).strftime('%Y-%m-%dT%H:%M:%SZ'))
    state['planBefore'] = arm('GET', PLAN + '?api-version=2024-11-01')['sku']
    state['otherAppsBefore'] = p.az('webapp', 'list', '--query', "[?resourceGroup!='rg-parameterpilot-dev'].{id:id,state:state,plan:serverFarmId}")
    apim = arm('GET', APIM + '?api-version=2024-05-01')
    assert apim['sku']['name'] == 'Developer' and state['planBefore']['name'] == 'B1'
    apim_ips = apim['properties']['publicIPAddresses']
    assert apim_ips and all('/' not in ip and ':' not in ip for ip in apim_ips)
    tracking = arm('GET', p.app_id('tracking') + '?api-version=2024-11-01')
    tracking_ips = tracking['properties']['possibleOutboundIpAddresses'].split(',')
    state['addressing'] = {'apim': apim_ips, 'trackingPossibleOutbound': tracking_ips}
    certificates = json.loads((ROOT / 'docs/infrastructure/evidence/obo-certificates-2026-11-03.json').read_text())
    state['settings'].update({'AquariumUrl': 'https://api-adt-aquarium-dev.azurewebsites.net', 'CertificateSecretUri': certificates['development']['secretId'], 'CertificateThumbprint': certificates['development']['thumbprint']})
    p.save(state)
    (p.RUNTIME / 'publish/probe-settings.json').write_text(json.dumps(state['settings']))
    p.publish()
    state = p.load()
    state['gateway'] = apim['properties']['gatewayUrl']
    for service in p.IDENTITIES:
        config = arm('GET', p.app_id(service) + '/config/web?api-version=2024-11-01')['properties']
        keys = ['ipSecurityRestrictions', 'ipSecurityRestrictionsDefaultAction', 'scmIpSecurityRestrictions', 'scmIpSecurityRestrictionsDefaultAction', 'scmIpSecurityRestrictionsUseMain']
        state['apps'][service]['ingressBefore'] = {key: config.get(key) for key in keys}
        allowed = apim_ips + (tracking_ips if service == 'aquarium' else [])
        rules = [{'ipAddress': ip + '/32', 'action': 'Allow', 'priority': 100 + i, 'name': ('apim-' if i < len(apim_ips) else 'tracking-egress-') + str(i)} for i, ip in enumerate(dict.fromkeys(allowed))]
        state['apps'][service]['restored'] = False
        state['apps'][service]['ingressRestored'] = False
        p.save(state)
        p.rest('PATCH', p.app_id(service) + '/config/web?api-version=2024-11-01', {'properties': {'ipSecurityRestrictions': rules, 'ipSecurityRestrictionsDefaultAction': 'Deny', 'scmIpSecurityRestrictionsUseMain': False, 'scmIpSecurityRestrictions': [], 'scmIpSecurityRestrictionsDefaultAction': 'Deny', 'linuxFxVersion': 'DOCKER|' + state['image'], 'acrUseManagedIdentityCreds': True, 'alwaysOn': True}})
        p.quiet('webapp', 'config', 'appsettings', 'set', '-g', p.RG, '-n', 'api-adt-' + service + '-dev', '--settings', 'WEBSITES_PORT=8080', 'DOCKER_REGISTRY_SERVER_URL=https://acradtplatformdev.azurecr.io')
        p.quiet('webapp', 'log', 'config', '-g', p.RG, '-n', 'api-adt-' + service + '-dev', '--docker-container-logging', 'filesystem')
        p.rest('PATCH', p.app_id(service) + '?api-version=2024-11-01', {'properties': {'enabled': True, 'publicNetworkAccess': 'Enabled'}})
        p.quiet('webapp', 'start', '-g', p.RG, '-n', 'api-adt-' + service + '-dev')
        name = 'pp-stage1-' + state['runId'] + '-' + service
        api = APIM + '/apis/' + name
        path = 'pp-stage1-' + state['runId'] + '/' + service
        state['apimApis'].append({'id': api, 'path': path, 'service': service})
        p.save(state)  # Journal before each creation; never overwrite another API.
        existing = arm('GET', APIM + '/apis?api-version=2024-05-01')['value']
        assert not any(item['name'] == name for item in existing)
        arm('PUT', api + '?api-version=2024-05-01', {'properties': {'displayName': 'PP temporary Stage 1 ' + service, 'path': path, 'protocols': ['https'], 'subscriptionRequired': False, 'serviceUrl': 'https://api-adt-' + service + '-dev.azurewebsites.net'}})
        for verb in ['GET', 'POST']:
            arm('PUT', api + '/operations/' + verb.lower() + '?api-version=2024-05-01', {'properties': {'displayName': verb + ' verification', 'method': verb, 'urlTemplate': '/*', 'responses': []}})
        arm('PUT', api + '/policies/policy?api-version=2024-05-01', {'properties': {'format': 'rawxml', 'value': policy(service, 'https://api-adt-' + service + '-dev.azurewebsites.net')}})
    state['startedUtc'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    p.save(state)
    print('Both PP hosts started with explicit /32 allow rules; SCM remains denied. Verifying gateway health.', flush=True)
    startup_deadline = time.monotonic() + 600
    for attempt in range(40):
        if time.monotonic() > startup_deadline:
            raise RuntimeError('Ten-minute startup lease expired')
        if attempt % 4 == 0:
            memory = metrics(state['startedUtc']).get('MemoryPercentage', [])
            if len(memory) >= 2 and all(point['average'] >= 92 for point in memory[-2:]):
                raise RuntimeError('B1 memory safety cutoff reached during startup')
        healthy = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda api: request(state['gateway'] + '/' + api['path'] + '/health'), state['apimApis']))
        for api, (status, body) in zip(state['apimApis'], results):
            healthy[api['service']] = bool(status == 200 and body and body.get('run') == state['runId'])
        if all(healthy.values()): break
        print('Waiting for container/gateway startup: ' + json.dumps(healthy), flush=True)
        time.sleep(10)
    else: raise RuntimeError('Both hosts did not become healthy through APIM')
    state['initialNetworkChecks'] = {}
    for api in state['apimApis']:
        root = state['gateway'] + '/' + api['path']
        service = api['service']
        state['initialNetworkChecks'][service] = {'apimHealth': True, 'noTokenDenied': request(root + '/read')[0] == 401, 'invalidTokenDenied': request(root + '/read', 'invalid')[0] == 401, 'directHealthDenied': request('https://api-adt-' + service + '-dev.azurewebsites.net/health')[0] == 403}
    assert all(all(checks.values()) for checks in state['initialNetworkChecks'].values())
    p.save(state)
    (ROOT / 'tests/Stage1.IdentityProbe/.hosting.json').write_text(json.dumps({'runId': state['runId'], 'gateway': state['gateway'], 'paths': {api['service']: api['path'] for api in state['apimApis']}}))
    print('Network checks passed. Ready for real customer browser tokens; start the bounded watcher now.', flush=True)


def cleanup():
    state = p.load()
    for service, snapshot in state['apps'].items():
        if not snapshot.get('restored'):
            p.restore_host(service, state)
        if snapshot.get('ingressBefore') and not snapshot.get('ingressRestored'):
            p.rest('PATCH', p.app_id(service) + '/config/web?api-version=2024-11-01', {'properties': snapshot['ingressBefore']})
            actual = arm('GET', p.app_id(service) + '/config/web?api-version=2024-11-01')['properties']
            assert all(actual.get(key) == value for key, value in snapshot['ingressBefore'].items())
            snapshot['ingressRestored'] = True
            p.save(state)
    for api in list(state.get('apimApis', [])):
        try: arm('DELETE', api['id'] + '?api-version=2024-05-01&deleteRevisions=true')
        except RuntimeError as error:
            if '404' not in str(error): raise
        state['apimApis'].remove(api)
        p.save(state)
    p.cleanup()
    state = p.load()
    global_policy = arm('GET', APIM + '/policies/policy?api-version=2024-05-01')['properties']['value']
    assert global_policy == state.get('originalGlobalPolicy', global_policy)
    assert arm('GET', PLAN + '?api-version=2024-11-01')['sku'] == state.get('planBefore', arm('GET', PLAN + '?api-version=2024-11-01')['sku'])
    others = p.az('webapp', 'list', '--query', "[?resourceGroup!='rg-parameterpilot-dev'].{id:id,state:state,plan:serverFarmId}")
    assert sorted(others, key=lambda x:x['id']) == sorted(state.get('otherAppsBefore', others), key=lambda x:x['id'])
    state['sharedSettingsPreserved'] = True
    p.save(state)
    config = ROOT / 'tests/Stage1.IdentityProbe/.hosting.json'
    if config.exists(): config.unlink()
    print('PP hosts disabled; original restrictions, shared policy/SKU and other app states verified; temporary routes/grants removed.', flush=True)


def watch():
    state = p.load()
    try:
        for attempt in range(30):
            state = p.load()
            state['hostingMetrics'] = metrics(state['startedUtc'])
            p.save(state)
            memory = state['hostingMetrics'].get('MemoryPercentage', [])
            if len(memory) >= 2 and all(point['average'] >= 92 for point in memory[-2:]):
                raise RuntimeError('B1 memory safety cutoff reached; no scale or other-product changes attempted')
            result = ROOT / 'docs/infrastructure/evidence/hosting-customer-verification-2026-11-03.json'
            if result.exists():
                browser = json.loads(result.read_text())
                if browser.get('runId') == state['runId']:
                    state['customerChecks'] = browser
                    p.save(state)
                    break
            print('Bounded hosting watch: waiting for browser checks; memory=' + str(memory[-1]['average'] if memory else 'pending'), flush=True)
            time.sleep(30)
        else: raise RuntimeError('15-minute browser verification lease expired')
    finally:
        cleanup()
        state = p.load()
        EVIDENCE.write_text(json.dumps({key: state.get(key) for key in ['runId', 'startedUtc', 'image', 'addressing', 'baselineMetrics', 'hostingMetrics', 'initialNetworkChecks', 'customerChecks', 'cleaned', 'sharedSettingsPreserved', 'cleanupErrors']}, indent=2) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase', choices=['start', 'watch', 'cleanup'], required=True)
    args = parser.parse_args()
    if args.phase == 'start':
        try: start()
        except BaseException as error:
            if p.JOURNAL.exists() and not p.load().get('cleaned'): cleanup()
            if p.JOURNAL.exists():
                state = p.load()
                (EVIDENCE.parent / ('hosting-startup-failure-' + state['runId'] + '.json')).write_text(json.dumps({'runId': state['runId'], 'failure': type(error).__name__, 'cleaned': state.get('cleaned'), 'sharedSettingsPreserved': state.get('sharedSettingsPreserved')}, indent=2) + '\n')
            raise
    elif args.phase == 'watch': watch()
    else: cleanup()
