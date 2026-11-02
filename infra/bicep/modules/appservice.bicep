targetScope = 'resourceGroup'

// ============================================================================
// Deployment
// ============================================================================

@description('Azure region for the application resource.')
param location string

@description('Tags applied to the service-owned resource.')
param tags object

// ============================================================================
// Application compute
// ============================================================================

@description('Globally unique name of the service API App Service.')
param apiAppName string

@description('Resource ID of the existing shared Linux App Service Plan.')
param appServicePlanId string

// ============================================================================
// Runtime configuration
// ============================================================================

@description('Endpoint of this service’s App Configuration store.')
param appConfigurationEndpoint string

@description('URI of this service’s Key Vault.')
param keyVaultUri string

// ============================================================================
// API App Service
// ============================================================================

// Identity/bootstrap host only: stopped, no image, no ingress. Not a working API.
// Image deployment, authentication, ACR scope and narrow ingress need separate review.
resource app 'Microsoft.Web/sites@2024-11-01' = {
  name: apiAppName
  location: location
  tags: tags
  kind: 'app,linux,container'
  identity: { type: 'SystemAssigned' }
  properties: {
    serverFarmId: appServicePlanId
    reserved: true
    enabled: false
    httpsOnly: true
    publicNetworkAccess: 'Disabled'
    clientAffinityEnabled: false
    siteConfig: {
      alwaysOn: false
      minTlsVersion: '1.2'
      scmMinTlsVersion: '1.2'
      ftpsState: 'Disabled'
      remoteDebuggingEnabled: false
      acrUseManagedIdentityCreds: true
      ipSecurityRestrictionsDefaultAction: 'Deny'
      scmIpSecurityRestrictionsDefaultAction: 'Deny'
      scmIpSecurityRestrictionsUseMain: true
      appSettings: [
        { name: 'AppConfiguration__Endpoint', value: appConfigurationEndpoint }
        { name: 'KeyVault__VaultUri', value: keyVaultUri }
      ]
    }
  }
}

resource ftpPublishing 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2024-11-01' = {
  parent: app
  name: 'ftp'
  properties: { allow: false }
}
resource scmPublishing 'Microsoft.Web/sites/basicPublishingCredentialsPolicies@2024-11-01' = {
  parent: app
  name: 'scm'
  properties: { allow: false }
}

// ============================================================================
// Outputs
// ============================================================================

output apiAppId string = app.id
output apiAppName string = app.name
output principalId string = app.identity.principalId
