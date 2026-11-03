"""Create/register separate Tracking OBO certificates; private keys never logged.

Development key is generated inside the existing Tracking vault. Local key is
non-exportable in the current Windows user's certificate store. --apply required.
"""
import argparse
import base64
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import time
import uuid

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('customer', ROOT / 'scripts/bootstrap-customer-identity.py')
customer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(customer)
delivery = customer.delivery
EVIDENCE = ROOT / 'docs/infrastructure/evidence/obo-certificates-2026-11-03.json'
VAULT = '/subscriptions/' + delivery.SUB + '/resourceGroups/rg-parameterpilot-dev/providers/Microsoft.KeyVault/vaults/kv-adt-tracking-dev'
NAME = 'tracking-obo-dev'


def save(state):
    EVIDENCE.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--cleanup', action='store_true')
    args = parser.parse_args()
    if not args.apply and not args.cleanup:
        print(json.dumps({'apply': False, 'developmentCertificate': 'kv-adt-tracking-dev/' + NAME, 'localCertificate': 'CurrentUser/My; RSA3072 non-exportable; 12-month validity; manual rotation'}, indent=2))
        return
    delivery.require_account()
    identities = json.loads(customer.EVIDENCE.read_text(encoding='utf-8'))
    state = json.loads(EVIDENCE.read_text(encoding='utf-8')) if EVIDENCE.exists() else {'date': '2026-11-03', 'tenantId': identities['tenantId'], 'temporaryAssignmentId': None, 'temporaryGrantRemoved': True}
    if state['tenantId'] != identities['tenantId']:
        raise RuntimeError('Certificate evidence tenant mismatch')

    def cleanup():
        if state.get('temporaryAssignmentId') and not state.get('temporaryGrantRemoved'):
            delivery.az('rest', '--method', 'DELETE', '--url', 'https://management.azure.com' + state['temporaryAssignmentId'] + '?api-version=2022-04-01')
            state['temporaryGrantRemoved'] = True
            save(state)
    if args.cleanup:
        cleanup()
        return
    graph = customer.Graph(identities['tenantId'])
    app = graph.call('GET', '/applications/' + identities['applications']['tracking']['objectId'] + '?$select=id,appId,keyCredentials,passwordCredentials')
    if app['appId'] != identities['applications']['tracking']['clientId'] or app.get('passwordCredentials'):
        raise RuntimeError('Unexpected Tracking identity or client secrets')
    if state.get('registeredPublicCertificates'):
        if not customer.contains(app['keyCredentials'], state['registeredPublicCertificates']):
            raise RuntimeError('Existing registered certificates differ from recorded setup')
        print(json.dumps({'certificateRegistrationAlreadyVerified': True, 'temporaryGrantRemoved': state['temporaryGrantRemoved']}))
        return
    try:
        if not state.get('development'):
            assignment = VAULT + '/providers/Microsoft.Authorization/roleAssignments/' + str(uuid.uuid4())
            state.update({'temporaryAssignmentId': assignment, 'temporaryGrantRemoved': False})
            save(state)
            props = {'principalId': delivery.OWNER, 'principalType': 'User', 'roleDefinitionId': '/subscriptions/' + delivery.SUB + '/providers/Microsoft.Authorization/roleDefinitions/a4417e6f-fecd-4de8-b567-7b0420556985', 'description': 'Temporary PP Step 4 certificate setup; remove after bootstrap'}
            delivery.body_call('rest', '--method', 'PUT', '--url', 'https://management.azure.com' + assignment + '?api-version=2022-04-01', body={'properties': props})
            with tempfile.TemporaryDirectory(prefix='pp-obo-policy-') as folder:
                policy = {'issuerParameters': {'name': 'Self'}, 'keyProperties': {'exportable': True, 'keyType': 'RSA', 'keySize': 3072, 'reuseKey': False}, 'secretProperties': {'contentType': 'application/x-pkcs12'}, 'x509CertificateProperties': {'subject': 'CN=Parameter Pilot Tracking OBO Development', 'keyUsage': ['digitalSignature'], 'validityInMonths': 12}}
                path = Path(folder) / 'policy.json'
                path.write_text(json.dumps(policy), encoding='utf-8')
                for attempt in range(18):
                    try:
                        current = delivery.az('keyvault', 'certificate', 'list', '--vault-name', 'kv-adt-tracking-dev', '--query', "[?ends_with(id, '/" + NAME + "')]")
                        if current:
                            # A previous interrupted create may have completed.
                            created = delivery.az('keyvault', 'certificate', 'show', '--vault-name', 'kv-adt-tracking-dev', '--name', NAME)
                        else:
                            delivery.az('keyvault', 'certificate', 'create', '--vault-name', 'kv-adt-tracking-dev', '--name', NAME, '--policy', '@' + str(path))
                            # Create returns an operation object, not a bundle.
                            created = delivery.az('keyvault', 'certificate', 'show', '--vault-name', 'kv-adt-tracking-dev', '--name', NAME)
                        break
                    except RuntimeError:
                        if attempt == 17:
                            raise
                        print('Waiting for temporary certificate setup permission propagation', flush=True)
                        time.sleep(10)
            def certificate_date(short_name, sdk_name):
                value = created['attributes'].get(short_name, created['attributes'].get(sdk_name))
                if isinstance(value, (int, float)):
                    return datetime.fromtimestamp(value, timezone.utc).isoformat()
                return datetime.fromisoformat(value.replace('Z', '+00:00')).isoformat()
            state['development'] = {'certificateId': created['id'], 'secretId': created['sid'], 'publicCertificate': created['cer'], 'notBefore': certificate_date('nbf', 'notBefore'), 'notAfter': certificate_date('exp', 'expires')}
            save(state)
        if not state.get('local'):
            process = subprocess.run(['powershell.exe', '-NoProfile', '-File', str(ROOT / 'scripts/create-local-obo-certificate.ps1'), '-Apply'], capture_output=True, text=True)
            if process.returncode:
                raise RuntimeError('Local non-exportable certificate setup failed; output suppressed')
            state['local'] = json.loads(process.stdout)
            save(state)
        keys = []
        for name, certificate in [('Development', state['development']), ('Local', state['local'])]:
            raw = base64.b64decode(certificate['publicCertificate'])
            thumb = hashlib.sha1(raw).digest()  # X.509 thumbprint identifier, not a signature algorithm.
            certificate['thumbprint'] = thumb.hex().upper()
            keys.append({'keyId': str(uuid.uuid5(uuid.UUID(identities['tenantId']), 'tracking-obo:' + certificate['thumbprint'])), 'type': 'AsymmetricX509Cert', 'usage': 'Verify', 'key': certificate['publicCertificate'], 'customKeyIdentifier': base64.b64encode(thumb).decode(), 'displayName': 'Parameter Pilot Tracking OBO ' + name, 'startDateTime': certificate['notBefore'], 'endDateTime': certificate['notAfter']})
        if app.get('keyCredentials') and not customer.contains(app['keyCredentials'], keys):
            raise RuntimeError('Existing unrecorded Tracking certificate credentials require reconciliation')
        graph.call('PATCH', '/applications/' + app['id'], {'keyCredentials': keys})
        expected = [{key: value for key, value in item.items() if key not in ['key', 'startDateTime', 'endDateTime']} for item in keys]
        actual = graph.call('GET', '/applications/' + app['id'] + '?$select=keyCredentials,passwordCredentials')
        if actual.get('passwordCredentials') or not customer.contains(actual['keyCredentials'], expected) or len(actual['keyCredentials']) != 2:
            raise RuntimeError('Certificate credential read-back verification failed')
        state['registeredPublicCertificates'] = expected
        state['credentialReadBackVerified'] = True
        save(state)
        identities['certificateConfigured'] = True
        customer.save(identities)
    finally:
        cleanup()
    print(json.dumps({'developmentThumbprint': state['development']['thumbprint'], 'localThumbprint': state['local']['thumbprint'], 'credentialReadBackVerified': state['credentialReadBackVerified'], 'temporaryGrantRemoved': state['temporaryGrantRemoved']}, indent=2))


if __name__ == '__main__':
    main()
