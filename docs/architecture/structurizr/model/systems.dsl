parameterPilot = softwareSystem "Parameter Pilot" "Aquarium parameter tracking, trend analysis and AI-assisted maintenance advice." "System" {
  web = container "Web Application" "Browser-based Angular application for recording data and viewing trends and advice." "Angular" "Web"

  apiGateway = container "API Gateway" "Single authenticated entry point for browser clients and external integrations." "Azure API Management" "Gateway,Microsoft Azure - API Management Services"

  aquariumService = container "Aquarium Service" "Manages tanks, aquarium configuration, parameter definitions and current state." ".NET 10 Web API" "Service"
  trackingService = container "Tracking Service" "Records history; receives authorised photo binaries and enforces 5242880-byte file limit before Blob persistence; registers photo processing." ".NET 10 Web API" "Service"
  advisorService = container "Advisor Service" "Produces maintenance advice from aquarium measurements, events and relevant reference knowledge." ".NET 10 Web API / Azure AI" "Service"

  eventProcessor = container "Event Processor" "Existing non-photo background-work candidate; broader ownership remains under review." ".NET 10 Worker / Azure Functions" "Service"
  photoProcessor = container "Tracking Photo Worker" "Validates originals; creates cropped 400x400 WebP thumbnails and padded 1200x800 WebP heroes; retains originals for future processing." ".NET Worker / Azure Functions - hosting tier TBD" "Service"

  sqlDb = container "Aquarium SQL Database" "Stores transactional aquarium and configuration data." "Azure SQL" "Database,Infra,Microsoft Azure - SQL Database"
  cosmosDb = container "Parameter Event Store" "Stores parameter measurements, observations and historical event-oriented data." "Azure Cosmos DB" "Database,Infra,Microsoft Azure - Azure Cosmos DB"
  serviceBus = container "Message Broker" "Provides asynchronous communication between application services and background processors." "Azure Service Bus" "Infra,Messaging,Microsoft Azure - Service Bus"
  blobStorage = container "Photo Storage" "Private retained originals plus 400x400 cropped WebP thumbnails and 1200x800 padded WebP heroes. No AI image context." "Azure Blob Storage" "Database,Infra,Microsoft Azure - Storage Accounts"

  advisorDb = container "Advisor PostgreSQL Database" "Advisor-owned advice jobs, results, quotas, submitted parameter snapshots and curated passages, metadata and embeddings; replaces proposed Advisor SQL and AI Search." "Azure Database for PostgreSQL Flexible Server / pgvector" "Database,Infra"
  appInsights = container "Observability" "Application telemetry, distributed tracing, metrics and diagnostics." "Azure Application Insights / Log Analytics" "Infra,Microsoft Azure - Application Insights"
}

entra = softwareSystem "Microsoft Entra External ID" "Identity provider for customer authentication and application access." "External,Identity,Microsoft Azure - Azure Active Directory"
stripe = softwareSystem "Stripe" "External payment provider for subscription billing." "External"
