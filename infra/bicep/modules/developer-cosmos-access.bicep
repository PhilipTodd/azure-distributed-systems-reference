targetScope = 'resourceGroup'

// ============================================================================
// Shared Cosmos account — PP Tracking container read access only
// ============================================================================

param accountName string
param databaseName string
param containerName string
param developerGroupId string

resource account 'Microsoft.DocumentDB/databaseAccounts@2024-11-15' existing = { name: accountName }
resource reader 'Microsoft.DocumentDB/databaseAccounts/sqlRoleDefinitions@2024-11-15' = {
  parent: account
  name: guid(account.id, 'parameterpilot-developer-reader')
  properties: {
    roleName: 'Parameter Pilot Developer Reader'
    type: 'CustomRole'
    assignableScopes: [account.id]
    permissions: [{ dataActions: [
      'Microsoft.DocumentDB/databaseAccounts/readMetadata'
      'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/read'
      'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/executeQuery'
      'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/readChangeFeed'
    ] }]
  }
}
resource assignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2024-11-15' = {
  parent: account
  name: guid(account.id, developerGroupId, databaseName, containerName, 'developer-reader')
  properties: {
    principalId: developerGroupId
    roleDefinitionId: reader.id
    scope: '${account.id}/dbs/${databaseName}/colls/${containerName}'
  }
}
