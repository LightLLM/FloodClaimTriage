# Data Model

## Overview

The Flood Claim Triage MVP uses a relational data model optimized for transactional consistency, audit trails, and geospatial queries.

## Entity Relationship Diagram

```
┌──────────────┐
│    users     │
└──────────────┘
       │ 1
       │
       │ n
       ▼
┌──────────────┐
│audit_events  │◄────┐
└──────────────┘     │
                     │
       ┌─────────────┼─────────────┐
       │             │             │
       │ n           │ n           │ n
       ▼             ▼             ▼
┌──────────────┐┌──────────┐┌──────────┐
│ properties   ││  events  ││  scores  │
└──────────────┘└──────────┘└──────────┘
       │             │             ▲
       │ 1           │ 1           │
       │             │             │
       │ n           │ n           │
       └──────┬──────┴─────────────┘
              ▼
       ┌──────────────┐
       │observations  │
       └──────────────┘
```

## Core Tables

### users

Stores authenticated users with role-based access control.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique user identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email (login) |
| hashed_password | VARCHAR(255) | NOT NULL | Bcrypt password hash |
| full_name | VARCHAR(255) | NOT NULL | Display name |
| role | VARCHAR(50) | NOT NULL | RBAC role (admin, analyst, reviewer, viewer) |
| is_active | BOOLEAN | NOT NULL | Account status |
| created_at | TIMESTAMPTZ | NOT NULL | Account creation timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL | Last update timestamp |

**Indexes**:
- Unique index on `email`

**Roles**:
- `admin`: Full system access, user management
- `analyst`: Create events, trigger scoring, review scores
- `reviewer`: Review and override scores, view all data
- `viewer`: Read-only access to triage queue and evidence

### properties

Represents insured properties in the portfolio.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Internal property ID |
| external_property_id | TEXT | UNIQUE, NOT NULL | Client's property identifier |
| geometry | GEOMETRY(Point, 4326) | NOT NULL | Property location (WGS84) |
| address_hash | TEXT | NULL | Anonymized address (SHA256) |
| building_type | TEXT | NULL | Residential, commercial, etc. |
| exposure_value | NUMERIC(18,2) | NULL | Insured value in USD |
| region | TEXT | NULL | Geographic region |
| data_source | TEXT | NOT NULL | Source of property data |
| created_at | TIMESTAMPTZ | NOT NULL | Ingestion timestamp |
| updated_at | TIMESTAMPTZ | NOT NULL | Last update timestamp |

**Indexes**:
- Unique index on `external_property_id`
- GIST index on `geometry` for spatial queries

**Privacy**:
- `address_hash` is one-way hash, not reversible
- Raw addresses never stored
- PII scrubbed before ingestion

### events

Represents flood events (historical or real-time).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Event identifier |
| event_type | TEXT | NOT NULL | flood, hurricane, storm surge |
| name | TEXT | NOT NULL | Human-readable event name |
| event_date | DATE | NOT NULL | Date of event occurrence |
| geometry | GEOMETRY(Geometry, 4326) | NULL | Event extent polygon |
| stac_collection_id | TEXT | NULL | STAC collection reference |
| status | VARCHAR(50) | NOT NULL | draft, active, archived |
| created_at | TIMESTAMPTZ | NOT NULL | Event record creation |

**Indexes**:
- None (small table, full scans acceptable)

### observations

Property-level observations during an event.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Observation identifier |
| property_id | UUID | FK → properties(id), NOT NULL | Property reference |
| event_id | UUID | FK → events(id), NOT NULL | Event reference |
| observation_date | TIMESTAMPTZ | NOT NULL | Observation timestamp |
| flood_extent | BOOLEAN | NULL | Property within flood extent |
| distance_to_flood_m | NUMERIC | NULL | Distance to nearest flood boundary |
| rainfall_percentile | NUMERIC | NULL | Rainfall percentile (0-100) |
| river_stage_exceedance | BOOLEAN | NULL | River gauge exceeded threshold |
| elevation_m | NUMERIC | NULL | Ground elevation (meters) |
| optical_change | NUMERIC | NULL | Normalized optical change (0-1) |
| cloud_quality | NUMERIC | NULL | Cloud-free fraction (0-1) |
| sensor_source | TEXT | NULL | Satellite sensor name |
| feature_payload | JSONB | NOT NULL | Full feature vector + metadata |
| created_at | TIMESTAMPTZ | NOT NULL | Feature extraction timestamp |

