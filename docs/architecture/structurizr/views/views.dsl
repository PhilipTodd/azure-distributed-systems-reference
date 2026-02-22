systemContext platform "SystemContext" {
  include *
  autoLayout lr
  title "System Context - Reference Platform"
}

container platform "Containers" {
  include *
  autoLayout lr
  title "Container View - 3 Microservices on Azure"
}

dynamic platform "OrderFlow" {
  title "Dynamic - Order → Payment flow"

  customer -> platform.web "1. Uses"
  platform.web -> platform.apiGateway "2. Create order"
  platform.apiGateway -> platform.orderApi "3. POST /orders"
  platform.orderApi -> platform.ordersDb "4. Save order"
  platform.orderApi -> platform.serviceBus "5. Publish OrderCreated"
  platform.paymentApi -> platform.serviceBus "6. Consume OrderCreated"
  platform.paymentApi -> paymentProvider "7. Charge"
  platform.paymentApi -> platform.paymentsDb "8. Persist payment"
}

dynamic platform "BrowseToOrder" {
  title "Dynamic - Browse catalog → place order"

  customer -> platform.web "1. Opens app"
  platform.web -> platform.apiGateway "2. Browse catalog"
  platform.apiGateway -> platform.catalogApi "3. GET /products"
  platform.catalogApi -> platform.catalogDb "4. Read products"
  platform.apiGateway -> platform.orderApi "5. POST /orders"
  platform.orderApi -> platform.ordersDb "6. Save order"
  platform.orderApi -> platform.serviceBus "7. Publish OrderCreated"
}

dynamic platform "CancelToRefund" {
  title "Dynamic - Cancel order → refund"

  customer -> platform.web "1. Requests cancellation"
  platform.web -> platform.apiGateway "2. Cancel order"
  platform.apiGateway -> platform.orderApi "3. POST /orders/{id}/cancel"
  platform.orderApi -> platform.ordersDb "4. Mark order as Cancelled"
  platform.orderApi -> platform.serviceBus "5. Publish OrderCancelled"

  platform.paymentApi -> platform.serviceBus "6. Consume OrderCancelled"
  platform.paymentApi -> paymentProvider "7. Refund"
  platform.paymentApi -> platform.paymentsDb "8. Persist refund result"
}

deployment platform "Azure" {
  include *
  // autoLayout lr
  title "Deployment - Azure Container Apps"
}
