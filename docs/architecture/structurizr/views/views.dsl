systemContext parameterPilot "SystemContext" {
  include *
  autoLayout lr
  title "System Context - Parameter Pilot"
}

// Service-focused views of one canonical model, not separate service models.
// Observability is intentionally omitted; shared infrastructure is repeated by reference.
container parameterPilot "AquariumContainers" {
  include parameterPilot.web parameterPilot.apiGateway parameterPilot.aquariumService parameterPilot.aquariumWorker parameterPilot.sqlDb parameterPilot.serviceBus
  title "Containers - Aquarium Service"
  description "Aquarium API commits owned state plus outbox in schema Aquarium within shared ReferenceProjectsDb synchronously. Aquarium Async Worker relays pending outbox messages to the shared Service Bus namespace."
}

container parameterPilot "TrackingContainers" {
  include parameterPilot.web parameterPilot.apiGateway parameterPilot.trackingService parameterPilot.trackingWorker parameterPilot.cosmosDb parameterPilot.blobStorage parameterPilot.serviceBus parameterPilot.aquariumService
  title "Containers - Tracking Service"
  description "Tracking API commits history plus outbox in one /tankId partition in the same Tracking container in shared ReferenceProjects; Tracking Async Worker publishes messages and processes photos. Aquarium API supplies one authorised batch of definition revisions/units/input rules per new panel; failures save nothing."
}

container parameterPilot "AdvisorContainers" {
  include parameterPilot.web parameterPilot.apiGateway parameterPilot.advisorService parameterPilot.advisorWorker parameterPilot.advisorDb parameterPilot.serviceBus parameterPilot.aquariumService parameterPilot.trackingService parameterPilot.foundry
  title "Containers - Advisor Service"
  description "Advisor API commits job/quota plus PostgreSQL outbox. Advisor Async Worker relays/consumes advice commands, retrieves authorised context, calls Foundry and stores result/completion outbox."
}

dynamic parameterPilot "CustomerIdentity" {
  title "Dynamic - Customer sign-in and authorised tank access"
  description "Accepted ADR-009. Customer and workload token contracts remain distinct; exact scopes/roles/delegation are TBD. No live identity setup is implied."
  aquariumOwner -> parameterPilot.web "1. Start sign-in"
  parameterPilot.web -> entra "2. Authorisation code + PKCE; obtain API access token"
  parameterPilot.web -> parameterPilot.apiGateway "3. Send API request with access token, not ID token"
  parameterPilot.apiGateway -> parameterPilot.trackingService "4. APIM validates token; Tracking independently validates token/permissions"
  parameterPilot.trackingService -> parameterPilot.aquariumService "5. Workload authentication plus verified actor/tank context; authorise access"
  parameterPilot.aquariumService -> parameterPilot.sqlDb "6. Resolve trusted identity to internal user and single-owner tank"
  parameterPilot.trackingService -> parameterPilot.cosmosDb "7. Only if authorised, read owned tank history"
  parameterPilot.trackingService -> parameterPilot.apiGateway "8. Return allowed data; fail closed if required context unavailable"
  parameterPilot.apiGateway -> parameterPilot.web "9. Present authorised result or safe error"
}

dynamic parameterPilot "AquariumOutbox" {
  title "Outbox - Aquarium tank creation"
  description "SQL state and outbox commit atomically. Publication is outside that transaction; send then crash can republish the same message ID."
  parameterPilot.web -> parameterPilot.apiGateway "1. POST tank"
  parameterPilot.apiGateway -> parameterPilot.aquariumService "2. Authorise and validate"
  parameterPilot.aquariumService -> parameterPilot.sqlDb "3. COMMIT tank + ownership + TankCreated outbox in one SQL transaction"
  parameterPilot.aquariumService -> parameterPilot.apiGateway "4. Return 201 after durable commit; broker can be unavailable"
  parameterPilot.aquariumWorker -> parameterPilot.sqlDb "5. Relay function reads pending outbox"
  parameterPilot.aquariumWorker -> parameterPilot.serviceBus "6. Publish TankCreated to Aquarium events topic; stable event ID"
  parameterPilot.aquariumWorker -> parameterPilot.sqlDb "7. Record dispatch only after broker acceptance; retry may duplicate"
}

