deploymentEnvironment "Local" {
dockerHost = deploymentNode "Developer Machine" "Windows / WSL2" "Docker" {
  web_local = containerInstance web
  gw_local = containerInstance apiGateway
  order_local = containerInstance orderApi
  catalog_local = containerInstance catalogApi
  payment_local = containerInstance paymentApi
}
}

deploymentEnvironment "Azure" {
subscription = deploymentNode "Azure Subscription" "" "" {

  acaEnv = deploymentNode "Container Apps Environment" "Azure Container Apps" "ACA" {
	web_aca = containerInstance web
	gw_aca = containerInstance apiGateway
	order_aca = containerInstance orderApi
	catalog_aca = containerInstance catalogApi
	payment_aca = containerInstance paymentApi
  }

  data = deploymentNode "Data Services" "" "" {
	ordersDb_az = containerInstance ordersDb
	catalogDb_az = containerInstance catalogDb
	paymentsDb_az = containerInstance paymentsDb
	sb_az = containerInstance serviceBus
	blob_az = containerInstance blob
	obs_az = containerInstance observability
  }
}
}
