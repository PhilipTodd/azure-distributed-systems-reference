customer -> platform.web "Uses" "HTTPS"
platform.web -> platform.apiGateway "Calls" "HTTPS/JSON"

platform.apiGateway -> entraId "Authenticates" "OIDC"
platform.apiGateway -> platform.orderApi "Routes" "HTTPS/JSON"
platform.apiGateway -> platform.catalogApi "Routes" "HTTPS/JSON"
platform.apiGateway -> platform.paymentApi "Routes" "HTTPS/JSON"

platform.orderApi -> platform.ordersDb "Reads/Writes"
platform.catalogApi -> platform.catalogDb "Reads/Writes"
platform.paymentApi -> platform.paymentsDb "Reads/Writes"

platform.orderApi -> platform.serviceBus "Publishes OrderCreated"
platform.paymentApi -> platform.serviceBus "Consumes OrderCreated"

platform.paymentApi -> paymentProvider "Charges" "HTTPS"
