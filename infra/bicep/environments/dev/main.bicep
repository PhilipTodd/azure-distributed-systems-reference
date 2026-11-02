targetScope = 'subscription'

// ============================================================================
// Deployment
// ============================================================================

@description('Deployment environment.')
@allowed([
  'dev'
  'test'
  'prod'
])
param environment string

@description('Location of the Parameter Pilot application resource group.')
param applicationLocation string

@description('Name of the Parameter Pilot application resource group.')
param applicationResourceGroupName string

@description('Opt in to the reviewed Development service foundations; does not activate API traffic.')
param deployServiceFoundations bool = false

// ============================================================================
// Shared platform resources
// ============================================================================

@description('Name of the shared platform resource group.')
param platformResourceGroupName string = 'rg-platform-dev'

@description('Name of the existing shared Linux B1 App Service Plan.')
param appServicePlanName string = 'asp-platform-dev'

// ============================================================================
// Application compute
// ============================================================================

@description('Azure region of the existing shared plan used by API hosts.')
param apiLocation string = 'australiaeast'

@description('Globally unique name of the Aquarium API App Service.')
param aquariumApiAppName string

@description('Globally unique name of the Tracking API App Service.')
param trackingApiAppName string

// ============================================================================
// Static Web App
// ============================================================================

@description('Azure region for the existing Static Web App.')
param staticWebAppLocation string

@description('Globally unique name of the Parameter Pilot Static Web App.')
param staticWebAppName string

@description('Custom domains associated with the Static Web App.')
param staticWebAppCustomDomains array = []

// ============================================================================
// App Configuration
// ============================================================================

@description('Globally unique name of the Aquarium App Configuration store.')
param aquariumAppConfigurationName string

@description('Globally unique name of the Tracking App Configuration store.')
param trackingAppConfigurationName string

// ============================================================================
// Key Vault
// ============================================================================

@description('Globally unique name of the Aquarium Key Vault.')
@maxLength(24)
param aquariumKeyVaultName string

@description('Globally unique name of the Tracking Key Vault.')
@maxLength(24)
param trackingKeyVaultName string

// ============================================================================
// Application resource group
// ============================================================================

resource applicationResourceGroup 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: applicationResourceGroupName
  location: applicationLocation
}

// ============================================================================
// Shared platform resources
// ============================================================================

resource sharedAppServicePlan 'Microsoft.Web/serverfarms@2024-04-01' existing = {
  name: appServicePlanName
  scope: resourceGroup(platformResourceGroupName)
}

// ============================================================================
// Service deployment configuration
// ============================================================================

// Preserve the review-only, Development-only safety gate.
var includeServiceFoundations = deployServiceFoundations && environment == 'dev'
var serviceNames = ['aquarium', 'tracking']
var resourceNames = {
  aquarium: {
    apiAppName: aquariumApiAppName
    appConfigurationName: aquariumAppConfigurationName
    keyVaultName: aquariumKeyVaultName
  }
  tracking: {
    apiAppName: trackingApiAppName
    appConfigurationName: trackingAppConfigurationName
    keyVaultName: trackingKeyVaultName
  }
}

// ============================================================================
// Application Static Web App
// ============================================================================

module web '../../modules/static-web-app.bicep' = {
  name: 'parameterpilot-static-web-app-${environment}'
  scope: applicationResourceGroup

  params: {
    name: staticWebAppName
    location: staticWebAppLocation
    environment: environment
    customDomains: staticWebAppCustomDomains
  }
}

// ============================================================================
// Application-owned App Configuration stores
// ============================================================================

module appConfiguration '../../modules/app-config.bicep' = [
  for serviceName in serviceNames: if (includeServiceFoundations) {
    name: 'parameterpilot-${serviceName}-app-config-${environment}'
    scope: applicationResourceGroup

    params: {
      location: apiLocation
      appConfigurationName: resourceNames[serviceName].appConfigurationName
      tags: {
        application: 'parameterpilot'
        service: serviceName
        environment: environment
      }
    }
  }
]

// ============================================================================
// Application-owned Key Vaults
// ============================================================================

module keyVault '../../modules/key-vault.bicep' = [
  for serviceName in serviceNames: if (includeServiceFoundations) {
    name: 'parameterpilot-${serviceName}-key-vault-${environment}'
    scope: applicationResourceGroup

    params: {
      location: apiLocation
      keyVaultName: resourceNames[serviceName].keyVaultName
      tags: {
        application: 'parameterpilot'
        service: serviceName
        environment: environment
      }
    }
  }
]

// ============================================================================
// Application App Services
// ============================================================================

module appService '../../modules/appservice.bicep' = [
  for (serviceName, i) in serviceNames: if (includeServiceFoundations) {
    name: 'parameterpilot-${serviceName}-appservice-${environment}'
    scope: applicationResourceGroup

    params: {
      location: apiLocation
      apiAppName: resourceNames[serviceName].apiAppName
      appServicePlanId: sharedAppServicePlan.id
      appConfigurationEndpoint: appConfiguration[i]!.outputs.endpoint
      keyVaultUri: keyVault[i]!.outputs.vaultUri
      tags: {
        application: 'parameterpilot'
        service: serviceName
        environment: environment
      }
    }
  }
]

// ============================================================================
// Application runtime read permissions
// ============================================================================

module runtimeAccess '../../modules/role-assignments.bicep' = [
  for (serviceName, i) in serviceNames: if (includeServiceFoundations) {
    name: 'parameterpilot-${serviceName}-runtime-access-${environment}'
    scope: applicationResourceGroup

    params: {
      apiAppName: resourceNames[serviceName].apiAppName
      principalId: appService[i]!.outputs.principalId
      appConfigurationName: appConfiguration[i]!.outputs.appConfigurationName
      keyVaultName: keyVault[i]!.outputs.keyVaultName
    }
  }
]

// ============================================================================
// Outputs
// ============================================================================

output staticWebAppName string = web.outputs.name
output staticWebAppHostname string = web.outputs.defaultHostname

output serviceFoundationResources array = includeServiceFoundations
  ? [
      {
        service: 'aquarium'
        appId: appService[0]!.outputs.apiAppId
        principalId: appService[0]!.outputs.principalId
        configurationEndpoint: appConfiguration[0]!.outputs.endpoint
        vaultUri: keyVault[0]!.outputs.vaultUri
      }
      {
        service: 'tracking'
        appId: appService[1]!.outputs.apiAppId
        principalId: appService[1]!.outputs.principalId
        configurationEndpoint: appConfiguration[1]!.outputs.endpoint
        vaultUri: keyVault[1]!.outputs.vaultUri
      }
    ]
  : []
