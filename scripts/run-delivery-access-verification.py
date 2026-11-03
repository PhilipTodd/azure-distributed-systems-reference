"""Real developer-profile and runtime registry verification with bounded cleanup.

Reuses the closed-host coordinator and its temporary content/repository journal.
No GitHub credentials or deployment identity credentials are used. The developer
profile is assigned directly to a disposable MI; this does not prove group login.
"""
import argparse
import importlib.util
import json
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('probe', ROOT / 'scripts/run-workload-access-verification.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


def prepare(mode):
    # Compile before any temporary Azure/SQL change.
    print(probe.command(['dotnet', 'publish', str(probe.PROBE / 'Stage1.AccessProbe.csproj'), '-c', 'Release', '-o', str(probe.RUNTIME / 'publish'), '--no-restore']), flush=True)
    probe.prepare('certificate' if mode == 'certificate' else 'data')
    state = probe.load()
    state['deliveryMode'] = mode
    state['settings']['Mode'] = mode
    if mode == 'certificate':
        certificates = json.loads((ROOT / 'docs/infrastructure/evidence/obo-certificates-2026-11-03.json').read_text(encoding='utf-8'))
        if not certificates.get('credentialReadBackVerified'):
            raise RuntimeError('Verify registered public certificates before runtime loading test')
        state['settings'].update({'CertificateSecretUri': certificates['development']['secretId'], 'CertificateThumbprint': certificates['development']['thumbprint']})
    probe.save(state)
    if mode == 'developer':
        name = 'id-adt-pp-devcheck-' + state['runId']
        identity_id = f'/subscriptions/{probe.SUB}/resourceGroups/{probe.RG}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{name}'
        original = probe.rest('get', probe.app_id('aquarium') + '?api-version=2024-11-01')['identity']
        state['developerProbe'] = {'identityId': identity_id, 'name': name, 'originalIdentity': original, 'sqlUser': '__Stage3Developer_' + state['runId'], 'roleAssignmentIds': [], 'cosmosAssignmentIds': []}
        probe.save(state)
        identity = probe.az('identity', 'create', '-g', probe.RG, '-n', name, '-l', 'australiaeast')
        state['developerProbe'].update({'principalId': identity['principalId'], 'clientId': identity['clientId']})
        state['settings'].update({'CredentialClientId': identity['clientId'], 'ExpectedPrincipalId': identity['principalId']})
        probe.save(state)
        scopes = [(f'/subscriptions/{probe.SUB}/resourceGroups/{probe.RG}', 'acdd72a7-3385-48ef-bd42-f606fba81ae7')]
        scopes += [(f'/subscriptions/{probe.SUB}/resourceGroups/{probe.RG}/providers/Microsoft.AppConfiguration/configurationStores/appcs-adt-{service}-dev', '516239f1-63e1-4d78-a4de-a74fb236a071') for service in ['aquarium', 'tracking']]
        for scope, role in scopes:
            assignment = scope + '/providers/Microsoft.Authorization/roleAssignments/' + str(uuid.uuid4())
            state['developerProbe']['roleAssignmentIds'].append(assignment)
            probe.save(state)
            probe.az('role', 'assignment', 'create', '--name', assignment.rsplit('/', 1)[-1], '--assignee-object-id', identity['principalId'], '--assignee-principal-type', 'ServicePrincipal', '--role', role, '--scope', scope)
        definitions = probe.az('cosmosdb', 'sql', 'role', 'definition', 'list', '-g', 'rg-platform-dev', '-a', 'cosmos-adt-platform-dev')
        role = next(item for item in definitions if item['roleName'] == 'Parameter Pilot Developer Reader')
        account = f'/subscriptions/{probe.SUB}/resourceGroups/rg-platform-dev/providers/Microsoft.DocumentDB/databaseAccounts/cosmos-adt-platform-dev'
        assignment = str(uuid.uuid4())
        state['developerProbe']['cosmosAssignmentIds'].append(assignment)
        probe.save(state)
        probe.az('cosmosdb', 'sql', 'role', 'assignment', 'create', '-g', 'rg-platform-dev', '-a', 'cosmos-adt-platform-dev', '--role-assignment-id', assignment, '--role-definition-id', role['id'], '--principal-id', identity['principalId'], '--scope', account + '/dbs/ReferenceProjects/colls/parameterpilot-tracking')
        with probe.sql_connect() as connection:
            cur = connection.cursor()
            sid = uuid.UUID(identity['clientId']).bytes_le.hex()
            user = state['developerProbe']['sqlUser']
            cur.execute(f'CREATE USER [{user}] WITH SID=0x{sid}, TYPE=E; GRANT CONNECT TO [{user}]; ALTER ROLE [AquariumDeveloper] ADD MEMBER [{user}];')
            cur.execute('INSERT INTO ' + state['settings']['SqlTable'] + ' VALUES(1,42); GRANT SELECT ON OBJECT::' + state['settings']['SqlTable'] + ' TO [AquariumDeveloper];')
        assigned = dict(original.get('userAssignedIdentities') or {})
        assigned[identity_id] = {}
        probe.rest('patch', probe.app_id('aquarium') + '?api-version=2024-11-01', {'identity': {'type': 'SystemAssigned, UserAssigned', 'userAssignedIdentities': assigned}})
    (probe.RUNTIME / 'publish/probe-settings.json').write_text(json.dumps(state['settings']), encoding='utf-8')
    probe.save(state)


def cleanup():
    state = probe.load()
    developer = state.get('developerProbe')
    # Restore hosts first even if a probe failed, then undo the identity profile.
    for service, snapshot in state['apps'].items():
        if not snapshot.get('restored'):
            probe.restore_host(service, state)
    if developer and not developer.get('cleaned'):
        original = developer['originalIdentity']
        assigned = {key: {} for key in (original.get('userAssignedIdentities') or {})}
        assigned[developer['identityId']] = None
        probe.rest('patch', probe.app_id('aquarium') + '?api-version=2024-11-01', {'identity': {'type': original['type'], 'userAssignedIdentities': assigned}})
        with probe.sql_connect() as connection:
            user = developer['sqlUser']
            connection.cursor().execute(f"IF DATABASE_PRINCIPAL_ID(N'{user}') IS NOT NULL DROP USER [{user}];")
        for assignment in list(developer['roleAssignmentIds']):
            probe.rest('delete', assignment + '?api-version=2022-04-01')
            developer['roleAssignmentIds'].remove(assignment)
            probe.save(state)
        for assignment in list(developer['cosmosAssignmentIds']):
            probe.quiet('cosmosdb', 'sql', 'role', 'assignment', 'delete', '-g', 'rg-platform-dev', '-a', 'cosmos-adt-platform-dev', '--role-assignment-id', assignment, '--yes')
            developer['cosmosAssignmentIds'].remove(assignment)
            probe.save(state)
        probe.quiet('identity', 'delete', '--ids', developer['identityId'])
        developer['cleaned'] = True
        probe.save(state)
    probe.cleanup()
    state = probe.load()
    identity = probe.rest('get', probe.app_id('aquarium') + '?api-version=2024-11-01')['identity']
    if developer:
        assert identity['type'] == developer['originalIdentity']['type']
        assert set(identity.get('userAssignedIdentities') or {}) == set(developer['originalIdentity'].get('userAssignedIdentities') or {})
        state['developerIdentityRestored'] = True
        probe.save(state)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['developer', 'registry', 'certificate'], default='developer')
    parser.add_argument('--phase', choices=['all', 'prepare', 'publish', 'run', 'cleanup'], default='all')
    args = parser.parse_args()
    if args.phase == 'cleanup':
        cleanup()
        return
    if args.phase == 'all':
        try:
            prepare(args.mode)
            probe.publish()
            for service in (['aquarium'] if args.mode == 'developer' else ['tracking'] if args.mode == 'certificate' else ['aquarium', 'tracking']):
                probe.run_service(service)
        finally:
            if probe.JOURNAL.exists():
                cleanup()
        state = probe.load()
        passed = bool(state['results']) and all(result['Passed'] for result in state['results'].values())
        evidence = {'date': '2026-11-03', 'runId': state['runId'], 'mode': args.mode, 'passed': passed, 'image': state.get('image'), 'results': state['results'], 'cleaned': state['cleaned'], 'sqlProbesAndTemporaryGrantsRemoved': state.get('sqlProbesAndTemporaryGrantsRemoved'), 'temporaryDeveloperIdentityRemoved': state.get('developerProbe', {}).get('cleaned'), 'developerIdentityRestored': state.get('developerIdentityRestored'), 'issuedTemporaryRegistryAssignmentIds': state.get('issuedRoleAssignmentIds'), 'registryConditionAssignmentsRestored': state.get('restoredRoleAssignments'), 'limitation': 'Developer profile tested through a directly assigned temporary MI, not Entra group login. Registry checks validate issued repository token actions, not a product image deployment. GitHub OIDC execution remains step 7.'}
        if args.mode == 'certificate':
            evidence['sqlOperationsPerformed'] = False
            evidence['limitation'] = 'Actual Tracking identity loaded/signed with Development certificate; not a customer-token OBO exchange.'
        filename = 'obo-runtime-certificate-verification-2026-11-03.json' if args.mode == 'certificate' else f'delivery-{args.mode}-verification-2026-11-03.json'
        (ROOT / 'docs/infrastructure/evidence' / filename).write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')
        if not passed:
            raise RuntimeError('One or more effective access checks failed; see evidence')
    elif args.phase == 'prepare':
        prepare(args.mode)
    elif args.phase == 'publish':
        probe.publish()
    else:
        for service in (['aquarium'] if probe.load()['deliveryMode'] == 'developer' else ['tracking'] if probe.load()['deliveryMode'] == 'certificate' else ['aquarium', 'tracking']):
            probe.run_service(service)


if __name__ == '__main__':
    main()
