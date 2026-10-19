aquariumOwner -> parameterPilot.web "Uses" "HTTPS"
operator -> parameterPilot.web "Operates" "HTTPS"

parameterPilot.web -> parameterPilot.apiGateway "Calls" "HTTPS/JSON"

parameterPilot.apiGateway -> entra "Authenticates users" "OIDC/OAuth 2.0"
parameterPilot.apiGateway -> parameterPilot.aquariumService "Routes aquarium requests" "HTTPS/JSON"
parameterPilot.apiGateway -> parameterPilot.trackingService "Routes tracking requests" "HTTPS/JSON"
parameterPilot.apiGateway -> parameterPilot.advisorService "Routes advice requests" "HTTPS/JSON"

parameterPilot.aquariumService -> parameterPilot.sqlDb "Reads/writes aquarium data"
parameterPilot.aquariumService -> parameterPilot.serviceBus "Publishes aquarium events"

parameterPilot.trackingService -> parameterPilot.cosmosDb "Reads/writes measurements and events"
parameterPilot.trackingService -> parameterPilot.serviceBus "Publishes parameter events"
parameterPilot.trackingService -> parameterPilot.apiGateway "Returns trend data" "HTTPS/JSON"

parameterPilot.advisorService -> parameterPilot.cosmosDb "Reads historical measurements"
parameterPilot.advisorService -> parameterPilot.advisorDb "Stores jobs/results/quotas/input snapshots; retrieves curated passages using pgvector"
parameterPilot.advisorService -> parameterPilot.serviceBus "Publishes advice processing events"
parameterPilot.advisorService -> parameterPilot.apiGateway "Returns maintenance advice" "HTTPS/JSON"

parameterPilot.eventProcessor -> parameterPilot.serviceBus "Consumes asynchronous events"
parameterPilot.serviceBus -> parameterPilot.eventProcessor "Delivers asynchronous events"
parameterPilot.eventProcessor -> parameterPilot.cosmosDb "Processes event data"
parameterPilot.eventProcessor -> parameterPilot.sqlDb "Updates derived state"
parameterPilot.photoProcessor -> parameterPilot.serviceBus "Consumes registered photo-processing work"
parameterPilot.serviceBus -> parameterPilot.photoProcessor "Delivers photo-processing work"
parameterPilot.photoProcessor -> parameterPilot.blobStorage "Reads private original; writes cropped thumbnail and padded hero WebP"
parameterPilot.photoProcessor -> parameterPilot.cosmosDb "Updates Tracking-owned photo processing status and derivative metadata"
parameterPilot.photoProcessor -> parameterPilot.appInsights "Sends photo processing telemetry"

parameterPilot.trackingService -> parameterPilot.blobStorage "Saves private within-limit original after bounded upload validation" "HTTPS / managed identity"

parameterPilot.apiGateway -> stripe "Handles subscription billing integration" "HTTPS"

parameterPilot.aquariumService -> parameterPilot.appInsights "Sends telemetry"
parameterPilot.trackingService -> parameterPilot.appInsights "Sends telemetry"
parameterPilot.advisorService -> parameterPilot.appInsights "Sends telemetry"
parameterPilot.eventProcessor -> parameterPilot.appInsights "Sends telemetry"
