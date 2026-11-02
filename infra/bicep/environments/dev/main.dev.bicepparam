using './main.bicep'

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
