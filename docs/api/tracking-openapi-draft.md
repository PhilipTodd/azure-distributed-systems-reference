# Tracking OpenAPI draft

Version: 0.5 | Date: 21 October 2026 | Status: Draft; not independently validated

29 October readiness addition: the [candidate JSON Schema bundle](schemas/stage-2.schema.json) provides separate closed PanelCreate and Panel response shapes, ReadingInput and Problem, accepted under SPEC-02 on 29 October. The historical OpenAPI excerpt remains Draft. See [SPEC-02](../engineering/stage-2-readiness-specification.md#candidate-executable-contracts) for limits and semantic checks. Structural validation of that bundle does not validate the historical OpenAPI excerpt below; the excerpt remains Draft and must not be treated as a complete HTTP specification.

Accepted MEAS-07 field behaviour; executable OpenAPI excerpt still requires validation. Concrete core-operation excerpt. Extract to YAML and validate before implementation. Cross-field checks reject duplicate definition IDs, retired definitions and incompatible units. No complete product OpenAPI is claimed.

```yaml
openapi: 3.1.0
info:
  title: Parameter Pilot Tracking API
  version: 0.1.0
servers:
  - url: /api/v1
security:
  - bearerAuth: []
paths:
  /tanks/{tankId}/measurement-panels:
    post:
      operationId: createMeasurementPanel
      description: >-
        Retrieve authorised tank definitions and rules in one Aquarium API batch,
        validate the complete panel and reject stale revisions before local commit.
        Aquarium validation unavailability results in no panel or outbox write.
      parameters:
        - name: tankId
          in: path
          required: true
          schema: { type: string, format: uuid }
        - name: Idempotency-Key
          in: header
          required: true
          schema: { type: string, minLength: 16, maxLength: 128 }
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateMeasurementPanel'
      responses:
        '201':
          description: Panel durably recorded
          headers:
            Location:
              schema: { type: string }
            ETag:
              schema: { type: string }
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/MeasurementPanel'
        '400': { $ref: '#/components/responses/Problem' }
        '401': { $ref: '#/components/responses/Problem' }
        '403': { $ref: '#/components/responses/Problem' }
        '404': { $ref: '#/components/responses/Problem' }
        '409': { $ref: '#/components/responses/Problem' }
        '422': { $ref: '#/components/responses/Problem' }
        '429': { $ref: '#/components/responses/Problem' }
        '503': { $ref: '#/components/responses/Problem' }
components:
  securitySchemes:
    bearerAuth: { type: http, scheme: bearer, bearerFormat: JWT }
  responses:
    Problem:
      description: RFC 9457 problem response
      content:
        application/problem+json:
          schema: { $ref: '#/components/schemas/Problem' }
  schemas:
    CreateMeasurementPanel:
      type: object
      required: [measuredAt, readings]
      properties:
        measuredAt:
          type: string
          format: date-time
          description: Offset-bearing panel time; backdating allowed, at most five minutes ahead of server time.
        testMethod: { type: string, maxLength: 200 }
        notes: { type: string, maxLength: 4000 }
        readings:
          type: array
          minItems: 1
          maxItems: 50
          items: { $ref: '#/components/schemas/ReadingInput' }
    ReadingInput:
      type: object
      additionalProperties: false
      required: [parameterDefinitionId, definitionRevision, value, unitCode, qualifier]
      properties:
        parameterDefinitionId: { type: string, format: uuid }
        definitionRevision: { type: integer, minimum: 1 }
        value: { type: number }
        unitCode: { type: string, maxLength: 40 }
        qualifier:
          type: string
          enum: [exact, belowDetectionLimit, aboveDetectionLimit]
    MeasurementPanel:
      allOf:
        - $ref: '#/components/schemas/CreateMeasurementPanel'
        - type: object
          required: [id, tankId, recordedAt, revision]
          properties:
            id: { type: string, format: uuid }
            tankId: { type: string, format: uuid }
            recordedAt: { type: string, format: date-time }
            revision: { type: integer, minimum: 1 }
    Problem:
      type: object
      required: [type, title, status, code, traceId]
      properties:
        type: { type: string, format: uri }
        title: { type: string }
        status: { type: integer }
        detail: { type: string }
        instance: { type: string }
        code: { type: string }
        traceId: { type: string }
```

The shared input schema deliberately permits extension so the composed response schema accepts server fields. Production request validation must use a dedicated closed request schema or explicit allowed-field validation; do not copy a closed base into allOf and accidentally reject response fields.

## Accepted pre-commit validation — ADR-023

For a new submission Tracking directly requests one batch of authoritative definition revisions, allowed units/input rules and tank eligibility from Aquarium. Validate all readings before any panel/outbox write. Never trust browser rule objects. Stale revisions produce actionable rejection so UI refreshes definitions while preserving form input; Aquarium outage fails without persistence.

Accepted MEAS-08 mappings use 409/parameter-definition-revision-stale, 422 for invalid readings, and 503/measurement-validation-unavailable; existing response slots cover these, but full error extensions and internal batch schema remain draft. See [Aquarium validation contract](aquarium-validation-contract.md).

The request schema remains definition ID/revision/value/unit/qualifier; optional display/analyte snapshots were not accepted. Panel storage is accepted; Cosmos /tankId is accepted in ADR-005; shared container placement is accepted in ADR-024.

## Measurement-panel contract — accepted 21 October 2026

MEAS-07: measurement-panel submission identifies the tank in the route and checks ownership server-side. Require one offset-bearing measuredAt for the panel; backdating allowed; reject times more than five minutes ahead of server time. readings contains 1–50 entries, no duplicate parameterDefinitionId. Each entry requires definition GUID, positive definition revision, numeric value, explicit unitCode and qualifier (exact, belowDetectionLimit, aboveDetectionLimit). For detection-limit qualifiers the numeric value is the limit, not an exact measurement. Optional panel testMethod max 200 characters and notes max 4,000 characters.

Require an idempotency key: same authorised submission retry returns the original outcome without another panel. Conflicting payload follows the existing conflict policy. Server generates panel ID, recordedAt UTC and revision. Validate the complete panel through the accepted single Aquarium batch and local rules before atomic panel/idempotency/outbox persistence in the same Cosmos container/partition. No partial save. Profile completion, selected-definition eligibility and accepted explicit-unit/basis rules still apply. Exact executable schemas/error extensions and numeric precision/seed rules remain readiness work; no code or test execution performed.

## Submission errors and input preservation — accepted 21 October 2026

MEAS-08: use consistent safe error bodies with stable code, explanation, trace ID and field details where applicable. Accepted mappings: 400 malformed request; 401 missing/expired authentication; 403 missing API permission; 404 absent/inaccessible tank without owner disclosure; 409 stale definition revision or idempotency-key payload conflict (distinct codes); 422 invalid readings/time; 503 temporary Aquarium/OBO unavailability. Only temporary OBO/dependency availability failures map to 503; actual authentication/permission failures retain their appropriate 401/403 semantics. Invalid or unusable trusted dependency responses fail closed without claiming a saved panel.

UI retains input for same-user reauthentication/retry, subject to ID-10 clearing on account change/sign-out. Refresh stale definitions while preserving entered values for review; never auto-resubmit after rules change. Field validation saves nothing. Permission/inaccessible-tank responses explain failure safely without exposing neighbour data. Do not expose tokens, internal exceptions or private dependency payloads. Rate-limit and unexpected-error conventions remain applicable; the table is not an exhaustive HTTP contract. No application changes or executable schema validation performed.
