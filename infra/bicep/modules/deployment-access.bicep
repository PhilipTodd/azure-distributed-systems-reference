targetScope = 'resourceGroup'

// ============================================================================
// Existing PP resources and reviewed principals
// ============================================================================

param deploymentPrincipalId string
param developerGroupId string
param apiReleaseRoleId string
param websiteReleaseRoleId string
param apiAppNames array
param configurationStoreNames array
param staticWebAppName string

resource apps 'Microsoft.Web/sites@2024-11-01' existing = [for name in apiAppNames: { name: name }]
resource stores 'Microsoft.AppConfiguration/configurationStores@2024-06-01' existing = [for name in configurationStoreNames: { name: name }]
resource website 'Microsoft.Web/staticSites@2024-11-01' existing = { name: staticWebAppName }

// ============================================================================
// App-scoped release and resource-scoped developer reads
// ============================================================================

resource apiRelease 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for (name, i) in apiAppNames: {
  name: guid(apps[i].id, deploymentPrincipalId, apiReleaseRoleId)
  scope: apps[i]
  properties: { principalId: deploymentPrincipalId, principalType: 'ServicePrincipal', roleDefinitionId: apiReleaseRoleId }
}]

resource webRelease 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(website.id, deploymentPrincipalId, websiteReleaseRoleId)
  scope: website
  properties: { principalId: deploymentPrincipalId, principalType: 'ServicePrincipal', roleDefinitionId: websiteReleaseRoleId }
}

var readerRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'acdd72a7-3385-48ef-bd42-f606fba81ae7')
var configurationReaderRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '516239f1-63e1-4d78-a4de-a74fb236a071')

resource developerReader 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, developerGroupId, readerRoleId)
  properties: { principalId: developerGroupId, principalType: 'Group', roleDefinitionId: readerRoleId }
}

resource developerConfigurationReader 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for (name, i) in configurationStoreNames: {
  name: guid(stores[i].id, developerGroupId, configurationReaderRoleId)
  scope: stores[i]
  properties: { principalId: developerGroupId, principalType: 'Group', roleDefinitionId: configurationReaderRoleId }
}]
