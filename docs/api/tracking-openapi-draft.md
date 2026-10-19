# Tracking OpenAPI draft

Version: 0.1 | Date: 8 October 2026 | Status: Draft; not independently validated

Concrete core-operation excerpt. Extract to YAML and validate before implementation. Cross-field checks reject duplicate definition IDs, retired definitions and incompatible units. No complete product OpenAPI is claimed.

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
        measuredAt: { type: string, format: date-time }
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
