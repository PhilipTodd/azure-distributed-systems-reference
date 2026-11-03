targetScope = 'resourceGroup'

// ============================================================================
// Shared Cosmos resources
// ============================================================================

param accountName string
param databaseName string
param containerName string
param trackingPrincipalId string

resource account 'Microsoft.DocumentDB/databaseAccounts@2024-11-15' existing = {
  name: accountName
}
resource database 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases@2024-11-15' existing = {
  parent: account
  name: databaseName
}

// ============================================================================
// Application-owned Tracking container
// ============================================================================

// Shares existing database throughput; no TTL, migration or domain records.
resource container 'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers@2024-11-15' = {
  parent: database
  name: containerName
  properties: {
    resource: {
      id: containerName
      partitionKey: {
        paths: ['/tankId']
        kind: 'Hash'
        version: 2
      }
    }
    options: {}
  }
}

// ============================================================================
// Tracking data-plane permissions
// ============================================================================

// Defining a role is not a grant. The assignment below is container-scoped.
resource runtimeRole 'Microsoft.DocumentDB/databaseAccounts/sqlRoleDefinitions@2024-11-15' = {
  parent: account
  name: guid(account.id, 'parameterpilot-tracking-runtime')
  properties: {
    roleName: 'Parameter Pilot Tracking Runtime'
    type: 'CustomRole'
    assignableScopes: [account.id]
    permissions: [
      {
        dataActions: [
          'Microsoft.DocumentDB/databaseAccounts/readMetadata'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/create'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/read'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/replace'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/upsert'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/delete'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/executeQuery'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/readChangeFeed'
        ]
      }
    ]
  }
}

resource runtimeAssignment 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2024-11-15' = {
  parent: account
  name: guid(account.id, trackingPrincipalId, databaseName, containerName, 'runtime')
  properties: {
    principalId: trackingPrincipalId
    roleDefinitionId: runtimeRole.id
    scope: '${account.id}/dbs/${databaseName}/colls/${containerName}'
  }
  dependsOn: [container]
}

// ============================================================================
// Outputs
// ============================================================================

output containerId string = container.id
output dataScope string = runtimeAssignment.properties.scope
output roleDefinitionId string = runtimeRole.id
output roleAssignmentId string = runtimeAssignment.id
