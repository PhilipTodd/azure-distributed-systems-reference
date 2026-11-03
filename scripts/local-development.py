"""Loopback-only PP Local dependencies. No Azure login, URL or data access.

up/check/down operate on pp-local and preserve its data. verify-clean uses a
new isolated project and removes only its own newly created test volumes.
"""
import argparse
import csv
from datetime import datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import re
import secrets
import socket
import ssl
import subprocess
import time
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[1]
LOCAL = ROOT / 'local'
PROJECT = ROOT / 'tests/Stage1.LocalProbe/Stage1.LocalProbe.csproj'
RUN_DATE = datetime.now().astimezone().date().isoformat()
EVIDENCE = ROOT / 'docs/infrastructure/evidence' / f'local-bootstrap-verification-{RUN_DATE}.json'


def command(args, env=None):
    result = subprocess.run(args, env=env, text=True, capture_output=True, timeout=600)
    if result.returncode:
        if args[:2] == ['docker', 'compose'] and 'up' in args:
            error = result.stderr.lower()
            if any(message in error for message in ('address already in use', 'port is already allocated', 'only one usage of each socket address')):
                raise RuntimeError("A Local port is already in use. If SQL port 1433 is occupied, set PP_SQL_PORT to a free port such as 15433 and rerun up. See local/README.md.")
        # No secret is passed as an argument. Do not echo database/SDK error bodies.
        raise RuntimeError('Local command failed: ' + ' '.join(args[:4]) + ' (exit ' + str(result.returncode) + ')')
    return result.stdout


def protect_directory(path):
    path.mkdir(parents=True, exist_ok=True)
    if os.name == 'nt':
        row = next(csv.reader(io.StringIO(command(['whoami', '/user', '/fo', 'csv', '/nh']))))
        command(['icacls', str(path), '/inheritance:r', '/grant:r', '*' + row[1] + ':(OI)(CI)F'])
    else:
        path.chmod(0o700)


def environment(project='pp-local', fresh=False):
    if project != 'pp-local' and not re.fullmatch(r'pp-local-check-[a-f0-9]{12}', project):
        raise ValueError('Only the dedicated PP Local project names are permitted')
    runtime = LOCAL / '.runtime' / project
    protect_directory(runtime)
    password = runtime / 'sql-password'
    if not password.exists():
        password.write_text('PpLocal!' + secrets.token_hex(24), encoding='utf-8')
        if os.name != 'nt': password.chmod(0o600)
    env = os.environ.copy()
    sql_port = '25433' if fresh else env.get('PP_SQL_PORT', '1433')
    if not re.fullmatch(r'[0-9]{1,5}', sql_port) or not 1024 <= int(sql_port) <= 65535:
        raise ValueError('PP_SQL_PORT must be a port from 1024 to 65535')
    env.update({'PP_LOCAL_RUNTIME': str(runtime), 'PP_SQL_PORT': sql_port, 'PP_COSMOS_PORT': '28081' if fresh else '8081', 'PP_COSMOS_HEALTH_PORT': '28080' if fresh else '18080', 'PP_COSMOS_EXPLORER_PORT': '21234' if fresh else '11234'})
    return env


def compose(project, env, *args):
    return command(['docker', 'compose', '--project-name', project, '--file', str(LOCAL / 'compose.yaml'), *args], env)


def validate_config(config):
    if set(config['services']) != {'sql', 'cosmos'}: raise ValueError('Unexpected dependency')
    for service in config['services'].values():
        if not re.search(r'@sha256:[a-f0-9]{64}$', service['image']): raise ValueError('Image must be digest-pinned')
        for port in service.get('ports', []):
            if port.get('host_ip') != '127.0.0.1': raise ValueError('Only loopback-published ports are allowed')
        if service.get('privileged') or service.get('network_mode') == 'host': raise ValueError('Unsafe container networking')
    if 'MSSQL_SA_PASSWORD' in config['services']['sql'].get('environment', {}): raise ValueError('Use the private secret file, not Compose environment values')


