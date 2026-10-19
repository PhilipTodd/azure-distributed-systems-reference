# Event envelope and payload draft

Version: 0.1 | Date: 8 October 2026 | Status: Draft; extract/validate before implementation

Proposed CloudEvents-style JSON envelope. The body must identify event version, origin, subject, time and causation. Transport mapping and complete envelope schema remain readiness work.

```json
{
  "specversion": "1.0",
  "id": "7b55633c-4f83-46f0-8640-e4094f4d78f9",
  "source": "/parameter-pilot/tracking",
  "type": "com.parameterpilot.measurement-panel.recorded.v1",
  "subject": "tanks/11111111-1111-4111-8111-111111111111/panels/22222222-2222-4222-8222-222222222222",
  "time": "2026-10-08T03:20:00Z",
  "datacontenttype": "application/json",
  "correlationid": "44444444-4444-4444-8444-444444444444",
  "causationid": "55555555-5555-4555-8555-555555555555",
  "data": {
    "tankId": "11111111-1111-4111-8111-111111111111",
    "panelId": "22222222-2222-4222-8222-222222222222",
    "revision": 1,
    "measuredAt": "2026-10-08T03:15:00Z"
  }
}
```

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "MeasurementPanelRecordedV1Data",
  "type": "object",
  "required": ["tankId", "panelId", "revision", "measuredAt"],
  "properties": {
    "tankId": {"type": "string", "format": "uuid"},
    "panelId": {"type": "string", "format": "uuid"},
    "revision": {"type": "integer", "minimum": 1},
    "measuredAt": {"type": "string", "format": "date-time"}
  },
  "additionalProperties": true
}
```

Required validation cases: missing fields, invalid format, unknown additive field, incompatible version, duplicate delivery and stale entity revision. Do not treat format annotations as enforced unless validator settings enable them.
