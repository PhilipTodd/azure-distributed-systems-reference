"""Read the approved image's startup log via a temporary owner-only SCM rule."""
from datetime import datetime, timezone
import importlib.util
from ipaddress import IPv4Address
import json
from pathlib import Path
import re
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('activation', ROOT / 'scripts/verify-aquarium-activation.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)
p = a.p


def startup_verified(start):
    records = p.az('webapp', 'log', 'startup', 'list', *a.APP)
    for record in records:
        if record['Outcome'] != 'success' or datetime.fromisoformat(record['LastWriteTimeUtc']) < start:
            continue
        raw = p.command([*p.CLI, 'webapp', 'log', 'startup', 'show', *a.APP,
                         '--filename', record['Filename'], '--only-show-errors'])
        digest_seen = False
        for line in raw.splitlines():
            stamp = re.match(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})', line)
            if not stamp or datetime.fromisoformat(stamp[0]) < start:
                continue
            digest_seen |= a.IMAGE in line
            if digest_seen and ('Site startup probe succeeded' in line or 'WarmUpProbeSucceeded' in line):
                return stamp[0]
    return None


def main():
    account = p.az('account', 'show')
    if account['id'] != p.SUB or account['user']['type'] != 'user':
        raise RuntimeError('Expected owner session in the Development subscription')
    site = p.rest('get', a.SITE + a.API)['properties']
    config = a.configuration()
    if (site['enabled'] or site['publicNetworkAccess'] != 'Disabled' or config['linuxFxVersion']
            or not config['acrUseManagedIdentityCreds']
            or any(config[key] != 'Deny' for key in ('ipSecurityRestrictionsDefaultAction', 'scmIpSecurityRestrictionsDefaultAction'))
            or any(rule.get('action') == 'Allow' for key in ('ipSecurityRestrictions', 'scmIpSecurityRestrictions') for rule in config[key] or [])):
        raise RuntimeError('Expected the reviewed disabled Aquarium baseline')
    publishing = a.SITE + '/basicPublishingCredentialsPolicies/scm' + a.API
    if p.rest('get', publishing)['properties']['allow']:
        raise RuntimeError('SCM password publishing must be disabled')
    with urllib.request.urlopen('https://api.ipify.org', timeout=10) as response:
        ip = IPv4Address(response.read(64).decode().strip())
    if not ip.is_global:
        raise RuntimeError('Expected a public IPv4 address')
    before = a.selected_settings()
    p.RUNTIME.mkdir(parents=True, exist_ok=True)
    (p.RUNTIME / 'step7-startup-log-snapshot.json').write_text(
        json.dumps({'configuration': config, 'selectedSettings': before}, indent=2), encoding='utf-8')
    evidence = {'image': a.IMAGE, 'startupVerified': False, 'restored': False}
    apim_evidence = json.loads((ROOT / 'docs/infrastructure/evidence/step-7-aquarium-apim-health-2026-11-04.json').read_text(encoding='utf-8'))
    retained_start = (datetime.fromisoformat(apim_evidence['started'])
                      if apim_evidence['image'] == a.IMAGE and apim_evidence['healthPassed'] else None)
    try:
        p.rest('patch', a.SITE + '/config/web' + a.API, {'properties': {
            'linuxFxVersion': 'DOCKER|' + a.IMAGE,
            'scmIpSecurityRestrictionsUseMain': False,
            'scmIpSecurityRestrictions': [{'name': 'pp-owner-startup-logs',
                                           'ipAddress': f'{ip}/32', 'priority': 100, 'action': 'Allow'}],
        }})
        p.quiet('webapp', 'config', 'appsettings', 'set', *a.APP, '--settings',
                *[f'{key}={value}' for key, value in a.SETTINGS.items()])
        live = a.configuration()
        if live['ipSecurityRestrictions'] != config['ipSecurityRestrictions'] or live['ipSecurityRestrictionsDefaultAction'] != 'Deny':
            raise RuntimeError('Main site restrictions differ from the baseline')
        allowed = [rule['ipAddress'] for rule in live['scmIpSecurityRestrictions'] or [] if rule.get('action') == 'Allow']
        if (allowed != [f'{ip}/32'] or live['scmIpSecurityRestrictionsUseMain'] is not False
                or live['scmIpSecurityRestrictionsDefaultAction'] != 'Deny'):
            raise RuntimeError('SCM rules differ from the approved single-address exception')
        start = datetime.now(timezone.utc)
        p.rest('patch', a.SITE + a.API, {'properties': {'enabled': True, 'publicNetworkAccess': 'Enabled'}})
        deadline = time.monotonic() + 480
        p.quiet('webapp', 'start', *a.APP)
        print('Aquarium startup requested with main API denied and one SCM diagnostic address.', flush=True)
        while time.monotonic() < deadline:
            try:
                timestamp = startup_verified(start)
                source = 'current activation'
                if not timestamp and retained_start:
                    timestamp = startup_verified(retained_start)
                    source = 'retained APIM verification deployment'
            except RuntimeError:
                timestamp = None
            if timestamp:
                evidence.update(startupVerified=True, warmupSucceededUtc=timestamp, ownerReadVerified=True, source=source)
                print('Owner read the approved image digest and successful warm-up in the startup log.', flush=True)
                break
            time.sleep(15)
    finally:
        try:
            p.rest('patch', a.SITE + a.API, {'properties': {'publicNetworkAccess': 'Disabled'}})
            try:
                p.quiet('webapp', 'stop', *a.APP)
            finally:
                p.rest('patch', a.SITE + a.API, {'properties': {'enabled': False, 'publicNetworkAccess': 'Disabled'}})
            p.rest('patch', a.SITE + '/config/web' + a.API, {'properties': {
                'linuxFxVersion': config['linuxFxVersion'] or '',
                'scmIpSecurityRestrictions': config['scmIpSecurityRestrictions'],
                'scmIpSecurityRestrictionsUseMain': config['scmIpSecurityRestrictionsUseMain'],
            }})
            remove = sorted(a.SETTINGS.keys() - before.keys())
            if remove:
                p.quiet('webapp', 'config', 'appsettings', 'delete', *a.APP, '--setting-names', *remove)
            if before:
                p.quiet('webapp', 'config', 'appsettings', 'set', *a.APP, '--settings',
                        *[f'{key}={value}' for key, value in before.items()])
            after = p.rest('get', a.SITE + a.API)['properties']
            evidence['restored'] = (a.configuration() == config and a.selected_settings() == before
                                    and not after['enabled'] and after['publicNetworkAccess'] == 'Disabled'
                                    and not p.rest('get', publishing)['properties']['allow'])
            if not evidence['restored']:
                raise RuntimeError('Aquarium readback differs from the saved baseline')
            print('Aquarium disabled and SCM exception removed.', flush=True)
        finally:
            (ROOT / 'docs/infrastructure/evidence/step-7-aquarium-startup-log-2026-11-04.json').write_text(
                json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
    if not evidence['startupVerified']:
        raise RuntimeError('No matching startup log arrived within the approved window')


if __name__ == '__main__':
    main()
