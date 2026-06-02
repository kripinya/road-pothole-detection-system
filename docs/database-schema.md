# Database Schema Design

## Road Pothole Detection System

---

## 1. Entity-Relationship Diagram

```mermaid
erDiagram
 USERS ||--o{ DETECTIONS : creates
 USERS ||--o{ AUDIT_LOGS : generates
 DETECTIONS ||--o| REPAIR_PRIORITIES : has
 DETECTIONS ||--o{ AUDIT_LOGS : tracked_in

 USERS {
 uuid id PK
 varchar email UK
 varchar password_hash
 varchar full_name
 enum role "admin | operator | viewer"
 boolean is_active
 timestamp created_at
 timestamp updated_at
 }

 DETECTIONS {
 uuid id PK
 uuid user_id FK
 varchar image_path
 varchar annotated_image_path
 enum source_type "upload | video | drone"
 float latitude
 float longitude
 geography location "PostGIS POINT"
 enum severity "low | medium | high | critical"
 float confidence_score
 jsonb bbox_data
 jsonb ai_analysis
 enum status "detected | verified | repair_scheduled | resolved"
 timestamp detected_at
 timestamp created_at
 timestamp updated_at
 timestamp deleted_at "soft delete"
 }

 REPAIR_PRIORITIES {
 uuid id PK
 uuid detection_id FK UK
 float priority_score "0-100"
 float estimated_cost
 text recommended_action
 varchar generated_by "agentic_ai_v1"
 jsonb agent_outputs
 timestamp created_at
 timestamp updated_at
 }

 AUDIT_LOGS {
 uuid id PK
 uuid user_id FK "nullable"
 varchar action
 varchar entity_type
 uuid entity_id
 jsonb details
 inet ip_address
 timestamp created_at
 }
```

---

## 2. Table Definitions

### 2.1 users

Stores authenticated user accounts with role-based access.

```sql
CREATE TABLE users (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 email VARCHAR(255) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL,
 full_name VARCHAR(255) NOT NULL,
 role VARCHAR(20) NOT NULL DEFAULT 'operator'
 CHECK (role IN ('admin', 'operator', 'viewer')),
 is_active BOOLEAN NOT NULL DEFAULT TRUE,
 created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
 updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
```

**Design Decisions:**
- `UUID` primary key: avoids sequential ID enumeration attacks, works across distributed systems
- `password_hash`: stores bcrypt hash (60 chars), never plain text
- `role` as CHECK constraint: enforces valid values at DB level, not just app level
- `is_active`: soft-disable accounts without deleting (preserves audit trail)
- `updated_at`: tracked for optimistic concurrency control

### 2.2 detections

Core table storing every pothole detection with spatial data.

```sql
-- Requires PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE detections (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
 image_path VARCHAR(500) NOT NULL,
 annotated_image_path VARCHAR(500),
 source_type VARCHAR(20) NOT NULL DEFAULT 'upload'
 CHECK (source_type IN ('upload', 'video', 'drone')),
 latitude DOUBLE PRECISION,
 longitude DOUBLE PRECISION,
 location GEOGRAPHY(POINT, 4326), -- PostGIS spatial type, WGS84
 severity VARCHAR(20)
 CHECK (severity IN ('low', 'medium', 'high', 'critical')),
 confidence_score DOUBLE PRECISION CHECK (confidence_score >= 0 AND confidence_score <= 1),
 bbox_data JSONB,
 ai_analysis JSONB,
 status VARCHAR(30) NOT NULL DEFAULT 'detected'
 CHECK (status IN ('detected', 'verified', 'repair_scheduled', 'resolved')),
 detected_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
 created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
 updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
 deleted_at TIMESTAMP WITH TIME ZONE -- NULL means not deleted (soft delete)
);

-- Indexes
CREATE INDEX idx_detections_user_id ON detections(user_id);
CREATE INDEX idx_detections_severity ON detections(severity);
CREATE INDEX idx_detections_status ON detections(status);
CREATE INDEX idx_detections_detected_at ON detections(detected_at DESC);
CREATE INDEX idx_detections_created_at ON detections(created_at DESC);
CREATE INDEX idx_detections_deleted_at ON detections(deleted_at) WHERE deleted_at IS NULL;

-- Spatial index (critical for PostGIS performance)
CREATE INDEX idx_detections_location ON detections USING GIST(location);

-- Composite index for common queries
CREATE INDEX idx_detections_severity_status ON detections(severity, status)
 WHERE deleted_at IS NULL;
```

