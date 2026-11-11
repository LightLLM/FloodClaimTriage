# API Reference

Base URL: `http://localhost:8000/api/v1` (development)

All endpoints except `/health` require authentication via JWT bearer token.

## Authentication

### POST /auth/login

Authenticate user and receive JWT tokens.

**Request**:
```json
{
  "email": "analyst@example.com",
  "password": "password123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "analyst@example.com",
  "full_name": "Jane Analyst",
  "role": "analyst"
}
```

**Errors**:
- 401: Invalid credentials
- 401: Account inactive

### POST /auth/refresh

Refresh access token using refresh token.

**Request**:
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### GET /auth/me

Get current authenticated user information.

**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "email": "analyst@example.com",
  "full_name": "Jane Analyst",
  "role": "analyst",
  "is_active": true
}
```

## Events

### GET /events

List all events with summary statistics.

**Query Parameters**:
- `skip` (int, default: 0): Pagination offset
- `limit` (int, default: 100): Max results

**Response** (200 OK):
```json
[
  {
    "id": "event-uuid",
    "event_type": "flood",
    "name": "Texas Flood August 2023",
    "event_date": "2023-08-15",
    "geometry": null,
    "stac_collection_id": "sentinel2-floods-tx-2023",
    "status": "active",
    "created_at": "2023-08-16T10:00:00Z",
    "property_count": 10000,
    "scored_count": 9850
  }
]
```

### POST /events

Create a new event.

**Required Role**: `admin` or `analyst`

**Request**:
```json
{
  "event_type": "flood",
  "name": "Texas Flood August 2023",
  "event_date": "2023-08-15",
  "stac_collection_id": "sentinel2-floods-tx-2023"
}
```

**Response** (201 Created):
```json
{
  "id": "event-uuid",
  "event_type": "flood",
  "name": "Texas Flood August 2023",
  "event_date": "2023-08-15",
  "geometry": null,
  "stac_collection_id": "sentinel2-floods-tx-2023",
  "status": "draft",
  "created_at": "2023-08-16T10:00:00Z"
}
```

### GET /events/{event_id}

Get detailed event information.

**Response** (200 OK):
```json
{
  "id": "event-uuid",
  "event_type": "flood",
  "name": "Texas Flood August 2023",
  "event_date": "2023-08-15",
  "geometry": null,
  "stac_collection_id": "sentinel2-floods-tx-2023",
  "status": "active",
  "created_at": "2023-08-16T10:00:00Z",
  "property_count": 10000,
  "scored_count": 9850
}
```

### POST /events/{event_id}/score

Trigger scoring for all properties in an event.

**Required Role**: `admin` or `analyst`

**Query Parameters**:
- `force_rescore` (bool, default: false): Re-score already scored properties

**Response** (200 OK):
```json
{
  "event_id": "event-uuid",
  "scored_count": 150,
  "skipped_count": 9700,
  "total_properties": 9850
}
```

## Properties

### GET /properties

List properties.

**Query Parameters**:
- `skip` (int, default: 0)
- `limit` (int, default: 100)

**Response** (200 OK):
```json
[
  {
    "id": "property-uuid",
    "external_property_id": "PROP-12345",
    "geometry": { "type": "Point", "coordinates": [-95.3698, 29.7604] },
    "address_hash": "a3b2c1...",
    "building_type": "residential",
    "exposure_value": 450000.00,
    "region": "TX",
    "data_source": "client_portfolio",
    "created_at": "2023-08-01T00:00:00Z",
    "updated_at": "2023-08-01T00:00:00Z"
  }
]
```

### GET /properties/{property_id}

Get property details.

**Response** (200 OK): Same schema as list item.

## Triage

### GET /events/{event_id}/triage

Get triage queue for an event with filtering and sorting.

**Query Parameters**:
- `priority` (string, optional): Filter by P1, P2, or P3
- `min_probability` (float, optional): Minimum damage probability (0-1)
- `skip` (int, default: 0)
- `limit` (int, default: 100)

**Response** (200 OK):
```json
[
  {
    "property_id": "property-uuid",
    "external_property_id": "PROP-12345",
    "geometry": { "type": "Point", "coordinates": [-95.3698, 29.7604] },
    "exposure_value": 450000.00,
    "damage_probability": 0.8523,
    "inspection_priority": "P1",
    "recommended_action": "Field inspection",
    "created_at": "2023-08-16T12:34:56Z"
  }
]
```

**Sorting**: Results ordered by priority (P1 → P2 → P3) then damage probability (high → low).

### GET /events/{event_id}/properties/{property_id}/evidence

Get detailed evidence for a property's score.

**Response** (200 OK):
```json
{
  "property_id": "property-uuid",
  "external_property_id": "PROP-12345",
  "score": {
    "id": "score-uuid",
    "damage_probability": 0.8523,
    "inspection_priority": "P1",
    "recommended_action": "Field inspection",
    "damage_confidence": "high",
    "model_version": "v0.1-rule-based",
    "created_at": "2023-08-16T12:34:56Z"
  },
  "evidence": {
    "flood_extent_signal": 1.0,
    "proximity_signal": 0.95,
    "rainfall_signal": 0.88,
    "river_stage_signal": 1.0,
    "optical_change_signal": 0.72,
    "elevation_signal": 0.60,
    "data_sources": {
      "sensor": "Sentinel-2",
      "stac_item": "sentinel2_20230815_tile32UQD",
      "weather": "NOAA NCEP Precipitation",
      "elevation": "USGS 3DEP 30m"
    },
    "confidence_factors": {
      "cloud_cover": "Clear imagery (quality: 0.95)",
      "data_completeness": "6/6 data sources available"
    }
  },
  "property_details": {
    "building_type": "residential",
    "exposure_value": 450000.00,
    "region": "TX"
  }
}
```

### POST /scores/{score_id}/review

Review and optionally override a score.

**Required Role**: `admin`, `analyst`, or `reviewer`

**Query Parameters**:
- `action` (string, required): `accept` or `override`
- `reason` (string, optional): Reason for action
- `new_priority` (string, optional): New priority if overriding (P1, P2, P3)

**Example**: Override to P2
```
POST /scores/{score_id}/review?action=override&new_priority=P2&reason=Local%20knowledge
```

**Response** (200 OK):
```json
{
  "score_id": "score-uuid",
  "action": "override",
  "updated_priority": "P2",
  "audit_event_id": "audit-uuid"
}
```

### GET /events/{event_id}/export.csv

Export triage queue as CSV.

**Response** (200 OK):
- Content-Type: `text/csv`
- Headers: `Content-Disposition: attachment; filename=triage-export-{event_name}.csv`

**CSV Format**:
```csv
property_id,external_property_id,damage_probability,inspection_priority,recommended_action,exposure_value,building_type,region,confidence,model_version
...
```

## Health

### GET /health

Health check endpoint (no authentication required).

**Response** (200 OK):
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "model_version": "v0.1-rule-based",
  "environment": "development"
}
```

## Error Responses

All errors return JSON with consistent structure:

**400 Bad Request**:
```json
{
  "detail": "Invalid priority value"
}
```

**401 Unauthorized**:
```json
{
  "detail": "Invalid token"
}
```

**403 Forbidden**:
```json
{
  "detail": "Insufficient permissions. Required roles: ['admin', 'analyst']"
}
```

**404 Not Found**:
```json
{
  "detail": "Event not found"
}
```

**422 Unprocessable Entity** (validation error):
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

## Rate Limiting

Not implemented in MVP. Production should implement:
- 100 requests/minute per user for read endpoints
- 20 requests/minute per user for write endpoints
- 10 requests/minute per IP for unauthenticated endpoints

## Pagination

Use `skip` and `limit` query parameters:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100, max: 1000)

Example:
```
GET /properties?skip=100&limit=50
```

## Timestamps

All timestamps are in ISO 8601 format with UTC timezone:
```
2023-08-16T12:34:56.789Z
```

## Interactive Documentation

FastAPI automatically generates interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
