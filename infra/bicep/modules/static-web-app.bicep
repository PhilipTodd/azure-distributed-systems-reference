@description('Globally unique name for the Parameter Pilot Static Web App.')
param name string

@description('Azure region for the Static Web App resource.')
param location string

@description('Deployment environment label.')
param environment string

@description('Custom domains associated with the Static Web App.')
param customDomains array = []

resource staticWebApp 'Microsoft.Web/staticSites@2023-12-01' = {
  name: name
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    buildProperties: {
      skipGithubActionWorkflowGeneration: true
    }
  }
  tags: {
    application: 'parameterpilot'
    environment: environment
  }
}

resource customDomainResources 'Microsoft.Web/staticSites/customDomains@2023-12-01' = [
  for domainName in customDomains: {
    parent: staticWebApp
    name: domainName
    properties: {
      validationMethod: 'dns-txt-token'
    }
  }
]

output name string = staticWebApp.name
output defaultHostname string = staticWebApp.properties.defaultHostname
