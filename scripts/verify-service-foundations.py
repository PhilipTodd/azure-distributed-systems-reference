"""Check security boundaries in the compiled PP foundation draft; no Azure calls."""
import argparse
import copy
import json
from pathlib import Path


def require(value, message):
    if not value:
        raise ValueError(message)


def verify(template, parameters):
    require(template['parameters']['deployServiceFoundations']['defaultValue'] is False, 'Opt-in must default off')
    require(parameters['parameters']['deployServiceFoundations']['value'] is False, 'Committed dev deployment must remain off')
    require(template['variables']['includeServiceFoundations'] == "[and(parameters('deployServiceFoundations'), equals(parameters('environment'), 'dev'))]", 'Development-only gate required')
    deployments = [r for r in template['resources'] if r['type'] == 'Microsoft.Resources/deployments']
    modules = {r['copy']['name']: r for r in deployments if 'copy' in r}
    require(set(modules) == {'appConfiguration', 'keyVault', 'appService', 'runtimeAccess'}, 'Exactly four resource-type module loops required')
    require(template['variables']['serviceNames'] == ['aquarium', 'tracking'], 'Exactly two initial services')
    for module in modules.values():
        require(module['condition'] == "[variables('includeServiceFoundations')]", 'Every foundation module must be conditional')
        require(module['copy']['count'] == "[length(variables('serviceNames'))]", 'Module must use matching service loop')
    service = modules['runtimeAccess']['properties']['template']
    resources = [r for module in modules.values() for r in module['properties']['template']['resources']]
    expected_types = {
        'appConfiguration': {'Microsoft.AppConfiguration/configurationStores'},
        'keyVault': {'Microsoft.KeyVault/vaults'},
        'appService': {'Microsoft.Web/sites', 'Microsoft.Web/sites/basicPublishingCredentialsPolicies'},
        'runtimeAccess': {'Microsoft.Authorization/roleAssignments'},
    }
    for name, types in expected_types.items():
        require({r['type'] for r in modules[name]['properties']['template']['resources']} == types, 'Resource types mixed in module ' + name)
    for service_name in ['aquarium', 'tracking']:
        for name in ['apiAppName', 'appConfigurationName', 'keyVaultName']:
            prefix = {'apiAppName': 'ApiAppName', 'appConfigurationName': 'AppConfigurationName', 'keyVaultName': 'KeyVaultName'}[name]
            require(template['variables']['resourceNames'][service_name][name] == f"[parameters('{service_name}{prefix}')]", 'Service names crossed')
    for module_name, key in [('appService', 'apiAppName'), ('appConfiguration', 'appConfigurationName'), ('keyVault', 'keyVaultName'), ('runtimeAccess', 'apiAppName')]:
        require(modules[module_name]['properties']['parameters'][key]['value'] == f"[variables('resourceNames')[variables('serviceNames')[copyIndex()]].{key}]", 'Module must use current service name')
    for module_name, keys in [('appService', {'appConfigurationEndpoint': ('app-config', 'endpoint'), 'keyVaultUri': ('key-vault', 'vaultUri')}), ('runtimeAccess', {'principalId': ('appservice', 'principalId'), 'appConfigurationName': ('app-config', 'appConfigurationName'), 'keyVaultName': ('key-vault', 'keyVaultName')})]:
        for key, (module_type, output) in keys.items():
            value = modules[module_name]['properties']['parameters'][key]['value']
            require(f'parameterpilot-{{0}}-{module_type}-{{1}}' in value and "variables('serviceNames')[copyIndex()]" in value and f'.outputs.{output}.value' in value, 'Cross-service module output wiring')
    allowed = {'Microsoft.AppConfiguration/configurationStores', 'Microsoft.KeyVault/vaults', 'Microsoft.Web/sites', 'Microsoft.Web/sites/basicPublishingCredentialsPolicies', 'Microsoft.Authorization/roleAssignments'}
    require(len(resources) == 7 and {r['type'] for r in resources} == allowed, 'Unexpected resource or shared infrastructure mutation')
    app = next(r for r in resources if r['type'] == 'Microsoft.Web/sites')
    props = app['properties']; config = props['siteConfig']
    require(app['identity'] == {'type': 'SystemAssigned'}, 'Distinct system identity required')
    require(props['enabled'] is False and props['publicNetworkAccess'] == 'Disabled', 'Bootstrap app must remain stopped and inaccessible')
    require(props['httpsOnly'] is True and props['serverFarmId'] == "[parameters('appServicePlanId')]", 'HTTPS and existing plan required')
    require(config['ipSecurityRestrictionsDefaultAction'] == config['scmIpSecurityRestrictionsDefaultAction'] == 'Deny', 'Main and SCM must deny by default')
    require(config['scmIpSecurityRestrictionsUseMain'] is True and config['ftpsState'] == 'Disabled', 'SCM/FTP protection required')
    require(config['minTlsVersion'] == config['scmMinTlsVersion'] == '1.2', 'TLS floor required')
    require('linuxFxVersion' not in config, 'No unreviewed image')
    require(all(r['properties']['allow'] is False for r in resources if r['type'].endswith('basicPublishingCredentialsPolicies')), 'Publishing passwords forbidden')
    store = next(r for r in resources if r['type'].startswith('Microsoft.AppConfiguration/'))
    require(store['sku']['name'] == 'Free' and store['properties']['disableLocalAuth'] is True, 'Free store without access keys required')
    vault = next(r for r in resources if r['type'] == 'Microsoft.KeyVault/vaults')
    v = vault['properties']
    require(v['sku']['name'] == 'standard' and v['enableRbacAuthorization'] is True and v['accessPolicies'] == [], 'Standard RBAC vault required')
    require(v['enablePurgeProtection'] is True and v['enableSoftDelete'] is True and v['softDeleteRetentionInDays'] == 90, 'Vault deletion protection required')
    require(app['name'] == "[parameters('apiAppName')]", 'Explicit API name required')
    require(store['name'] == "[parameters('appConfigurationName')]", 'Explicit configuration name required')
    require(vault['name'] == "[parameters('keyVaultName')]", 'Explicit vault name required')
    expected_names = {
        'aquariumApiAppName': 'api-adt-aquarium-dev',
        'trackingApiAppName': 'api-adt-tracking-dev',
        'aquariumAppConfigurationName': 'appcs-adt-aquarium-dev',
        'trackingAppConfigurationName': 'appcs-adt-tracking-dev',
        'aquariumKeyVaultName': 'kv-adt-aquarium-dev',
        'trackingKeyVaultName': 'kv-adt-tracking-dev',
        'staticWebAppName': 'stapp-adt-parameterpilot-dev',
        'applicationResourceGroupName': 'rg-parameterpilot-dev',
        'platformResourceGroupName': 'rg-platform-dev',
        'appServicePlanName': 'asp-platform-dev',
    }
    for name, value in expected_names.items():
        require(parameters['parameters'][name]['value'] == value, 'Unexpected Development name: ' + name)
    require('uniqueString(' not in json.dumps(service), 'Resource names must not have generated suffixes')
    require('516239f1-63e1-4d78-a4de-a74fb236a071' in service['variables']['configurationReader'], 'Only Configuration Data Reader')
    require('4633458b-17de-408a-b874-0445c86b69e6' in service['variables']['secretsUser'], 'Only Key Vault Secrets User')
    grants = [r for r in resources if r['type'] == 'Microsoft.Authorization/roleAssignments']
    for grant, resource_type, role in zip(grants, ['Microsoft.AppConfiguration/configurationStores', 'Microsoft.KeyVault/vaults'], ['configurationReader', 'secretsUser']):
        require(resource_type in grant['scope'], 'Grant must target own store/vault')
        g = grant['properties']
        require(g['roleDefinitionId'] == f"[variables('{role}')]" and g['principalType'] == 'ServicePrincipal', 'Unexpected privilege')
        require(g['principalId'] == "[parameters('principalId')]", 'Grant must use the verified API principal parameter')
    serialised = json.dumps(template).lower()
    require('listkeys(' not in serialised and 'listcredentials(' not in serialised, 'No credential retrieval')


