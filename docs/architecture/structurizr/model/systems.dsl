parameterPilot = softwareSystem "Parameter Pilot" "Aquarium parameter tracking, trend analysis and AI-assisted maintenance advice." "System" {
  web = container "Web Application" "Browser-based Angular application for recording data and viewing trends and advice." "Angular" "Web"

  apiGateway = container "API Gateway" "Single authenticated entry point for browser clients and external integrations." "Azure API Management" "Gateway,Microsoft Azure - API Management Services"

  aquariumService = container "Aquarium Service" "Manages tanks, aquarium configuration, parameter definitions and current state." ".NET 10 Web API" "Service"
  trackingService = container "Tracking Service" "Records parameter measurements, events and observations and provides historical trend data." ".NET 10 Web API" "Service"
  advisorService = container "Advisor Service" "Produces maintenance advice from aquarium measurements, events and relevant reference knowledge." ".NET 10 Web API / Azure AI" "Service"

  eventProcessor = container "Event Processor" "Processes asynchronous domain events and performs background work." ".NET 10 Worker / Azure Functions" "Service"

  sqlDb = container "Aquarium SQL Database" "Stores transactional aquarium and configuration data." "Azure SQL" "Database,Infra,Microsoft Azure - SQL Database"
  cosmosDb = container "Parameter Event Store" "Stores parameter measurements, observations and historical event-oriented data." "Azure Cosmos DB" "Database,Infra,Microsoft Azure - Azure Cosmos DB"
  serviceBus = container "Message Broker" "Provides asynchronous communication between application services and background processors." "Azure Service Bus" "Infra,Messaging,Microsoft Azure - Service Bus"
  blobStorage = container "Photo Storage" "Stores aquarium photos and other user-uploaded media." "Azure Blob Storage" "Database,Infra,Microsoft Azure - Storage Accounts"

  aiSearch = container "Knowledge Search" "Retrieves curated aquarium reference material used to ground AI advice." "Azure AI Search" "Infra,Microsoft Azure - Search Services"
  appInsights = container "Observability" "Application telemetry, distributed tracing, metrics and diagnostics." "Azure Application Insights / Log Analytics" "Infra,Microsoft Azure - Application Insights"
}

entra = softwareSystem "Microsoft Entra External ID" "Identity provider for customer authentication and application access." "External,Identity,Microsoft Azure - Azure Active Directory"
stripe = softwareSystem "Stripe" "External payment provider for subscription billing." "External"
