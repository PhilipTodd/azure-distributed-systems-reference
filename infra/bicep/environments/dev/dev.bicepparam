using '../../main.bicep'

param environment = 'dev'
param primaryLocation = 'australiaeast'
param resourceGroupName = 'rg-parameterpilot-dev'
param staticWebAppLocation = 'eastasia'
param staticWebAppName = 'stapp-adt-parameterpilot-dev'
param staticWebAppCustomDomains = [
  'parameterpilot.com'
  'www.parameterpilot.com'
]
