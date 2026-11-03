"""Step 4 customer registrations and email-passcode flow in the EXTERNAL tenant.

Default only validates/prints the local plan. --apply requires a separately
verified customer tenant ID and an authenticated owner session in that tenant.
No token, private key or secret is printed/saved. Certificates are separate.
"""
import argparse
import importlib.util
import json
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'infra/bicep/environments/dev/customer-identity.json'
EVIDENCE = ROOT / 'docs/infrastructure/evidence/customer-registrations-2026-11-03.json'
spec = importlib.util.spec_from_file_location('delivery', ROOT / 'scripts/bootstrap-delivery-access.py')
delivery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delivery)


def validate(plan):
    if plan['environment'] != 'dev' or plan['tenantSubdomain'] != 'parameterpilotdev':
        raise ValueError('Unexpected environment/tenant')
    if set(plan['applications']) != {'ui', 'aquarium', 'tracking'}:
        raise ValueError('Only three approved customer applications')
    if plan['applications']['aquarium']['scopes'] != ['Aquarium.Read', 'Aquarium.Write'] or plan['applications']['tracking']['scopes'] != ['Tracking.Read', 'Tracking.Write']:
        raise ValueError('Exact approved per-service delegated scopes required')
    if set(plan['spaRedirectUris']) != {'http://localhost:4200', 'https://parameterpilot.com', 'https://www.parameterpilot.com'}:
        raise ValueError('Only reviewed explicit Local/Development redirects')
    if plan['trackingDownstreamScope'] != 'Aquarium.Read' or plan['customerSignIn'] != 'EmailOTP':
        raise ValueError('Unapproved delegation/sign-in method')


