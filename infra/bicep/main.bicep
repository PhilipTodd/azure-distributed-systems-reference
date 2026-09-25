targetScope = 'subscription'

@description('Name of the Parameter Pilot resource group.')
param resourceGroupName string

@description('Azure region for the Parameter Pilot resource group.')
param primaryLocation string

@description('Deployment environment.')
@allowed(['dev', 'test', 'prod'])
param environment string

@description('Azure region for the Static Web App. Check regional availability before deployment.')
param staticWebAppLocation string

@description('Name of the Parameter Pilot Static Web App.')
param staticWebAppName string

@description('Custom domain for the Parameter Pilot web application.')
param staticWebAppCustomDomainName string

resource applicationResourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: resourceGroupName
  location: primaryLocation
}

module web 'modules/static-web-app.bicep' = {
  name: 'parameterpilot-static-web-app-${environment}'
  scope: applicationResourceGroup
  params: {
    name: staticWebAppName
    location: staticWebAppLocation
    environment: environment
    customDomainName: staticWebAppCustomDomainName
  }
}

output staticWebAppName string = web.outputs.name
output staticWebAppHostname string = web.outputs.defaultHostname