**Design Decisions:**
- `GEOGRAPHY(POINT, 4326)`: PostGIS spatial type using WGS84 coordinate system (same as GPS). Enables spatial queries like `ST_DWithin(location, point, distance_meters)`
- `latitude` + `longitude` as separate columns: easy to read/debug; `location` column is the indexed spatial version
- `bbox_data` as JSONB: variable number of bounding boxes per image
- `ai_analysis` as JSONB: flexible structure for Agentic AI outputs that may evolve
- `deleted_at`: soft delete pattern — `WHERE deleted_at IS NULL` filters active records
- `GIST` spatial index: essential for performant geo queries

**bbox_data JSON structure:**
```json
{
 "detections": [
 {
 "class": "pothole",
 "confidence": 0.92,
 "bbox": {
 "x_min": 120,
 "y_min": 340,
 "x_max": 280,
 "y_max": 450
 }
 }
 ],
 "image_width": 640,
 "image_height": 480,
 "model_version": "yolov8m-pothole-v1"
}
```

**ai_analysis JSON structure:**
```json
{
 "perception": {
 "estimated_size": "large",
 "estimated_depth": "deep",
 "road_type": "urban",
 "surface_material": "asphalt"
 },
 "severity": {
 "score": 78,
 "classification": "high",
 "factors": {
 "size_score": 85,
 "road_type_score": 70,
 "traffic_score": 80,
 "recurrence_score": 75
 }
 },
 "report": "This is a large, deep pothole on an urban asphalt road...",
 "pipeline_version": "agentic_ai_v1",
 "processing_time_ms": 3200
}
```

### 2.3 repair_priorities

Agentic AI-generated repair priority assignments.

```sql
CREATE TABLE repair_priorities (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 detection_id UUID NOT NULL UNIQUE REFERENCES detections(id) ON DELETE CASCADE,
 priority_score DOUBLE PRECISION NOT NULL CHECK (priority_score >= 0 AND priority_score <= 100),
 estimated_cost DOUBLE PRECISION CHECK (estimated_cost >= 0),
 recommended_action TEXT,
 generated_by VARCHAR(100) NOT NULL DEFAULT 'agentic_ai_v1',
 agent_outputs JSONB,
 created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
 updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_repair_priorities_detection_id ON repair_priorities(detection_id);
CREATE INDEX idx_repair_priorities_score ON repair_priorities(priority_score DESC);
```

**Design Decisions:**
- `UNIQUE` on `detection_id`: one priority record per detection (1:1 relationship)
- `ON DELETE CASCADE`: if detection is hard-deleted, priority goes too
- `agent_outputs` JSONB: stores raw output from each agent for debugging/auditing
- `priority_score DESC` index: fast retrieval of highest-priority items

### 2.4 audit_logs

Immutable audit trail for compliance and debugging.

```sql
CREATE TABLE audit_logs (
 id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
 user_id UUID REFERENCES users(id) ON DELETE SET NULL,
 action VARCHAR(100) NOT NULL,
 entity_type VARCHAR(50) NOT NULL,
 entity_id UUID,
 details JSONB,
 ip_address INET,
 created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at DESC);
```

