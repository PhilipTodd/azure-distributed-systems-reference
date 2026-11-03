targetScope = 'resourceGroup'

// ============================================================================
// Shared registry — PP repository permissions only
// ============================================================================

param registryName string
param deploymentPrincipalId string
param aquariumPrincipalId string
param trackingPrincipalId string

resource registry 'Microsoft.ContainerRegistry/registries@2025-04-01' existing = { name: registryName }
var writerRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '2a1e307c-b015-4ebd-883e-5b7698a07328')
var readerRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b93aa761-3e63-49ed-ac28-beffa264f7ac')
var runtimeRepositories = [
  { principalId: aquariumPrincipalId, repository: 'parameterpilot/aquarium-api' }
  { principalId: trackingPrincipalId, repository: 'parameterpilot/tracking-api' }
]

resource publish 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(registry.id, deploymentPrincipalId, 'pp-api-repository-writer')
  scope: registry
  properties: {
    principalId: deploymentPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: writerRoleId
    conditionVersion: '2.0'
    condition: '((!(ActionMatches{\'Microsoft.ContainerRegistry/registries/repositories/content/read\'}) AND !(ActionMatches{\'Microsoft.ContainerRegistry/registries/repositories/content/write\'}) AND !(ActionMatches{\'Microsoft.ContainerRegistry/registries/repositories/metadata/read\'}) AND !(ActionMatches{\'Microsoft.ContainerRegistry/registries/repositories/metadata/write\'})) OR (@Request[Microsoft.ContainerRegistry/registries/repositories:name] StringEqualsIgnoreCase \'parameterpilot/aquarium-api\') OR (@Request[Microsoft.ContainerRegistry/registries/repositories:name] StringEqualsIgnoreCase \'parameterpilot/tracking-api\'))'
  }
}

resource pull 'Microsoft.Authorization/roleAssignments@2022-04-01' = [for item in runtimeRepositories: {
  name: guid(registry.id, item.principalId, item.repository, 'reader')
  scope: registry
  properties: {
    principalId: item.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: readerRoleId
    conditionVersion: '2.0'
    condition: '((!(ActionMatches{\'Microsoft.ContainerRegistry/registries/repositories/content/read\'}) AND !(ActionMatches{\'Microsoft.ContainerRegistry/registries/repositories/metadata/read\'})) OR (@Request[Microsoft.ContainerRegistry/registries/repositories:name] StringEqualsIgnoreCase \'${item.repository}\'))'
  }
}]
