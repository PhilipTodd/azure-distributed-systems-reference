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

@description('Include the existing website/domain module; set false for access-only maintenance.')
param deployStaticWebApp bool = true

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
// Tracking Cosmos access
// ============================================================================

@description('Opt in to approved Tracking container and data grants; does not redeploy hosts.')
param deployTrackingDataAccess bool = false

param cosmosAccountName string = 'cosmos-adt-platform-dev'
param cosmosDatabaseName string = 'ReferenceProjects'
param trackingContainerName string = 'parameterpilot-tracking'

@description('Actual deployed Tracking managed identity, independently verified before deployment.')
param trackingPrincipalId string = '6c046dfa-2416-4706-893d-7cc000afecf0'

// ============================================================================
// Controlled deployment and ordinary developer access
// ============================================================================

@description('Opt in to approved Step 3 access only; directory/GitHub setup is separate.')
param deployDeliveryAccess bool = false

param deploymentPrincipalId string = ''
param developerGroupId string = ''
param aquariumPrincipalId string = 'e43e0132-e184-4669-8431-9f5a3ea5393e'
param containerRegistryName string = 'acradtplatformdev'

// ============================================================================
// Development customer identity
// ============================================================================

@description('Opt in to approved customer tenant creation/link only; does not configure apps or credentials.')
param deployCustomerIdentity bool = false

param customerTenantSubdomain string = 'parameterpilotdev'
param customerTenantDisplayName string = 'Parameter Pilot Development Customers'

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

module web '../../modules/static-web-app.bicep' = if (deployStaticWebApp) {
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
// Application-owned Tracking Cosmos container
// ============================================================================

module trackingDataAccess '../../modules/cosmos-container.bicep' = if (deployTrackingDataAccess && environment == 'dev') {
  name: 'parameterpilot-tracking-data-access-${environment}'
  scope: resourceGroup(platformResourceGroupName)

  params: {
    accountName: cosmosAccountName
    databaseName: cosmosDatabaseName
    containerName: trackingContainerName
    trackingPrincipalId: trackingPrincipalId
  }
}

// ============================================================================
// Controlled delivery access
// ============================================================================

module deliveryRoles '../../modules/deployment-role-definitions.bicep' = if (deployDeliveryAccess && environment == 'dev') {
  name: 'parameterpilot-delivery-role-definitions-dev'
  params: {
    applicationResourceGroupName: applicationResourceGroupName
  }
  dependsOn: [applicationResourceGroup]
}

module deliveryAccess '../../modules/deployment-access.bicep' = if (deployDeliveryAccess && environment == 'dev') {
  name: 'parameterpilot-delivery-access-dev'
  scope: applicationResourceGroup
  params: {
    deploymentPrincipalId: deploymentPrincipalId
    developerGroupId: developerGroupId
    apiReleaseRoleId: deliveryRoles!.outputs.apiReleaseRoleId
    websiteReleaseRoleId: deliveryRoles!.outputs.websiteReleaseRoleId
    apiAppNames: [aquariumApiAppName, trackingApiAppName]
    configurationStoreNames: [aquariumAppConfigurationName, trackingAppConfigurationName]
    staticWebAppName: staticWebAppName
  }
}

module registryAccess '../../modules/registry-access.bicep' = if (deployDeliveryAccess && environment == 'dev') {
  name: 'parameterpilot-registry-access-dev'
  scope: resourceGroup(platformResourceGroupName)
  params: {
    registryName: containerRegistryName
    deploymentPrincipalId: deploymentPrincipalId
    aquariumPrincipalId: aquariumPrincipalId
    trackingPrincipalId: trackingPrincipalId
  }
}

module developerCosmosAccess '../../modules/developer-cosmos-access.bicep' = if (deployDeliveryAccess && environment == 'dev') {
  name: 'parameterpilot-developer-cosmos-access-dev'
  scope: resourceGroup(platformResourceGroupName)
  params: {
    accountName: cosmosAccountName
    databaseName: cosmosDatabaseName
    containerName: trackingContainerName
    developerGroupId: developerGroupId
  }
}

// ============================================================================
// Development customer identity
// ============================================================================

module customerIdentity '../../modules/external-id.bicep' = if (deployCustomerIdentity && environment == 'dev') {
  name: 'parameterpilot-customer-identity-dev'
  scope: applicationResourceGroup
  params: {
    tenantSubdomain: customerTenantSubdomain
    displayName: customerTenantDisplayName
  }
}

output customerTenantId string = deployCustomerIdentity && environment == 'dev' ? customerIdentity!.outputs.tenantId : ''

// ============================================================================
// Outputs
// ============================================================================

output staticWebAppName string = staticWebAppName
output staticWebAppHostname string = deployStaticWebApp ? web!.outputs.defaultHostname : ''

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
