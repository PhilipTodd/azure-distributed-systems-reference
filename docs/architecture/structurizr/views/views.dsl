systemContext parameterPilot "SystemContext" {
  include *
  autoLayout lr
  title "System Context - Parameter Pilot"
}

container parameterPilot "Containers" {
  include *
  // Observability is documented separately; omit it and its links for readability.
  exclude parameterPilot.appInsights
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
  parameterPilot.advisorService -> parameterPilot.advisorDb "5. Store submitted parameter snapshot; retrieve curated passages with pgvector"
  parameterPilot.advisorDb -> parameterPilot.advisorService "6. Return reference passages and metadata; no photo context"
  parameterPilot.advisorService -> parameterPilot.apiGateway "7. Return maintenance advice"
  parameterPilot.apiGateway -> parameterPilot.web "8. Return maintenance advice"
}

dynamic parameterPilot "PhotoUpload" {
  title "Dynamic - Upload via Tracking and generate WebP images"

  aquariumOwner -> parameterPilot.web "1. Select photo; UI rejects above 5242880 bytes"
  parameterPilot.web -> parameterPilot.apiGateway "2. Authenticated binary upload; no browser Blob SAS"
  parameterPilot.apiGateway -> parameterPilot.trackingService "3. Stream upload; enforce actual 5242880-byte file cap; 413 on excess"
  parameterPilot.trackingService -> parameterPilot.blobStorage "4. Save within-limit private original after bounded validation"
  parameterPilot.trackingService -> parameterPilot.cosmosDb "5. Register uploaded metadata and durable processing work"
  parameterPilot.trackingService -> parameterPilot.serviceBus "6. Publish registered photo-processing work"
  parameterPilot.serviceBus -> parameterPilot.photoProcessor "7. Deliver work idempotently"
  parameterPilot.photoProcessor -> parameterPilot.blobStorage "8. Validate original; create cropped 400x400 thumbnail and padded 1200x800 hero WebP; retain original"
  parameterPilot.photoProcessor -> parameterPilot.cosmosDb "9. Mark Ready only when both derivatives and metadata are durable"
}

dynamic parameterPilot "AdviceHistory" {
  title "Dynamic - Browse historical advice and submitted parameters"

  aquariumOwner -> parameterPilot.web "1. Scroll Advice history and select an item"
  parameterPilot.web -> parameterPilot.apiGateway "2. Request owner-scoped history page or detail"
  parameterPilot.apiGateway -> parameterPilot.advisorService "3. Validate access and query history"
  parameterPilot.advisorService -> parameterPilot.advisorDb "4. Read historic advice and original submitted parameter snapshot"
  parameterPilot.advisorService -> parameterPilot.apiGateway "5. Return history page or selected advice with submitted values"
  parameterPilot.apiGateway -> parameterPilot.web "6. Display advice and original values; not current readings"
}


deployment parameterPilot "Azure" {
  include *
  autoLayout lr
  title "Deployment - Azure"
}
