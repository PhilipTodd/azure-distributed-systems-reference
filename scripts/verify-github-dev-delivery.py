"""Protected Development delivery probes. Run only from the reviewed workflows."""
import argparse
import json
import os
import re
import struct
import subprocess

SUBSCRIPTION = '9671ac36-9800-451a-b283-35ea87f8b419'
REGISTRY = 'acradtplatformdev'
IMAGE = REGISTRY + '.azurecr.io/parameterpilot/aquarium-api'
SITE = (
    'https://management.azure.com/subscriptions/' + SUBSCRIPTION
    + '/resourceGroups/rg-parameterpilot-dev/providers/Microsoft.Web/sites/api-adt-aquarium-dev'
)


def command(*args, stdin=None):
    result = subprocess.run(args, input=stdin, text=True, capture_output=True, timeout=180)
    if result.returncode:
        raise RuntimeError(f'{args[0]} {args[1]} failed with exit code {result.returncode}')
    return result.stdout.strip()


def arm(method, path='', body=None):
    args = ['az', 'rest', '--method', method, '--url', SITE + path + '?api-version=2024-11-01']
    if body is not None:
        args += ['--body', json.dumps(body)]
    return json.loads(command(*args))


def release():
    site = arm('get')['properties']
    if site['enabled'] or site.get('publicNetworkAccess') != 'Disabled':
        raise RuntimeError('Verification requires the disabled Aquarium host with public access disabled')
    config = arm('get', '/config/web')['properties']
    original = config.get('linuxFxVersion') or ''
    if original or config.get('ipSecurityRestrictionsDefaultAction') != 'Deny':
        raise RuntimeError('Aquarium host differs from the reviewed closed bootstrap configuration')
    tag = 'stage1-' + os.environ['GITHUB_RUN_ID'] + '-' + os.environ['GITHUB_RUN_ATTEMPT']
    if not re.fullmatch(r'stage1-[0-9]+-[0-9]+', tag):
        raise ValueError('Unexpected verification tag')
    token = command('az', 'acr', 'login', '-n', REGISTRY, '--expose-token', '--query', 'accessToken', '-o', 'tsv')
    try:
        command('docker', 'login', REGISTRY + '.azurecr.io', '--username',
                '00000000-0000-0000-0000-000000000000', '--password-stdin', stdin=token)
        push = command('docker', 'push', IMAGE + ':' + tag)
    finally:
        command('docker', 'logout', REGISTRY + '.azurecr.io')
    match = re.search(r'digest: (sha256:[0-9a-f]{64})', push)
    if not match:
        raise RuntimeError('Published digest could not be determined')
    version = 'DOCKER|' + IMAGE + '@' + match[1]
    try:
        arm('patch', '/config/web', {'properties': {'linuxFxVersion': version}})
        if arm('get', '/config/web')['properties']['linuxFxVersion'] != version:
            raise RuntimeError('Container configuration readback differs from the published digest')
    finally:
        arm('patch', '/config/web', {'properties': {'linuxFxVersion': original}})
        if (arm('get', '/config/web')['properties'].get('linuxFxVersion') or '') != original:
            raise RuntimeError('Owner intervention required to restore the Aquarium image configuration')
    print(f'Image published and closed-host configuration verified and restored. Digest {match[1]}')


def migration():
    import pyodbc

    token = command('az', 'account', 'get-access-token', '--resource',
                    'https://database.windows.net/', '--query', 'accessToken', '-o', 'tsv').encode('utf-16-le')
    connection = pyodbc.connect(
        'Driver={ODBC Driver 18 for SQL Server};Server=tcp:sql-adt-platform-dev.database.windows.net,1433;'
        'Database=ReferenceProjectsDb;Encrypt=yes;TrustServerCertificate=no;',
        attrs_before={1256: struct.pack('<I', len(token)) + token}, timeout=20, autocommit=False,
    )
    try:
        cursor = connection.cursor()
        if cursor.execute("SELECT IS_ROLEMEMBER('AquariumMigrations')").fetchone()[0] != 1:
            raise RuntimeError('Expected AquariumMigrations role membership')
        cursor.execute('CREATE TABLE Aquarium.Stage1GitHubMigrationProbe (Id int NOT NULL PRIMARY KEY)')
        if cursor.execute("SELECT OBJECT_ID(N'Aquarium.Stage1GitHubMigrationProbe', N'U')").fetchone()[0] is None:
            raise RuntimeError('Verification table could not be read back')
    finally:
        try:
            connection.rollback()
        finally:
            connection.close()
    print('Aquarium migration DDL verified under the GitHub identity and rolled back')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=['release', 'migration'])
    args = parser.parse_args()
    expected = {
        'release': '1680b16a-c50a-4691-8c84-e681cfb18813',
        'migration': '83029544-189c-4630-9b9b-d4a23fb3312b',
    }[args.mode]
    account = json.loads(command('az', 'account', 'show'))
    if account['id'] != SUBSCRIPTION or account['user']['name'] != expected:
        raise SystemExit('Unexpected Azure subscription or GitHub service principal')
    {'release': release, 'migration': migration}[args.mode]()
