@description('Globally unique name for the Parameter Pilot Static Web App.')
param name string

@description('Azure region for the Static Web App resource.')
param location string

@description('Deployment environment label.')
param environment string

@description('Custom domain associated with the Static Web App.')
param customDomainName string

resource staticWebApp 'Microsoft.Web/staticSites@2023-12-01' = {
  name: name
  location: location
  sku: {
    name: 'Free'
    tier: 'Free'
  }
  properties: {
    // The site is deployed separately using its deployment token.
    // Do not link a repository here: doing so can create an unwanted workflow.
    buildProperties: {
      skipGithubActionWorkflowGeneration: true
    }
  }
  tags: {
    application: 'parameterpilot'
    environment: environment
  }
}

resource customDomain 'Microsoft.Web/staticSites/customDomains@2023-12-01' = {
  parent: staticWebApp
  name: customDomainName
  properties: {}
}

output name string = staticWebApp.name
output defaultHostname string = staticWebApp.properties.defaultHostname