class Graph:
    def __init__(self, tenant):
        self.tenant = str(uuid.UUID(tenant))
        if self.tenant == delivery.TENANT:
            raise ValueError('Refusing customer setup in the workforce tenant')
        self.token = delivery.az('account', 'get-access-token', '--tenant', self.tenant, '--resource', 'https://graph.microsoft.com/')['accessToken']
        orgs = self.call('GET', '/organization?$select=id,displayName,tenantType,verifiedDomains')['value']
        if len(orgs) != 1 or orgs[0]['id'] != self.tenant or orgs[0]['tenantType'] != 'CIAM':
            raise RuntimeError('Authenticated directory is not the expected External ID tenant')
        if not any(item['name'] == 'parameterpilotdev.onmicrosoft.com' for item in orgs[0]['verifiedDomains']):
            raise RuntimeError('Unexpected customer domain')

    def call(self, method, path, body=None):
        if not path.startswith('/') or path.startswith('//'):
            raise ValueError('Graph-relative path required')
        req = urllib.request.Request('https://graph.microsoft.com/v1.0' + path, method=method,
            data=json.dumps(body).encode() if body is not None else None,
            headers={'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except urllib.error.HTTPError as error:
            # Only Graph's error code/message, never request bodies or tokens.
            try:
                details = json.loads(error.read()).get('error', {})
                detail = str(details.get('code', '')) + ': ' + str(details.get('message', ''))[:700]
            except (ValueError, AttributeError):
                detail = 'Details unavailable'
            raise RuntimeError('Graph ' + method + ' ' + path.split('?')[0] + ' returned ' + str(error.code) + ' ' + detail) from None


def scope_id(tenant, service, name):
    return str(uuid.uuid5(uuid.UUID(tenant), 'parameterpilot-dev:' + service + ':' + name))


def save(state):
    EVIDENCE.write_text(json.dumps(state, indent=2) + '\n', encoding='utf-8')


def contains(actual, expected):
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(key in actual and contains(actual[key], value) for key, value in expected.items())
    if isinstance(expected, list):
        return isinstance(actual, list) and len(actual) == len(expected) and all(any(contains(item, required) for item in actual) for required in expected)
    return actual == expected


def applications(graph, plan):
    state = json.loads(EVIDENCE.read_text(encoding='utf-8')) if EVIDENCE.exists() else {'date': '2026-11-03', 'tenantId': graph.tenant, 'applications': {}}
    if state['tenantId'] != graph.tenant:
        raise RuntimeError('Existing evidence names a different tenant')
    for service, desired in plan['applications'].items():
        query = urllib.parse.urlencode({'$filter': "displayName eq '" + desired['displayName'] + "'"})
        found = graph.call('GET', '/applications?' + query)['value']
        if len(found) > 1:
            raise RuntimeError('Ambiguous customer application name')
        if found and service not in state['applications']:
            raise RuntimeError('Unrecorded existing application needs explicit reconciliation')
        app = found[0] if found else graph.call('POST', '/applications', {'displayName': desired['displayName'], 'signInAudience': 'AzureADMyOrg'})
        if app.get('passwordCredentials'):
            raise RuntimeError('Customer registration has unexpected client secrets')
        previous = state['applications'].get(service, {})
        if previous and previous['objectId'] != app['id']:
            raise RuntimeError('Recorded application changed')
        previous.update({'objectId': app['id'], 'clientId': app['appId'], 'displayName': desired['displayName']})
        state['applications'][service] = previous
        save(state)
        found_sp = graph.call('GET', '/servicePrincipals?' + urllib.parse.urlencode({'$filter': "appId eq '" + app['appId'] + "'"}))['value']
        if len(found_sp) > 1:
            raise RuntimeError('Ambiguous customer service principal')
        sp = found_sp[0] if found_sp else graph.call('POST', '/servicePrincipals', {'appId': app['appId']})
        previous['principalId'] = sp['id']
        save(state)
    ui = state['applications']['ui']
    graph.call('PATCH', '/applications/' + ui['objectId'], {'spa': {'redirectUris': plan['spaRedirectUris']}, 'isFallbackPublicClient': False, 'web': {'implicitGrantSettings': {'enableAccessTokenIssuance': False, 'enableIdTokenIssuance': False}}})
    ui_permissions = []
    for service in ['aquarium', 'tracking']:
        app = state['applications'][service]
        scopes = [{'id': scope_id(graph.tenant, service, name), 'value': name, 'isEnabled': True, 'type': 'Admin', 'adminConsentDisplayName': name, 'adminConsentDescription': 'Delegated ' + name + ' operations; tank ownership is checked independently.'} for name in plan['applications'][service]['scopes']]
        preauthorised = [{'appId': ui['clientId'], 'delegatedPermissionIds': [item['id'] for item in scopes]}]
        if service == 'aquarium':
            preauthorised.append({'appId': state['applications']['tracking']['clientId'], 'delegatedPermissionIds': [scope_id(graph.tenant, 'aquarium', 'Aquarium.Read')]})
        # Graph validates preauthorised IDs against already persisted scopes,
        # not scopes introduced in the same request. Keep these writes ordered.
        graph.call('PATCH', '/applications/' + app['objectId'], {'identifierUris': ['api://' + app['clientId']], 'api': {'requestedAccessTokenVersion': 2, 'oauth2PermissionScopes': scopes}})
        graph.call('PATCH', '/applications/' + app['objectId'], {'api': {'preAuthorizedApplications': preauthorised}})
        app.update({'audience': app['clientId'], 'scopeUris': ['api://' + app['clientId'] + '/' + item['value'] for item in scopes]})
        ui_permissions.append({'resourceAppId': app['clientId'], 'resourceAccess': [{'id': item['id'], 'type': 'Scope'} for item in scopes]})
        save(state)
    graph.call('PATCH', '/applications/' + ui['objectId'], {'requiredResourceAccess': ui_permissions})
    tracking = state['applications']['tracking']
    aquarium = state['applications']['aquarium']
    graph.call('PATCH', '/applications/' + tracking['objectId'], {'requiredResourceAccess': [{'resourceAppId': aquarium['clientId'], 'resourceAccess': [{'id': scope_id(graph.tenant, 'aquarium', 'Aquarium.Read'), 'type': 'Scope'}]}]})
    # Explicit tenant admin consent for the approved customer delegated scopes.
    for client, resource, names in [(ui, aquarium, ['Aquarium.Read', 'Aquarium.Write']), (ui, tracking, ['Tracking.Read', 'Tracking.Write']), (tracking, aquarium, ['Aquarium.Read'])]:
        query = urllib.parse.urlencode({'$filter': "clientId eq '" + client['principalId'] + "' and resourceId eq '" + resource['principalId'] + "'"})
        grants = graph.call('GET', '/oauth2PermissionGrants?' + query)['value']
        if grants:
            if len(grants) != 1 or grants[0]['consentType'] != 'AllPrincipals' or set(grants[0]['scope'].split()) != set(names):
                raise RuntimeError('Existing consent differs from the reviewed scopes')
        else:
            graph.call('POST', '/oauth2PermissionGrants', {'clientId': client['principalId'], 'resourceId': resource['principalId'], 'consentType': 'AllPrincipals', 'scope': ' '.join(names)})
    for service, app in state['applications'].items():
        actual = graph.call('GET', '/applications/' + app['objectId'])
        if actual['appId'] != app['clientId'] or actual['signInAudience'] != 'AzureADMyOrg' or actual.get('passwordCredentials'):
            raise RuntimeError('Application identity/audience/secret read-back mismatch')
        if service == 'ui':
            if set(actual['spa']['redirectUris']) != set(plan['spaRedirectUris']) or not contains(actual['requiredResourceAccess'], ui_permissions):
                raise RuntimeError('SPA redirect/permission read-back mismatch')
            implicit = actual['web']['implicitGrantSettings']
            if implicit['enableAccessTokenIssuance'] or implicit['enableIdTokenIssuance']:
                raise RuntimeError('Implicit flow must remain disabled')
        else:
            expected_scopes = {name: scope_id(graph.tenant, service, name) for name in plan['applications'][service]['scopes']}
            actual_scopes = {item['value']: item['id'] for item in actual['api']['oauth2PermissionScopes'] if item['isEnabled']}
            if actual['api']['requestedAccessTokenVersion'] != 2 or actual_scopes != expected_scopes or actual['identifierUris'] != ['api://' + app['clientId']]:
                raise RuntimeError('API token version/scope/audience read-back mismatch')
    state.update({'authority': 'https://parameterpilotdev.ciamlogin.com/' + graph.tenant, 'spaRedirectUris': plan['spaRedirectUris'], 'registrationsAndConsentConfigured': True, 'registrationReadBackVerified': True, 'certificateConfigured': state.get('certificateConfigured', False), 'interactiveSignInAndOboVerified': state.get('interactiveSignInAndOboVerified', False)})
    save(state)
    return state


def user_flow(graph, plan):
    state = json.loads(EVIDENCE.read_text(encoding='utf-8'))
    if state['tenantId'] != graph.tenant or not state.get('registrationsAndConsentConfigured'):
        raise RuntimeError('Configure/verify registrations first')
    providers = graph.call('GET', '/identity/identityProviders')['value']
    otp = [item for item in providers if item.get('identityProviderType') == 'EmailOTP']
    if len(otp) != 1:
        raise RuntimeError('Cannot unambiguously resolve the email-passcode provider')
    existing = graph.call('GET', '/identity/authenticationEventsFlows')['value']
    body = {'@odata.type': '#microsoft.graph.externalUsersSelfServiceSignUpEventsFlow', 'displayName': plan['userFlowName'], 'conditions': {'applications': {'includeApplications': [{'appId': state['applications']['ui']['clientId']}]}}, 'onAuthenticationMethodLoadStart': {'@odata.type': '#microsoft.graph.onAuthenticationMethodLoadStartExternalUsersSelfServiceSignUp', 'identityProviders': [{'id': otp[0]['id']}]}, 'onInteractiveAuthFlowStart': {'@odata.type': '#microsoft.graph.onInteractiveAuthFlowStartExternalUsersSelfServiceSignUp', 'isSignUpAllowed': True}}
    matching = [item for item in existing if item.get('displayName') == plan['userFlowName']]
    if matching:
        if len(matching) != 1 or matching[0]['id'] != state.get('userFlow', {}).get('id'):
            raise RuntimeError('Existing unrecorded user flow needs explicit reconciliation')
        flow = matching[0]
    else:
        flow = graph.call('POST', '/identity/authenticationEventsFlows', body)
    state['userFlow'] = {'id': flow['id'], 'displayName': plan['userFlowName'], 'identityProviderId': otp[0]['id']}
    save(state)
    actual = graph.call('GET', '/identity/authenticationEventsFlows/' + flow['id'])
    if not contains(actual, body):
        raise RuntimeError('User flow read-back differs from the approved email-only configuration')
    state['userFlow']['readBackVerified'] = True
    save(state)
    return state['userFlow']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tenant')
    parser.add_argument('--phase', choices=['applications', 'user-flow'], default='applications')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    plan = json.loads(MANIFEST.read_text(encoding='utf-8'))
    validate(plan)
    if not args.apply:
        print(json.dumps({'apply': False, 'plan': plan}, indent=2))
        return
    if not args.tenant:
        parser.error('A verified External ID tenant ID is required')
    graph = Graph(args.tenant)
    result = applications(graph, plan) if args.phase == 'applications' else user_flow(graph, plan)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
