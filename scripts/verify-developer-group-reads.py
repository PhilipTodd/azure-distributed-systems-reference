"""Read-only group data-access checks using owner Entra tokens.

Owner's management/SQL admin privileges make this unsuitable for proving general
developer isolation. Cosmos and App Configuration reads exercise the group data
grants where ARM Owner alone does not grant data read. No token/value is logged.
"""
import base64
import importlib.util
import json
import urllib.error
import urllib.parse
import urllib.request
import uuid
from email.utils import formatdate
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('delivery', ROOT / 'scripts/bootstrap-delivery-access.py')
delivery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delivery)


def request(resource, url, headers=None, body=None):
    token = delivery.az('account', 'get-access-token', '--resource', resource)['accessToken']
    payload = token.split('.')[1]
    claims = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))
    state = json.loads(delivery.EVIDENCE.read_text(encoding='utf-8'))
    group_claim = state['developerGroup']['objectId'] in claims.get('groups', [])
    auth = urllib.parse.quote('type=aad&ver=1.0&sig=' + token, safe='') if resource == 'https://cosmos.azure.com/' else 'Bearer ' + token
    actual_headers = {'Authorization': auth, **(headers or {})}
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=actual_headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            # Do not return configuration or document contents.
            return response.status, group_claim
    except urllib.error.HTTPError as error:
        return error.code, group_claim


def main():
    delivery.require_account()
    marker = 'stage3-' + uuid.uuid4().hex[:12]
    checks = {}
    claims = {}
    for service in ['aquarium', 'tracking']:
        status, group = request('https://azconfig.io', f'https://appcs-adt-{service}-dev.azconfig.io/kv?key=Stage1%3AStep3%3A{marker}*&api-version=1.0')
        checks['groupConfigurationRead:' + service] = status == 200
        claims['configuration:' + service] = group
    base = 'https://cosmos-adt-platform-dev.documents.azure.com/dbs/ReferenceProjects/colls/parameterpilot-tracking/docs'
    headers = {'x-ms-date': formatdate(usegmt=True), 'x-ms-version': '2018-12-31', 'x-ms-documentdb-partitionkey': json.dumps([marker])}
    status, group = request('https://cosmos.azure.com/', base + '/' + marker, headers)
    checks['groupCosmosAuthorisedMissingItemRead'] = status == 404
    claims['cosmos'] = group
    headers.update({'Content-Type': 'application/query+json', 'x-ms-documentdb-isquery': 'true'})
    status, _ = request('https://cosmos.azure.com/', base, headers, {'query': 'SELECT * FROM c WHERE c.id=@id', 'parameters': [{'name': '@id', 'value': marker}]})
    checks['groupCosmosQuery'] = status == 200
    result = {'date': '2026-11-03', 'passed': all(checks.values()), 'checks': checks, 'developerGroupPresentInTokenClaims': claims, 'limitation': 'Read-only data grant checks under the owner. Not evidence of restricted SQL/ARM access or general ordinary-user isolation.'}
    (ROOT / 'docs/infrastructure/evidence/developer-group-reads-2026-11-03.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    if not result['passed']:
        raise RuntimeError('One or more actual group data reads failed')


if __name__ == '__main__':
    main()
