using './main.bicep'

// ============================================================================
// Controlled delivery access — explicit opt-in after directory bootstrap
// ============================================================================

param deployDeliveryAccess = false
param deploymentPrincipalId = ''
param developerGroupId = ''

// ============================================================================
// Customer identity — explicit Development-only opt-in
// ============================================================================

param deployCustomerIdentity = false
param customerTenantSubdomain = 'parameterpilotdev'
param customerTenantDisplayName = 'Parameter Pilot Development Customers'

// ============================================================================
// Environment
// ============================================================================

param environment = 'dev'

// ============================================================================
// Resource Groups
// ============================================================================

param applicationResourceGroupName = 'rg-parameterpilot-dev'
param platformResourceGroupName = 'rg-platform-dev'

// ============================================================================
// Locations
// ============================================================================

param applicationLocation = 'australiaeast'
param apiLocation = 'australiaeast'
param staticWebAppLocation = 'eastasia'

// ============================================================================
// Shared Platform Resources
// ============================================================================

param appServicePlanName = 'asp-platform-dev'

// ============================================================================
// Application Resources
// ============================================================================

param aquariumApiAppName = 'api-adt-aquarium-dev'

param trackingApiAppName = 'api-adt-tracking-dev'

param staticWebAppName = 'stapp-adt-parameterpilot-dev'

// ============================================================================
// App Configuration
// ============================================================================

param aquariumAppConfigurationName = 'appcs-adt-aquarium-dev'

param trackingAppConfigurationName = 'appcs-adt-tracking-dev'

// ============================================================================
// Key Vault
// ============================================================================

param aquariumKeyVaultName = 'kv-adt-aquarium-dev'

param trackingKeyVaultName = 'kv-adt-tracking-dev'

// ============================================================================
// Static Web App Custom Domains
// ============================================================================

param staticWebAppCustomDomains = [
  'parameterpilot.com'
  'www.parameterpilot.com'
]

// ============================================================================
// Deployment Controls
// ============================================================================

// Disabled until the owner reviews and approves the foundation deployment.
param deployServiceFoundations = false

// ============================================================================
// Cosmos DB
// ============================================================================

param cosmosAccountName = 'cosmos-adt-platform-dev'
param cosmosDatabaseName = 'ReferenceProjects'
param trackingContainerName = 'parameterpilot-tracking'
param trackingPrincipalId = '6c046dfa-2416-4706-893d-7cc000afecf0'

// Separate opt-in: manage data access without redeploying stopped API hosts.
param deployTrackingDataAccess = false