def up(project, env):
    baseline = json.loads((LOCAL / 'baseline.json').read_text())
    if baseline['status'] != 'owner-approved':
        raise RuntimeError('Cosmos replacement awaits owner approval; see local/baseline.json')
    config = json.loads(compose(project, env, 'config', '--format', 'json'))
    validate_config(config)
    compose(project, env, 'up', '--detach', '--wait', '--wait-timeout', '360')
    # Explicit HTTP readiness on loopback; this is not the Cosmos data endpoint.
    for attempt in range(60):
        try:
            with urllib.request.urlopen('http://127.0.0.1:' + env['PP_COSMOS_HEALTH_PORT'] + '/ready', timeout=5) as response:
                if response.status == 200: break
        except (OSError, TimeoutError): pass
        time.sleep(5)
    else: raise RuntimeError('Local Cosmos readiness timed out')
    # Pin this emulator instance's public certificate; no global trust-store change.
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # Bootstrap only, fixed loopback socket; never used for SDK calls.
    with socket.create_connection(('127.0.0.1', int(env['PP_COSMOS_PORT'])), timeout=10) as sock:
        with context.wrap_socket(sock, server_hostname='localhost') as secured:
            certificate = secured.getpeercert(binary_form=True)
    runtime = Path(env['PP_LOCAL_RUNTIME'])
    (runtime / 'cosmos-cert-sha256').write_text(hashlib.sha256(certificate).hexdigest().upper())
    (runtime / 'probe.json').write_text(json.dumps({'SqlPort': int(env['PP_SQL_PORT']), 'CosmosPort': int(env['PP_COSMOS_PORT']), 'FixturePath': str(LOCAL / 'synthetic-fixtures.json')}))
    # Verify the effective engine bindings, not just the Compose declaration.
    ids = compose(project, env, 'ps', '--quiet').split()
    assert len(ids) == 2
    actual = json.loads(command(['docker', 'inspect', *ids]))
    for container in actual:
        for bindings in container['NetworkSettings']['Ports'].values():
            for binding in bindings or []:
                if binding['HostIp'] != '127.0.0.1': raise RuntimeError('Effective port binding escaped loopback')
    print('Local SQL and Cosmos ready; all published ports verified loopback-only.', flush=True)
    return {'images': {name: service['image'] for name, service in config['services'].items()}, 'loopbackBindingsVerified': True}


def check(env):
    command(['dotnet', 'restore', str(PROJECT), '--locked-mode'], env)
    # SDK failures are reported by safe check names; never expose connection strings.
    command(['dotnet', 'run', '--project', str(PROJECT), '--no-restore'], env)
    result = json.loads((Path(env['PP_LOCAL_RUNTIME']) / 'result.json').read_text())
    print(json.dumps(result), flush=True)
    return result


def verify_clean():
    project = 'pp-local-check-' + uuid.uuid4().hex[:12]
    env = environment(project, fresh=True)
    evidence = {'date': RUN_DATE, 'project': project, 'startedUtc': datetime.now(timezone.utc).isoformat(), 'passed': False}
    try:
        evidence.update(up(project, env))
        evidence['firstRun'] = check(env)
        # Recreate the processes, keep only this run's volumes, repeat all checks.
        compose(project, env, 'down')
        up(project, env)
        evidence['afterRestart'] = check(env)
        evidence['passed'] = evidence['firstRun']['passed'] and evidence['afterRestart']['passed']
    except Exception as error:
        evidence['failure'] = type(error).__name__ + ': ' + str(error)
        raise
    finally:
        # The generated project was created by this invocation; never target pp-local here.
        assert re.fullmatch(r'pp-local-check-[a-f0-9]{12}', project)
        compose(project, env, 'down', '--volumes', '--remove-orphans')
        remaining = command(['docker', 'volume', 'ls', '--filter', 'label=com.docker.compose.project=' + project, '--format', '{{.Name}}']).strip()
        evidence['temporaryVolumesRemoved'] = not remaining
        if not remaining:
            (Path(env['PP_LOCAL_RUNTIME']) / 'sql-password').unlink(missing_ok=True)
        evidence['azureOperationsPerformed'] = False
        evidence['tools'] = {'docker': command(['docker', 'version', '--format', '{{.Server.Version}}']).strip(), 'compose': command(['docker', 'compose', 'version', '--short']).strip(), 'dotnet': command(['dotnet', '--version']).strip()}
        EVIDENCE.write_text(json.dumps(evidence, indent=2) + '\n')
        print('Isolated Local verification cleaned up; ordinary pp-local data untouched.', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['up', 'check', 'down', 'verify-clean'])
    args = parser.parse_args()
    if args.action == 'verify-clean': verify_clean()
    else:
        env = environment()
        if args.action == 'up': up('pp-local', env)
        elif args.action == 'check': check(env)
        else:
            compose('pp-local', env, 'down')
            print('PP Local containers stopped; data volumes preserved.')
