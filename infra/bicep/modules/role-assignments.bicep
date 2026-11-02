targetScope = 'resourceGroup'

// ============================================================================
// Application resources
// ============================================================================

@description('Name of the service API App Service whose identity receives read access.')
param apiAppName string

@description('System-assigned principal ID returned by the corresponding API host.')
param principalId string

@description('Name of this service’s App Configuration store.')
param appConfigurationName string

@description('Name of this service’s Key Vault.')
param keyVaultName string

// ============================================================================
// Existing application resources
// ============================================================================

resource app 'Microsoft.Web/sites@2024-11-01' existing = {
  name: apiAppName
}

resource configuration 'Microsoft.AppConfiguration/configurationStores@2024-06-01' existing = {
  name: appConfigurationName
}

resource vault 'Microsoft.KeyVault/vaults@2024-11-01' existing = {
  name: keyVaultName
}

// ============================================================================
// Runtime read permissions
// ============================================================================

var configurationReader = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '516239f1-63e1-4d78-a4de-a74fb236a071'
)
var secretsUser = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '4633458b-17de-408a-b874-0445c86b69e6'
)

resource configurationRead 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(configuration.id, app.id, configurationReader)
  scope: configuration
  properties: {
    principalId: principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: configurationReader
  }
}
resource secretRead 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(vault.id, app.id, secretsUser)
  scope: vault
  properties: {
    principalId: principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: secretsUser
  }
}
