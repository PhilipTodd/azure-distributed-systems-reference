targetScope = 'resourceGroup'

// ============================================================================
// Development customer tenant and subscription billing link
// ============================================================================

@description('Globally unique customer tenant subdomain; no punctuation.')
@minLength(1)
@maxLength(26)
param tenantSubdomain string

param displayName string

// Actual portal-created resource metadata: Global, with Go-Local disabled.
// Country is AU; this resource label is not an Australian residency purchase.
@allowed(['Global'])
param resourceLocation string = 'Global'

@allowed(['AU'])
param countryCode string = 'AU'

// Microsoft currently exposes this resource through a preview ARM API.
// Live provider preflight requires Base/A0 for the core MAU offering.
// The published 2023 template example's Standard name is rejected by Azure.
resource customerDirectory 'Microsoft.AzureActiveDirectory/ciamDirectories@2025-08-01-preview' = {
  name: '${tenantSubdomain}.onmicrosoft.com'
  location: resourceLocation
  sku: {
    name: 'Base'
    tier: 'A0'
  }
  properties: {
    createTenantProperties: {
      countryCode: countryCode
      displayName: displayName
      isGoLocalTenant: false
    }
  }
  tags: {
    application: 'parameterpilot'
    environment: 'dev'
    purpose: 'customer-identity'
  }
}

output resourceId string = customerDirectory.id
output tenantId string = customerDirectory.properties.tenantId
