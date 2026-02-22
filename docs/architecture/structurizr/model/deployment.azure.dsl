deploymentEnvironment "Azure" {

  azure = deploymentNode "Microsoft Azure" "Azure subscription boundary" {

    rg = deploymentNode "Resource Group" "All resources for this environment" {

      acaEnv = deploymentNode "Container Apps Environment" "Azure Container Apps Environment" {

        webApp = deploymentNode "Web Frontend App" "Azure Container App" {
          containerInstance platform.web
        }

        gatewayApp = deploymentNode "API Gateway / BFF App" "Azure Container App" {
          containerInstance platform.apiGateway
        }

        orderApp = deploymentNode "Order Service App" "Azure Container App" {
          containerInstance platform.orderApi
        }

        catalogApp = deploymentNode "Catalog Service App" "Azure Container App" {
          containerInstance platform.catalogApi
        }

        paymentApp = deploymentNode "Payment Service App" "Azure Container App" {
          containerInstance platform.paymentApi
        }
      }

      messaging = deploymentNode "Messaging" "Managed messaging services" {
        containerInstance platform.serviceBus
      }

      data = deploymentNode "Data" "Managed databases" {
        containerInstance platform.ordersDb
        containerInstance platform.catalogDb
        containerInstance platform.paymentsDb
      }
    }
  }
}