dynamic parameterPilot "TrackingOutbox" {
  title "Outbox - Tracking measurement recording"
  description "One Aquarium rule/eligibility batch before an all-or-nothing local commit. Stale revision or unavailable validation saves neither panel nor outbox. Accepted /tankId partition; state and outbox must share the same container."
  parameterPilot.apiGateway -> parameterPilot.trackingService "1. Submit panel with definition IDs/revisions, values and units"
  parameterPilot.trackingService -> parameterPilot.aquariumService "2. One batch: authorise tank and retrieve selected active definitions/revisions/units/input rules"
  parameterPilot.trackingService -> parameterPilot.cosmosDb "3. After trusted validation, COMMIT panel + idempotency + outbox in one partition"
  parameterPilot.trackingService -> parameterPilot.apiGateway "4. Confirm saved; stale rules/unavailable Aquarium instead return actionable error with no write"
  parameterPilot.trackingWorker -> parameterPilot.cosmosDb "5. Relay reads pending outbox"
  parameterPilot.trackingWorker -> parameterPilot.serviceBus "6. Publish MeasurementPanelRecorded to Tracking events topic"
  parameterPilot.trackingWorker -> parameterPilot.cosmosDb "7. Record broker acceptance; duplicates remain possible"
}

dynamic parameterPilot "AdvisorOutbox" {
  title "Outbox - Advisor request and completion"
  description "Two local PostgreSQL transactions surround external work. Outbox relay and command processing are different functions in the same worker app; no exactly-once inference claim."
  parameterPilot.apiGateway -> parameterPilot.advisorService "1. Submit authorised advice request"
  parameterPilot.advisorService -> parameterPilot.advisorDb "2. COMMIT job + quota reservation + GenerateAdvice outbox"
  parameterPilot.advisorService -> parameterPilot.apiGateway "3. Return 202 and job Location after commit"
  parameterPilot.advisorWorker -> parameterPilot.advisorDb "4. Relay reads pending GenerateAdvice command"
  parameterPilot.advisorWorker -> parameterPilot.serviceBus "5. Send stable command ID to Advisor advice queue"
  parameterPilot.advisorWorker -> parameterPilot.advisorDb "6. Record dispatch after broker acceptance"
  parameterPilot.serviceBus -> parameterPilot.advisorWorker "7. Advice handler receives command; idempotent lease"
  parameterPilot.advisorWorker -> parameterPilot.aquariumService "8. Authorised profile and entitlement"
  parameterPilot.advisorWorker -> parameterPilot.trackingService "9. Authorised reading/history context"
  parameterPilot.advisorWorker -> parameterPilot.advisorDb "10. Save submitted-input snapshot; retrieve pgvector references"
  parameterPilot.advisorWorker -> parameterPilot.foundry "11. Request text inference; no photos"
  parameterPilot.advisorWorker -> parameterPilot.advisorDb "12. COMMIT result + terminal job + quota settlement + AdviceCompleted outbox"
  parameterPilot.advisorWorker -> parameterPilot.advisorDb "13. Relay reads completion outbox"
  parameterPilot.advisorWorker -> parameterPilot.serviceBus "14. Publish AdviceCompleted to Advisor events topic"
  parameterPilot.advisorWorker -> parameterPilot.advisorDb "15. Record completion dispatch after broker acceptance"
}

