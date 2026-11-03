targetScope = 'subscription'

// ============================================================================
// PP application release roles — definitions alone do not grant access
// ============================================================================

param applicationResourceGroupName string

resource apiRelease 'Microsoft.Authorization/roleDefinitions@2022-04-01' = {
  name: guid(subscription().id, 'parameterpilot-api-release-dev')
  properties: {
    roleName: 'Parameter Pilot API Release Dev'
    description: 'Update configuration and restart existing PP API hosts; no host creation, IAM or secret listing.'
    type: 'CustomRole'
    assignableScopes: [subscriptionResourceId('Microsoft.Resources/resourceGroups', applicationResourceGroupName)]
    permissions: [{
      actions: [
        'Microsoft.Web/sites/read'
        'Microsoft.Web/sites/config/read'
        'Microsoft.Web/sites/config/write'
        'Microsoft.Web/sites/restart/action'
      ]
      notActions: []
      dataActions: []
      notDataActions: []
    }]
  }
}

resource websiteRelease 'Microsoft.Authorization/roleDefinitions@2022-04-01' = {
  name: guid(subscription().id, 'parameterpilot-website-release-dev')
  properties: {
    roleName: 'Parameter Pilot Website Release Dev'
    description: 'Read the existing PP static website and its deployment token; no site creation or role administration.'
    type: 'CustomRole'
    assignableScopes: [subscriptionResourceId('Microsoft.Resources/resourceGroups', applicationResourceGroupName)]
    permissions: [{
      actions: [
        'Microsoft.Web/staticSites/read'
        'Microsoft.Web/staticSites/listsecrets/action'
      ]
      notActions: []
      dataActions: []
      notDataActions: []
    }]
  }
}

output apiReleaseRoleId string = apiRelease.id
output websiteReleaseRoleId string = websiteRelease.id
