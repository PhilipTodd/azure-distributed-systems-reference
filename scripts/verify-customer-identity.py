"""Offline customer-tenant scope/billing guardrails for compiled Bicep."""
import argparse
import copy
import json
from pathlib import Path


def verify(template, parameters):
    p = parameters['parameters']
    if p['deployCustomerIdentity']['value'] is not False:
        raise ValueError('Customer creation must require explicit opt-in')
    module = next(r for r in template['resources'] if 'customer-identity-' in r.get('name', ''))
    if module['condition'] != "[and(parameters('deployCustomerIdentity'), equals(parameters('environment'), 'dev'))]":
        raise ValueError('Customer tenant must be Development-only')
    resources = module['properties']['template']['resources']
    if len(resources) != 1 or resources[0]['type'] != 'Microsoft.AzureActiveDirectory/ciamDirectories':
        raise ValueError('Only one customer directory/link resource is allowed')
    directory = resources[0]
    if directory['sku'] != {'name': 'Base', 'tier': 'A0'}:
        raise ValueError('Only the core Base/A0 SKU is approved')
    properties = directory['properties']['createTenantProperties']
    if properties != {'countryCode': "[parameters('countryCode')]", 'displayName': "[parameters('displayName')]", 'isGoLocalTenant': False}:
        raise ValueError('Go-Local must be explicitly disabled; no extra tenant settings')
    params = module['properties']['template']['parameters']
    if params['countryCode']['defaultValue'] != 'AU' or params['resourceLocation']['defaultValue'] != 'Global':
        raise ValueError('Country/resource label must match the reviewed AU setup')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('template', type=Path)
    parser.add_argument('parameters', type=Path)
    args = parser.parse_args()
    template = json.loads(args.template.read_text(encoding='utf-8-sig'))
    parameters = json.loads(args.parameters.read_text(encoding='utf-8-sig'))
    verify(template, parameters)
    for field in ['addon', 'sku', 'resource', 'condition', 'savedSwitch']:
        changed, inputs = copy.deepcopy(template), copy.deepcopy(parameters)
        module = next(r for r in changed['resources'] if 'customer-identity-' in r.get('name', ''))
        directory = module['properties']['template']['resources'][0]
        if field == 'addon': directory['properties']['createTenantProperties']['isGoLocalTenant'] = True
        elif field == 'sku': directory['sku']['name'] = 'PremiumP1'
        elif field == 'resource': directory['type'] = 'Microsoft.AzureActiveDirectory/b2cDirectories'
        elif field == 'condition': module['condition'] = True
        else: inputs['parameters']['deployCustomerIdentity']['value'] = True
        try:
            verify(changed, inputs)
        except ValueError:
            continue
        raise RuntimeError('Unsafe customer identity mutation accepted')
    print('PASS: customer identity scope/core SKU/no paid Go-Local and five unsafe mutations rejected')


if __name__ == '__main__':
    main()
