targetScope = 'resourceGroup'

// ============================================================================
// Deployment
// ============================================================================

@description('Azure region for the application resource.')
param location string

@description('Tags applied to the service-owned resource.')
param tags object

// ============================================================================
// Key Vault
// ============================================================================

@description('Globally unique name of the service Key Vault.')
@maxLength(24)
param keyVaultName string

resource vault 'Microsoft.KeyVault/vaults@2024-11-01' = {
  name: keyVaultName
  location: location
  tags: tags
  properties: {
    tenantId: tenant().tenantId
    sku: { family: 'A', name: 'standard' }
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
    enabledForDeployment: false
    enabledForDiskEncryption: false
    enabledForTemplateDeployment: false
    publicNetworkAccess: 'Enabled'
    networkAcls: { bypass: 'None', defaultAction: 'Allow' }
    accessPolicies: []
  }
}

// ============================================================================
// Outputs
// ============================================================================

output keyVaultId string = vault.id
output keyVaultName string = vault.name
output vaultUri string = vault.properties.vaultUri