def negative_checks(template, parameters):
    mutations = [
        ('Microsoft.Web/sites', lambda r: r['properties'].update(enabled=True)),
        ('Microsoft.Web/sites', lambda r: r['properties'].update(publicNetworkAccess='Enabled')),
        ('Microsoft.Web/sites', lambda r: r['properties']['siteConfig'].update(scmIpSecurityRestrictionsDefaultAction='Allow')),
        ('Microsoft.AppConfiguration/configurationStores', lambda r: r['properties'].update(disableLocalAuth=False)),
        ('Microsoft.AppConfiguration/configurationStores', lambda r: r['sku'].update(name='Standard')),
        ('Microsoft.KeyVault/vaults', lambda r: r['properties'].update(enableRbacAuthorization=False)),
        ('Microsoft.Authorization/roleAssignments', lambda r: r.update(scope="[resourceGroup().id]")),
    ]
    for resource_type, mutate in mutations:
        changed = copy.deepcopy(template)
        resources = [r for module in changed['resources'] if 'copy' in module for r in module['properties']['template']['resources']]
        mutate(next(r for r in resources if r['type'] == resource_type))
        try:
            verify(changed, parameters)
        except ValueError:
            continue
        raise AssertionError('Unsafe mutation accepted: ' + resource_type)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('template')
    parser.add_argument('parameters')
    args = parser.parse_args()
    template = json.loads(Path(args.template).read_text(encoding='utf-8-sig'))
    parameters = json.loads(Path(args.parameters).read_text(encoding='utf-8-sig'))
    verify(template, parameters)
    negative_checks(template, parameters)
    print('PASS: foundation resource/security boundaries and 7 unsafe-mutation checks')
