// Accepted Development only. Core/APIM/ACR existence is verified; app access/capacity remain gates.
deploymentEnvironment "Azure" {
  azure = deploymentNode "Microsoft Azure - Development" "Local/dev-only initial scope; no Test/Production resources implied" {
    resourceGroup = deploymentNode "Parameter Pilot Resource Group" "PP-owned hosting and service-isolated App Configuration/Key Vault instances; instance deployment deferred to PP Bicep under ADR-031" {
      webHosting = deploymentNode "Static Web Apps" "Angular hosting; only APIM used for browser API calls" {
        containerInstance parameterPilot.web
      }
      inference = deploymentNode "Inference Hosting" "Later Foundry allocation/model/region remain to be verified" {
        containerInstance parameterPilot.foundry
      }
    }
    sharedPlatform = deploymentNode "Shared Development Platform" "Shared compute/data/messaging/APIM/ACR/monitoring lifecycle; PP-exclusive configuration/vaults are application-owned" {
      sharedGateway = deploymentNode "Shared APIM" "Platform-owned instance; app APIs/policies; HTTPS browser entry; outbound addressing must support narrow backend rules" {
        containerInstance parameterPilot.apiGateway
      }
      sharedSql = deploymentNode "ReferenceProjectsDb" "Platform-owned SQL database and capacity" {
        aquariumSchema = deploymentNode "Aquarium schema" "Application-owned tables/migrations; schema-scoped runtime identities" {
          containerInstance parameterPilot.sqlDb
        }
      }
      sharedCosmos = deploymentNode "ReferenceProjects Cosmos database" "Platform-owned account/database/throughput" {
        trackingContainers = deploymentNode "Tracking-owned containers" "App-owned /tankId containers; state/outbox same container and partition" {
          containerInstance parameterPilot.cosmosDb
        }
      }
      sharedStorage = deploymentNode "Shared Blob Storage Account" "Platform-owned account; application private photo containers/lifecycle, introduced in photo stage" {
        containerInstance parameterPilot.blobStorage
      }
      sharedPostgres = deploymentNode "Shared PostgreSQL Flexible Server" "Platform capacity/extensions/backups; Advisor database/data in later AI stage" {
        containerInstance parameterPilot.advisorDb
      }
      sharedMessaging = deploymentNode "Shared Service Bus Namespace" "Platform namespace/SKU; application-owned queues/topics/subscriptions" {
        containerInstance parameterPilot.serviceBus
      }
      sharedMonitoring = deploymentNode "Shared Monitoring" "Platform App Insights/Log Analytics hosting and policy" {
        containerInstance parameterPilot.appInsights
      }
      sharedPlan = deploymentNode "Existing Shared Linux App Service Plan" "Shared API/Functions compute; verify OS/SKU/runtime/Always On/headroom; no independent compute scaling" {
        aquariumApp = deploymentNode "Aquarium API App" "Separate containerised App Service app/identity/configuration; restricted public HTTPS behind APIM" {
          containerInstance parameterPilot.aquariumService
        }
        trackingApp = deploymentNode "Tracking API App" "Separate containerised App Service app/identity/configuration; restricted public HTTPS behind APIM" {
          containerInstance parameterPilot.trackingService
        }
        advisorApp = deploymentNode "Advisor API App" "Later separate containerised App Service app/identity/configuration; restricted public HTTPS" {
          containerInstance parameterPilot.advisorService
        }
        aquariumFunctions = deploymentNode "Aquarium Function App" "Service-owned functions and managed identity" {
          containerInstance parameterPilot.aquariumWorker
        }
        trackingFunctions = deploymentNode "Tracking Function App" "Photo/outbox functions; bounded image concurrency" {
          containerInstance parameterPilot.trackingWorker
        }
        advisorFunctions = deploymentNode "Advisor Function App" "Later advice/outbox functions; bounded inference concurrency" {
          containerInstance parameterPilot.advisorWorker
        }
      }
    }
  }
}
