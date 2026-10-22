parameterPilot = softwareSystem "Parameter Pilot" "Aquarium parameter tracking, trend analysis and AI-assisted maintenance advice." "System" {
  web = container "Web Application" "Browser-based Angular application for recording data and viewing trends and advice." "Angular 22 / strict TypeScript" "Web"

  apiGateway = container "API Gateway" "Single authenticated entry point for browser clients and external integrations." "Azure API Management" "Gateway,Microsoft Azure - API Management Services"

  aquariumService = container "Aquarium Service" "Owns tanks and SQL GUID parameter definitions/revisions/units/input rules; serves tank-selected definitions and batch validation context." "ASP.NET Core 10 / C# 14" "Service"
  trackingService = container "Tracking Service" "Records history; receives authorised photo binaries and enforces 5242880-byte file limit before Blob persistence; registers photo processing." "ASP.NET Core 10 / C# 14" "Service"
  advisorService = container "Advisor Service" "Produces maintenance advice from aquarium measurements, events and relevant reference knowledge." "ASP.NET Core 10 / C# 14 / Foundry" "Service"

  aquariumWorker = container "Aquarium Async Worker" "Aquarium-owned outbox publication and approved deferred tasks; accesses Aquarium SQL only." ".NET 10 isolated Azure Functions / shared plan (compatibility verification pending)" "Service"
  trackingWorker = container "Tracking Async Worker" "Tracking outbox and deferred tasks; photo validation and cropped 400x400 thumbnail/padded 1200x800 hero WebP; retains originals." ".NET 10 isolated Azure Functions / shared plan (compatibility verification pending)" "Service"
  advisorWorker = container "Advisor Async Worker" "Advisor-owned advice context, retrieval, inference, result persistence and outbox publication." ".NET 10 isolated Azure Functions / shared plan (compatibility verification pending)" "Service"

  sqlDb = container "Aquarium SQL Schema" "Aquarium-owned tables, outbox/inbox and migrations in schema Aquarium within platform-owned ReferenceProjectsDb; schema-scoped runtime access." "Azure SQL / Aquarium schema" "Database,Infra,Microsoft Azure - SQL Database"
  cosmosDb = container "Tracking History Store" "Tracking-owned containers in platform-owned ReferenceProjects database; partition key /tankId; state and outbox in same container/partition for atomicity." "Azure Cosmos DB" "Database,Infra,Microsoft Azure - Azure Cosmos DB"
  serviceBus = container "Message Broker" "One Service Bus namespace with separate service command queues and event topics/filtered subscriptions; not one shared consumer queue." "Azure Service Bus" "Infra,Messaging,Microsoft Azure - Service Bus"
  blobStorage = container "Photo Storage" "Private retained originals plus 400x400 cropped WebP thumbnails and 1200x800 padded WebP heroes. No AI image context." "Azure Blob Storage" "Database,Infra,Microsoft Azure - Storage Accounts"

  advisorDb = container "Advisor PostgreSQL Database" "Advisor-owned advice jobs, results, quotas, submitted parameter snapshots and curated passages, metadata and embeddings; replaces proposed Advisor SQL and AI Search." "Azure Database for PostgreSQL Flexible Server / pgvector" "Database,Infra"
  foundry = container "Model Inference" "Text advice inference; model/version/region remain subject to selection; no photo context." "Microsoft Foundry" "Infra"
  appInsights = container "Observability" "Application telemetry, distributed tracing, metrics and diagnostics." "Azure Application Insights / Log Analytics" "Infra,Microsoft Azure - Application Insights"
}

entra = softwareSystem "Microsoft Entra External ID" "Identity provider for customer authentication and application access." "External,Identity,Microsoft Azure - Azure Active Directory"
stripe = softwareSystem "Stripe" "External payment provider for subscription billing." "External"