**Indexes**:
- Index on `property_id`
- Index on `event_id`
- Composite index on `(property_id, event_id)` for joins

**feature_payload** structure (JSONB):
```json
{
  "stac_item_id": "sentinel2_20230815_tile32UQD",
  "weather_source": "noaa_ncep_precipitation",
  "elevation_source": "usgs_3dep_30m",
  "processing_version": "v1.0.0",
  "raw_features": {
    "ndwi_pre": 0.12,
    "ndwi_post": 0.78,
    "ndvi_pre": 0.65,
    "ndvi_post": 0.32
  }
}
```

### scores

Damage probability scores and inspection priorities.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Score identifier |
| property_id | UUID | FK → properties(id), NOT NULL | Property scored |
| event_id | UUID | FK → events(id), NOT NULL | Event context |
| model_version | TEXT | NOT NULL | Scoring model version |
| damage_probability | NUMERIC(5,4) | NOT NULL | Probability (0.0000 - 1.0000) |
| damage_confidence | TEXT | NOT NULL | low, medium, high |
| inspection_priority | VARCHAR(10) | NOT NULL | P1, P2, P3 |
| recommended_action | TEXT | NOT NULL | Human-readable recommendation |
| evidence | JSONB | NOT NULL | Explainability payload |
| created_at | TIMESTAMPTZ | NOT NULL | Score generation timestamp |

**Indexes**:
- Index on `property_id`
- Index on `event_id`
- Index on `inspection_priority`
- Composite index on `(event_id, inspection_priority, damage_probability DESC)` for triage queries

**evidence** structure (JSONB):
```json
{
  "flood_extent_signal": 1.0,
  "proximity_signal": 0.85,
  "rainfall_signal": 0.92,
  "river_stage_signal": 1.0,
  "optical_change_signal": 0.76,
  "elevation_signal": 0.45,
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
}
```

### audit_events

Immutable audit trail of human actions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Audit record identifier |
| user_id | UUID | NULL | User who performed action |
| property_id | UUID | NULL | Property involved |
| event_id | UUID | NULL | Event involved |
| score_id | UUID | NULL | Score reviewed |
| action | TEXT | NOT NULL | accept, override, export, etc. |
| before_value | JSONB | NULL | State before action |
| after_value | JSONB | NULL | State after action |
| reason | TEXT | NULL | User-provided reason for override |
| created_at | TIMESTAMPTZ | NOT NULL | Audit record timestamp |

**Indexes**:
- Index on `action`
- Index on `created_at` for chronological queries

**Retention**: Audit records are never deleted (immutable log).

## Data Lineage

Every score is traceable:
```
score.evidence → observation.id → observation.feature_payload → STAC item
```

This enables:
- Regenerating scores with updated models
- Verifying input data quality
- Debugging unexpected scores
- Regulatory compliance

## Spatial Queries

PostGIS enables efficient geospatial operations:

**Find properties within flood extent**:
```sql
SELECT p.* 
FROM properties p
JOIN events e ON ST_Intersects(p.geometry, e.geometry)
WHERE e.id = '...';
```

**Find properties within 500m of flood boundary**:
```sql
SELECT p.*, ST_Distance(p.geometry, e.geometry) as distance_m
FROM properties p, events e
WHERE e.id = '...'
  AND ST_DWithin(p.geometry, e.geometry, 500);
```

## Data Volume Estimates (Pilot)

| Entity | Count | Size per Row | Total Size |
|--------|-------|--------------|------------|
| users | 10 | 1 KB | 10 KB |
| properties | 10,000 | 500 bytes | 5 MB |
| events | 5 | 1 KB | 5 KB |
| observations | 50,000 | 2 KB | 100 MB |
| scores | 50,000 | 3 KB | 150 MB |
| audit_events | 5,000 | 1 KB | 5 MB |

**Total**: ~260 MB database (easily fits in memory for performance)

## Backup & Recovery

- Daily automated backups
- Point-in-time recovery enabled
- Backups retained for 30 days
- Test restore monthly

## Schema Evolution

All schema changes are versioned with Alembic migrations:

1. Create migration: `alembic revision -m "description"`
2. Edit generated migration file
3. Apply: `alembic upgrade head`
4. Rollback: `alembic downgrade -1`

Never modify the database schema manually.

## Data Privacy & Compliance

- No raw addresses stored
- Exposure values optional
- PII hashed or pseudonymized
- GDPR-compliant deletion on request (property and all linked records)
- Audit trail cannot be deleted (regulatory requirement)