**Design Decisions:**
- `user_id` nullable with `ON DELETE SET NULL`: preserves logs even if user is deleted
- No UPDATE or DELETE operations on this table — append-only (immutable log)
- `INET` type for IP address: PostgreSQL native type, supports IPv4 and IPv6
- `details` JSONB: flexible for storing any action-specific context

**Example audit log entries:**
```json
// User login
{"action": "user.login", "entity_type": "user", "entity_id": "uuid", "details": {"method": "email"}}

// Detection created
{"action": "detection.create", "entity_type": "detection", "entity_id": "uuid", "details": {"source": "upload", "severity": "high"}}

// Status updated
{"action": "detection.update_status", "entity_type": "detection", "entity_id": "uuid", "details": {"old_status": "detected", "new_status": "verified"}}

// AI analysis completed
{"action": "ai.analysis_complete", "entity_type": "detection", "entity_id": "uuid", "details": {"pipeline": "agentic_ai_v1", "duration_ms": 3200}}
```

---

## 3. PostGIS Spatial Query Examples

```sql
-- Find all potholes within 5km of a point (lat: 28.6139, lng: 77.2090 = Delhi)
SELECT id, severity, confidence_score,
 ST_AsGeoJSON(location) as geojson,
 ST_Distance(location, ST_MakePoint(77.2090, 28.6139)::geography) as distance_m
FROM detections
WHERE deleted_at IS NULL
 AND ST_DWithin(location, ST_MakePoint(77.2090, 28.6139)::geography, 5000)
ORDER BY distance_m;

-- Generate GeoJSON FeatureCollection for map overlay
SELECT json_build_object(
 'type', 'FeatureCollection',
 'features', json_agg(
 json_build_object(
 'type', 'Feature',
 'geometry', ST_AsGeoJSON(location)::json,
 'properties', json_build_object(
 'id', id,
 'severity', severity,
 'status', status,
 'confidence', confidence_score,
 'detected_at', detected_at
 )
 )
 )
) as geojson
FROM detections
WHERE deleted_at IS NULL;

-- Pothole density heatmap data (grid-based aggregation)
SELECT
 ST_X(ST_Centroid(ST_Collect(location::geometry))) as lng,
 ST_Y(ST_Centroid(ST_Collect(location::geometry))) as lat,
 COUNT(*) as count
FROM detections
WHERE deleted_at IS NULL
GROUP BY ST_SnapToGrid(location::geometry, 0.01) -- ~1km grid cells
ORDER BY count DESC;

-- Find clusters of potholes (potholes within 100m of each other)
SELECT id, severity,
 ST_ClusterDBSCAN(location::geometry, eps := 0.001, minpoints := 2)
 OVER() as cluster_id
FROM detections
WHERE deleted_at IS NULL;
```

---

## 4. Migration Strategy

Using **Alembic** for version-controlled database migrations:

```
alembic/
├── env.py # Migration environment config
├── script.py.mako # Migration template
└── versions/
 ├── 001_create_users_table.py
 ├── 002_create_detections_table.py
 ├── 003_create_repair_priorities_table.py
 ├── 004_create_audit_logs_table.py
 └── 005_add_spatial_indexes.py
```

Each migration is:
- **Reversible:** both `upgrade()` and `downgrade()` functions
- **Atomic:** wrapped in a transaction
- **Timestamped:** ordered by creation time
- **Tested:** run in CI pipeline against test database

---

## 5. Data Retention Policy

| Data Type | Retention | Rationale |
|-----------|-----------|-----------|
| Users | Indefinite (soft-delete) | Account recovery, audit trail |
| Detections | Indefinite (soft-delete) | Historical analysis, trend data |
| Detection Images | Indefinite | Required for re-analysis, evidence |
| Repair Priorities | Follows detection lifecycle | Cascade delete with detection |
| Audit Logs | 90 days | Compliance, space management |
| Redis Cache | TTL-based (1 hour default) | Ephemeral by design |
| Prometheus Metrics | 15 days | Observability, alerting |
