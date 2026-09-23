deploymentEnvironment "Azure" {
  azure = deploymentNode "Microsoft Azure" "Azure subscription" {
    resourceGroup = deploymentNode "Parameter Pilot Resource Group" "Azure resources for Parameter Pilot" {

      appServices = deploymentNode "Azure App Service" "Managed Linux App Service hosting" {
        tags "Microsoft Azure - App Services"
        webApp = deploymentNode "Web Application" "Azure App Service" {
          containerInstance parameterPilot.web
        }

        apiGateway = deploymentNode "API Gateway" "Azure API Management" {
          tags "Microsoft Azure - API Management Services"
          containerInstance parameterPilot.apiGateway
        }

        aquariumApp = deploymentNode "Aquarium Service" "Azure App Service" {
          containerInstance parameterPilot.aquariumService
        }

        trackingApp = deploymentNode "Tracking Service" "Azure App Service" {
          containerInstance parameterPilot.trackingService
        }

        advisorApp = deploymentNode "Advisor Service" "Azure App Service" {
          containerInstance parameterPilot.advisorService
        }
      }

      functions = deploymentNode "Azure Functions" "Serverless background processing" {
        tags "Microsoft Azure - Function Apps"
        processor = deploymentNode "Event Processor" "Azure Functions isolated worker" {
          containerInstance parameterPilot.eventProcessor
        }
      }

      data = deploymentNode "Data Services" "Managed Azure data services" {
        containerInstance parameterPilot.sqlDb
        containerInstance parameterPilot.cosmosDb
        containerInstance parameterPilot.blobStorage
      }

      messaging = deploymentNode "Messaging" "Managed messaging" {
        containerInstance parameterPilot.serviceBus
      }

      ai = deploymentNode "AI Services" "Managed AI services" {
        containerInstance parameterPilot.aiSearch
      }

      observability = deploymentNode "Observability" "Azure Monitor" {
        containerInstance parameterPilot.appInsights
      }
    }
  }
}