dynamic parameterPilot "RecordParameter" {
  title "Dynamic - Batched rule validation, measurement panel commit and outbox publication"
  description "UI retains input on stale-definition or Aquarium-unavailable errors; no new panel/outbox is saved on validation failure."
  aquariumOwner -> parameterPilot.web "1. Open measurement entry for tank"
  parameterPilot.web -> parameterPilot.apiGateway "2. Request tank-selected definitions/units/revisions"
  parameterPilot.apiGateway -> parameterPilot.aquariumService "3. Get authorised entry configuration"
  parameterPilot.aquariumService -> parameterPilot.sqlDb "4. Read selected GUID definitions and scientific revisions"
  parameterPilot.web -> parameterPilot.apiGateway "5. Submit panel with IDs/revisions, values, units and measured time"
  parameterPilot.apiGateway -> parameterPilot.trackingService "6. Validate shape/authentication"
  parameterPilot.trackingService -> parameterPilot.aquariumService "7. Batch all references once: tank eligibility, active revisions, units and authoritative rules"
  parameterPilot.trackingService -> parameterPilot.cosmosDb "8. If complete panel validates, atomically save panel/idempotency/outbox"
  parameterPilot.trackingService -> parameterPilot.apiGateway "9. Return 201 only after durable commit; invalid/stale/unavailable means no new save"
  parameterPilot.apiGateway -> parameterPilot.web "10. Confirm saved, or preserve input and offer refresh/retry"
  parameterPilot.trackingWorker -> parameterPilot.cosmosDb "11. Relay function reads persisted outbox asynchronously"
  parameterPilot.trackingWorker -> parameterPilot.serviceBus "12. Publish MeasurementPanelRecorded; duplicates possible"
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
  title "Dynamic - Registered advice job processed by Advisor Async Worker"
  aquariumOwner -> parameterPilot.web "1. Request advice"
  parameterPilot.web -> parameterPilot.apiGateway "2. POST advice request"
  parameterPilot.apiGateway -> parameterPilot.advisorService "3. Authorise request and entitlement"
  parameterPilot.advisorService -> parameterPilot.advisorDb "4. Commit job/quota reservation/outbox"
  parameterPilot.advisorService -> parameterPilot.apiGateway "5. Return 202 and job Location"
  parameterPilot.advisorWorker -> parameterPilot.advisorDb "6. Relay persisted GenerateAdvice command"
  parameterPilot.advisorWorker -> parameterPilot.serviceBus "7. Send command to Advisor queue"
  parameterPilot.serviceBus -> parameterPilot.advisorWorker "8. Advice function receives command; claim lease idempotently"
  parameterPilot.advisorWorker -> parameterPilot.aquariumService "9. Get scoped profile/entitlement"
  parameterPilot.advisorWorker -> parameterPilot.trackingService "10. Get scoped history via owner API; no direct Cosmos read"
  parameterPilot.advisorWorker -> parameterPilot.advisorDb "11. Preserve submitted context; retrieve curated passages with pgvector"
  parameterPilot.advisorWorker -> parameterPilot.foundry "12. Infer text advice without photos"
  parameterPilot.advisorWorker -> parameterPilot.advisorDb "13. Validate/store result, settle quota and write completion outbox"
}

dynamic parameterPilot "PhotoUpload" {
  title "Dynamic - Upload via Tracking and generate WebP images"

  aquariumOwner -> parameterPilot.web "1. Select photo; UI rejects above 5242880 bytes"
  parameterPilot.web -> parameterPilot.apiGateway "2. Authenticated binary upload; no browser Blob SAS"
  parameterPilot.apiGateway -> parameterPilot.trackingService "3. Stream upload; enforce actual 5242880-byte file cap; 413 on excess"
  parameterPilot.trackingService -> parameterPilot.blobStorage "4. Save within-limit private original after bounded validation"
  parameterPilot.trackingService -> parameterPilot.cosmosDb "5. Register uploaded metadata and durable processing work"
  parameterPilot.trackingWorker -> parameterPilot.cosmosDb "6. Relay durable photo-processing command from outbox"
  parameterPilot.trackingWorker -> parameterPilot.serviceBus "7. Publish ProcessPhoto command to Tracking queue"
  parameterPilot.serviceBus -> parameterPilot.trackingWorker "8. Tracking photo function receives command idempotently"
  parameterPilot.trackingWorker -> parameterPilot.blobStorage "9. Validate original; create cropped 400x400 thumbnail and padded 1200x800 hero WebP; retain original"
  parameterPilot.trackingWorker -> parameterPilot.cosmosDb "10. Mark Ready only when both derivatives and metadata are durable; completion outbox"
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
  title "Deployment - Azure"
}
