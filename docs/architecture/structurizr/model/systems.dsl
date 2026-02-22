platform = softwareSystem "Reference Platform" "3 microservices hosted on Azure Container Apps." "System" {

  web = container "Web Frontend" "Browser-based UI." "Angular" "Web"
  apiGateway = container "API Gateway / BFF" "Single entry point for clients; routes to services." "YARP / APIM (logical)" "Gateway"

  orderApi = container "Order Service" "Manages orders (create/cancel/status)." ".NET Web API" "Service"
  catalogApi = container "Catalog Service" "Products and pricing." ".NET Web API" "Service"
  paymentApi = container "Payment Service" "Payment workflow + integration to provider." ".NET Worker/Web API" "Service"

  serviceBus = container "Message Broker" "Async messaging between services." "Azure Service Bus" "Infra,Messaging"

  ordersDb = container "Orders DB" "Stores orders." "Azure SQL" "Database,Infra"
  catalogDb = container "Catalog DB" "Stores catalog data." "Azure SQL" "Database,Infra"
  paymentsDb = container "Payments DB" "Stores payment records." "Azure SQL" "Database,Infra"
}

entraId = softwareSystem "Microsoft Entra ID" "OAuth2/OIDC identity provider." "External,Identity"
paymentProvider = softwareSystem "Payment Provider" "External payment processor." "External"
