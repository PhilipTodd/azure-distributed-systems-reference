"""Verify owner access to Aquarium platform logs during an approved temporary window."""
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('activation', ROOT / 'scripts/verify-aquarium-activation.py')
activation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(activation)
p = activation.p
SITE = activation.SITE
API = activation.API
APP = activation.APP
WORKSPACE = f'/subscriptions/{p.SUB}/resourceGroups/rg-platform-dev/providers/Microsoft.OperationalInsights/workspaces/log-platform-dev'
WORKSPACE_ID = 'acf80e91-3324-43f3-8844-b958986f0b9d'
DIAGNOSTICS = SITE + '/providers/Microsoft.Insights/diagnosticSettings'
DIAGNOSTIC_API = '?api-version=2021-05-01-preview'
SETTING = DIAGNOSTICS + '/pp-step7-aquarium-platform' + DIAGNOSTIC_API


def log_counts(token, start):
    query = (
        f'AppServicePlatformLogs | where _ResourceId =~ "{SITE}" '
        f'| where TimeGenerated >= datetime({start}) '
        '| summarize events=count(), startupEvents=countif(Message contains "container" '
        'or Message contains "startup" or Message contains "warmup"), latest=max(TimeGenerated)'
    )
    request = urllib.request.Request(
        f'https://api.loganalytics.azure.com/v1/workspaces/{WORKSPACE_ID}/query',
        data=json.dumps({'query': query}).encode(),
        headers={'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)['tables'][0]['rows'][0]


def main():
    account = p.az('account', 'show')
    if account['id'] != p.SUB or account['user']['type'] != 'user':
        raise RuntimeError('Expected the owner session in the Development subscription')
    site = p.rest('get', SITE + API)['properties']
    config = activation.configuration()
    if (site['enabled'] or site['publicNetworkAccess'] != 'Disabled' or config['linuxFxVersion']
            or not config['acrUseManagedIdentityCreds']
            or any(config[key] != 'Deny' for key in ('ipSecurityRestrictionsDefaultAction', 'scmIpSecurityRestrictionsDefaultAction'))
            or any(rule.get('action') == 'Allow' for key in ('ipSecurityRestrictions', 'scmIpSecurityRestrictions') for rule in config[key] or [])):
        raise RuntimeError('Aquarium differs from the approved closed baseline')
    if p.rest('get', DIAGNOSTICS + DIAGNOSTIC_API)['value']:
        raise RuntimeError('Aquarium already has diagnostic settings')
    before = activation.selected_settings()
    p.RUNTIME.mkdir(parents=True, exist_ok=True)
    (p.RUNTIME / 'step7-aquarium-diagnostics-snapshot.json').write_text(
        json.dumps({'configuration': config, 'selectedSettings': before}, indent=2), encoding='utf-8')
    start = datetime.now(timezone.utc).isoformat()
    evidence = {'date': '2026-11-04', 'image': activation.IMAGE, 'startUtc': start,
                'workspace': 'log-platform-dev', 'category': 'AppServicePlatformLogs',
                'effectiveRetentionDays': 30, 'hostRestored': False, 'diagnosticSettingRemoved': False}
    token = p.az('account', 'get-access-token', '--resource', 'https://api.loganalytics.io')['accessToken']
    log_counts(token, start)
    created = False
    try:
        setting = p.rest('put', SETTING, {'properties': {
            'workspaceId': WORKSPACE, 'logAnalyticsDestinationType': 'Dedicated',
            'logs': [{'category': 'AppServicePlatformLogs', 'enabled': True}], 'metrics': [],
        }})
        created = True
        enabled = [item['category'] for item in setting['properties']['logs'] if item['enabled']]
        if enabled != ['AppServicePlatformLogs'] or setting['properties']['workspaceId'].lower() != WORKSPACE.lower():
            raise RuntimeError('Diagnostic setting differs from the approved category or destination')
        print('Temporary Aquarium platform-log export verified.', flush=True)
        try:
            p.rest('patch', SITE + '/config/web' + API, {'properties': {'linuxFxVersion': 'DOCKER|' + activation.IMAGE}})
            p.quiet('webapp', 'config', 'appsettings', 'set', *APP, '--settings',
                    *[f'{key}={value}' for key, value in activation.SETTINGS.items()])
            p.rest('patch', SITE + API, {'properties': {'enabled': True, 'publicNetworkAccess': 'Disabled'}})
            p.quiet('webapp', 'start', *APP)
            print('Aquarium started with network access disabled. Waiting two minutes for platform events.', flush=True)
            time.sleep(120)
        finally:
            try:
                p.quiet('webapp', 'stop', *APP)
            finally:
                p.rest('patch', SITE + API, {'properties': {'enabled': False, 'publicNetworkAccess': 'Disabled'}})
            p.rest('patch', SITE + '/config/web' + API, {'properties': {'linuxFxVersion': config['linuxFxVersion'] or ''}})
            remove = sorted(activation.SETTINGS.keys() - before.keys())
            if remove:
                p.quiet('webapp', 'config', 'appsettings', 'delete', *APP, '--setting-names', *remove)
            if before:
                p.quiet('webapp', 'config', 'appsettings', 'set', *APP, '--settings',
                        *[f'{key}={value}' for key, value in before.items()])
            site = p.rest('get', SITE + API)['properties']
            observed = activation.configuration()
            observed['linuxFxVersion'] = observed['linuxFxVersion'] or ''
            config['linuxFxVersion'] = config['linuxFxVersion'] or ''
            evidence['hostRestored'] = (
                observed == config and activation.selected_settings() == before
                and not site['enabled'] and site['publicNetworkAccess'] == 'Disabled'
            )
            if not evidence['hostRestored']:
                raise RuntimeError('Aquarium restoration differs from the snapshot')
            print('Aquarium disabled and original settings verified. Checking log ingestion.', flush=True)
        deadline = time.monotonic() + 300
        while time.monotonic() < deadline:
            total, startup, latest = log_counts(token, start)
            evidence.update(platformEvents=total, startupEvents=startup, latestEventUtc=latest)
            if startup:
                print(f'Owner query returned {startup} Aquarium startup-related platform events.', flush=True)
                break
            time.sleep(20)
    finally:
        try:
            if created:
                p.rest('delete', SETTING)
                evidence['diagnosticSettingRemoved'] = not p.rest('get', DIAGNOSTICS + DIAGNOSTIC_API)['value']
                if not evidence['diagnosticSettingRemoved']:
                    raise RuntimeError('Temporary diagnostic setting removal was not verified')
                print('Temporary diagnostic export removed and verified.', flush=True)
        finally:
            path = ROOT / 'docs/infrastructure/evidence/step-7-aquarium-platform-diagnostics-2026-11-04.json'
            path.write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    if not evidence.get('startupEvents'):
        raise RuntimeError('No startup-related platform events arrived in the bounded window')


if __name__ == '__main__':
    main()
