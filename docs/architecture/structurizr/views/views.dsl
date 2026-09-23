systemContext parameterPilot "SystemContext" {
  include *
  autoLayout lr
  title "System Context - Parameter Pilot"
}

container parameterPilot "Containers" {
  include *
  autoLayout lr
  title "Container View - Parameter Pilot"
}

dynamic parameterPilot "RecordParameter" {
  title "Dynamic - Record aquarium parameter"

  aquariumOwner -> parameterPilot.web "1. Records a parameter measurement"
  parameterPilot.web -> parameterPilot.apiGateway "2. POST measurement"
  parameterPilot.apiGateway -> parameterPilot.trackingService "3. Submit measurement"
  parameterPilot.trackingService -> parameterPilot.cosmosDb "4. Store measurement"
  parameterPilot.trackingService -> parameterPilot.serviceBus "5. Publish ParameterRecorded"
  parameterPilot.serviceBus -> parameterPilot.eventProcessor "6. Consume event"
  parameterPilot.eventProcessor -> parameterPilot.appInsights "7. Record telemetry"
}

dynamic parameterPilot "TrendAnalysis" {
  title "Dynamic - View parameter trends"

  aquariumOwner -> parameterPilot.web "1. Opens trend view"
  parameterPilot.web -> parameterPilot.apiGateway "2. Request historical measurements"
  parameterPilot.apiGateway -> parameterPilot.trackingService "3. Query measurements"
  parameterPilot.trackingService -> parameterPilot.cosmosDb "4. Read historical data"
  parameterPilot.cosmosDb -> parameterPilot.trackingService "5. Return measurements"
  parameterPilot.trackingService -> parameterPilot.apiGateway "6. Return trend data"
  parameterPilot.apiGateway -> parameterPilot.web "7. Return trend data"
}

dynamic parameterPilot "MaintenanceAdvice" {
  title "Dynamic - Generate maintenance advice"

  aquariumOwner -> parameterPilot.web "1. Requests maintenance advice"
  parameterPilot.web -> parameterPilot.apiGateway "2. Request advice"
  parameterPilot.apiGateway -> parameterPilot.advisorService "3. Generate advice"
  parameterPilot.advisorService -> parameterPilot.cosmosDb "4. Read recent measurements"
  parameterPilot.advisorService -> parameterPilot.aiSearch "5. Retrieve relevant reference knowledge"
  parameterPilot.aiSearch -> parameterPilot.advisorService "6. Return grounded knowledge"
  parameterPilot.advisorService -> parameterPilot.apiGateway "7. Return maintenance advice"
  parameterPilot.apiGateway -> parameterPilot.web "8. Return maintenance advice"
}

dynamic parameterPilot "PhotoUpload" {
  title "Dynamic - Upload aquarium photo"

  aquariumOwner -> parameterPilot.web "1. Selects aquarium photo"
  parameterPilot.web -> parameterPilot.blobStorage "2. Upload photo"
  parameterPilot.web -> parameterPilot.apiGateway "3. Record photo metadata"
  parameterPilot.apiGateway -> parameterPilot.aquariumService "4. Save metadata"
  parameterPilot.aquariumService -> parameterPilot.sqlDb "5. Persist metadata"
  parameterPilot.aquariumService -> parameterPilot.serviceBus "6. Publish PhotoUploaded"
  parameterPilot.serviceBus -> parameterPilot.eventProcessor "7. Process event"
}

deployment parameterPilot "Azure" {
  include *
  autoLayout lr
  title "Deployment - Azure"
}
