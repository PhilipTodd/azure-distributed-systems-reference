targetScope = 'resourceGroup'

// ============================================================================
// Deployment
// ============================================================================

@description('Azure region for the application resource.')
param location string

@description('Tags applied to the service-owned resource.')
param tags object

// ============================================================================
// App Configuration
// ============================================================================

@description('Globally unique name of the service App Configuration store.')
param appConfigurationName string

resource configuration 'Microsoft.AppConfiguration/configurationStores@2024-06-01' = {
  name: appConfigurationName
  location: location
  tags: tags
  sku: { name: 'Free' }
  properties: {
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
  }
}

// ============================================================================
// Outputs
// ============================================================================

output appConfigurationId string = configuration.id
output appConfigurationName string = configuration.name
output endpoint string = configuration.properties.endpoint
