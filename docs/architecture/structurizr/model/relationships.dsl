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
parameterPilot.advisorService -> parameterPilot.aiSearch "Retrieves reference knowledge"
parameterPilot.advisorService -> parameterPilot.serviceBus "Publishes advice processing events"
parameterPilot.advisorService -> parameterPilot.apiGateway "Returns maintenance advice" "HTTPS/JSON"

parameterPilot.eventProcessor -> parameterPilot.serviceBus "Consumes asynchronous events"
parameterPilot.serviceBus -> parameterPilot.eventProcessor "Delivers asynchronous events"
parameterPilot.eventProcessor -> parameterPilot.cosmosDb "Processes event data"
parameterPilot.eventProcessor -> parameterPilot.sqlDb "Updates derived state"
parameterPilot.eventProcessor -> parameterPilot.blobStorage "Processes uploaded media"

parameterPilot.web -> parameterPilot.blobStorage "Uploads aquarium photos" "HTTPS"

parameterPilot.apiGateway -> stripe "Handles subscription billing integration" "HTTPS"

parameterPilot.aquariumService -> parameterPilot.appInsights "Sends telemetry"
parameterPilot.trackingService -> parameterPilot.appInsights "Sends telemetry"
parameterPilot.advisorService -> parameterPilot.appInsights "Sends telemetry"
parameterPilot.eventProcessor -> parameterPilot.appInsights "Sends telemetry"
