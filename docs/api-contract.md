# API Contract

## Road Pothole Detection System — REST API v1

**Base URL:** `https://<host>/api/v1` 
**Auth:** Bearer JWT in `Authorization` header 
**Content-Type:** `application/json` (unless file upload) 
**Error Format:** `{ "detail": "message" }`

---

## 1. Authentication

### POST `/auth/register`
Create a new user account.

**Auth Required:** No

**Request Body:**
```json
{
 "email": "operator@city.gov",
 "password": "SecurePass123!",
 "full_name": "Ananya Karn"
}
```

**Response (201 Created):**
```json
{
 "id": "550e8400-e29b-41d4-a716-446655440000",
 "email": "operator@city.gov",
 "full_name": "Ananya Karn",
 "role": "operator",
 "access_token": "eyJhbGciOiJIUzI1NiIs...",
 "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
 "token_type": "bearer"
}
```

**Errors:** `400` (validation), `409` (email exists)

---

### POST `/auth/login`
Authenticate and get JWT tokens.

**Auth Required:** No

**Request Body:**
```json
{
 "email": "operator@city.gov",
 "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
 "access_token": "eyJhbGciOiJIUzI1NiIs...",
 "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
 "token_type": "bearer",
 "expires_in": 1800,
 "user": {
 "id": "550e8400-e29b-41d4-a716-446655440000",
 "email": "operator@city.gov",
 "full_name": "Ananya Karn",
 "role": "operator"
 }
}
```

**Errors:** `401` (invalid credentials)

---

### POST `/auth/refresh`
Refresh an expired access token.

**Auth Required:** No (uses refresh token)

**Request Body:**
```json
{
 "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}
```

**Response (200 OK):**
```json
{
 "access_token": "eyJhbGciOiJIUzI1NiIs...",
 "token_type": "bearer",
 "expires_in": 1800
}
```

**Errors:** `401` (invalid/expired refresh token)

---

## 2. Detections

### POST `/detections`
Upload an image for pothole detection.

**Auth Required:** Yes (operator, admin) 
**Content-Type:** `multipart/form-data`

**Request:**
```
file: <image file (JPEG/PNG), max 10MB>
latitude: 28.6139 (optional)
longitude: 77.2090 (optional)
source_type: "upload" | "video" | "drone" (default: "upload")
```

**Response (202 Accepted):**
```json
{
 "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
 "status": "processing",
 "message": "Image uploaded. Detection in progress.",
 "image_path": "/uploads/2026/06/7c9e6679.jpg"
}
```

**Response (200 OK — when sync processing completes):**
```json
{
 "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
 "user_id": "550e8400-e29b-41d4-a716-446655440000",
 "image_path": "/uploads/2026/06/7c9e6679.jpg",
 "annotated_image_path": "/uploads/2026/06/7c9e6679_annotated.jpg",
 "source_type": "upload",
 "latitude": 28.6139,
 "longitude": 77.2090,
 "severity": "high",
 "confidence_score": 0.92,
 "bbox_data": {
 "detections": [
 {
 "class": "pothole",
 "confidence": 0.92,
 "bbox": { "x_min": 120, "y_min": 340, "x_max": 280, "y_max": 450 }
 }
 ],
 "image_width": 640,
 "image_height": 480,
 "model_version": "yolov8m-pothole-v1"
 },
 "ai_analysis": {
 "perception": { "estimated_size": "large", "road_type": "urban" },
 "severity": { "score": 78, "classification": "high" },
 "report": "A large pothole detected on urban asphalt road..."
 },
 "status": "detected",
 "detected_at": "2026-06-02T00:10:00Z",
 "created_at": "2026-06-02T00:10:00Z"
}
```

**Errors:** `400` (invalid file), `413` (file too large), `401` (unauthorized)

---

### GET `/detections`
List detections with filtering and pagination.

**Auth Required:** Yes (all roles)

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `page` | int | 1 | Page number |
| `limit` | int | 20 | Items per page (max 100) |
| `severity` | string | — | Filter: `low`, `medium`, `high`, `critical` |
| `status` | string | — | Filter: `detected`, `verified`, `repair_scheduled`, `resolved` |
| `source_type` | string | — | Filter: `upload`, `video`, `drone` |
| `date_from` | ISO datetime | — | Filter: detected after this date |
| `date_to` | ISO datetime | — | Filter: detected before this date |
| `sort_by` | string | `detected_at` | Sort field: `detected_at`, `severity`, `confidence_score` |
| `sort_order` | string | `desc` | Sort direction: `asc`, `desc` |

**Response (200 OK):**
```json
{
 "items": [
 {
 "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
 "severity": "high",
 "confidence_score": 0.92,
 "latitude": 28.6139,
 "longitude": 77.2090,
 "status": "detected",
 "source_type": "upload",
 "detected_at": "2026-06-02T00:10:00Z"
 }
 ],
 "total": 142,
 "page": 1,
 "limit": 20,
 "pages": 8
}
```

---

### GET `/detections/{id}`
Get full detection details.

**Auth Required:** Yes (all roles)

**Response (200 OK):** Full detection object (same as POST response)

**Errors:** `404` (not found)

---

### PATCH `/detections/{id}`
Update detection status or severity.

**Auth Required:** Yes (admin only for status, admin/operator for severity override)

**Request Body:**
```json
{
 "status": "verified",
 "severity": "critical"
}
```

**Response (200 OK):** Updated detection object

**Errors:** `400` (invalid state transition), `403` (insufficient role), `404`

---

### DELETE `/detections/{id}`
Soft-delete a detection.

**Auth Required:** Yes (admin only)

**Response (204 No Content)**

**Errors:** `403`, `404`

---

## 3. Map & Geo Queries

### GET `/map/potholes`
Get all potholes as GeoJSON for map rendering.

**Auth Required:** Yes (all roles)

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `severity` | string | Filter by severity |
| `status` | string | Filter by status |
| `bounds` | string | Viewport bounds: `sw_lat,sw_lng,ne_lat,ne_lng` |

**Response (200 OK):**
```json
{
 "type": "FeatureCollection",
 "features": [
 {
 "type": "Feature",
 "geometry": {
 "type": "Point",
 "coordinates": [77.2090, 28.6139]
 },
 "properties": {
 "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
 "severity": "high",
 "status": "detected",
 "confidence": 0.92,
 "detected_at": "2026-06-02T00:10:00Z"
 }
 }
 ]
}
```

---

### GET `/map/heatmap`
Get heatmap intensity data.

**Auth Required:** Yes (all roles)

**Response (200 OK):**
```json
{
 "points": [
 { "lat": 28.6139, "lng": 77.2090, "intensity": 5 },
 { "lat": 28.6200, "lng": 77.2150, "intensity": 12 }
 ]
}
```

---

### GET `/map/cluster`
Get clustered markers for performance at low zoom levels.

**Auth Required:** Yes (all roles)

**Query Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `zoom` | int | Current map zoom level |
| `bounds` | string | Viewport bounds |

**Response (200 OK):**
```json
{
 "clusters": [
 { "lat": 28.61, "lng": 77.21, "count": 15, "avg_severity": "high" },
 { "lat": 28.63, "lng": 77.23, "count": 3, "avg_severity": "low" }
 ]
}
```

---

## 4. Analytics

### GET `/analytics/summary`
Overall system statistics.

**Auth Required:** Yes (admin, viewer)

**Response (200 OK):**
```json
{
 "total_detections": 1423,
 "by_severity": {
 "critical": 89,
 "high": 312,
 "medium": 567,
 "low": 455
 },
 "by_status": {
 "detected": 890,
 "verified": 234,
 "repair_scheduled": 167,
 "resolved": 132
 },
 "detection_rate": {
 "today": 12,
 "this_week": 78,
 "this_month": 342
 },
 "avg_confidence": 0.87,
 "avg_resolution_time_hours": 72.5
}
```

---

### GET `/analytics/trends`
Time-series detection data.

**Auth Required:** Yes (admin, viewer)

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `period` | string | `30d` | Time range: `7d`, `30d`, `90d`, `1y` |
| `granularity` | string | `daily` | `daily`, `weekly`, `monthly` |

**Response (200 OK):**
```json
{
 "period": "30d",
 "granularity": "daily",
 "data": [
 { "date": "2026-06-01", "count": 12, "critical": 2, "high": 4, "medium": 3, "low": 3 },
 { "date": "2026-06-02", "count": 8, "critical": 1, "high": 3, "medium": 2, "low": 2 }
 ]
}
```

---

### GET `/analytics/severity-distribution`
Severity breakdown for charts.

**Auth Required:** Yes (admin, viewer)

**Response (200 OK):**
```json
{
 "distribution": [
 { "severity": "critical", "count": 89, "percentage": 6.3 },
 { "severity": "high", "count": 312, "percentage": 21.9 },
 { "severity": "medium", "count": 567, "percentage": 39.8 },
 { "severity": "low", "count": 455, "percentage": 32.0 }
 ]
}
```

---

## 5. Reports

### POST `/reports/generate`
Generate a PDF report.

**Auth Required:** Yes (admin only)

**Request Body:**
```json
{
 "date_from": "2026-05-01T00:00:00Z",
 "date_to": "2026-06-01T00:00:00Z",
 "area": {
 "center_lat": 28.6139,
 "center_lng": 77.2090,
 "radius_km": 10
 }
}
```

**Response (202 Accepted):**
```json
{
 "report_id": "report-uuid",
 "status": "generating",
 "message": "Report is being generated. Poll GET /reports/{id} for status."
}
```

---

### GET `/reports/{id}`
Download generated report.

**Auth Required:** Yes (admin only)

**Response (200 OK):** PDF file download 
**Response (202 Accepted):** `{ "status": "generating" }` (still processing)

---

## 6. ML Service (Internal)

> These endpoints are internal — only accessible within the Docker network.

### POST `/detect`
Run YOLOv8 inference on an image.

**Request:** `multipart/form-data` with `file` field

**Response (200 OK):**
```json
{
 "detections": [
 {
 "class": "pothole",
 "confidence": 0.92,
 "bbox": { "x_min": 120, "y_min": 340, "x_max": 280, "y_max": 450 }
 }
 ],
 "inference_time_ms": 245,
 "model_version": "yolov8m-pothole-v1",
 "image_size": { "width": 640, "height": 480 }
}
```

---

### POST `/analyze`
Run full Agentic AI pipeline.

**Request Body:**
```json
{
 "detection_id": "uuid",
 "bbox_data": { ... },
 "latitude": 28.6139,
 "longitude": 77.2090,
 "image_path": "/uploads/image.jpg"
}
```

**Response (200 OK):**
```json
{
 "perception": { ... },
 "severity": { ... },
 "prioritization": { ... },
 "report": "Natural language analysis...",
 "processing_time_ms": 3200
}
```

---

### GET `/model/info`
Get ML model metadata.

**Response (200 OK):**
```json
{
 "model_name": "yolov8m-pothole-v1",
 "framework": "ultralytics",
 "version": "8.1.0",
 "input_size": 640,
 "classes": ["pothole"],
 "metrics": {
 "mAP50": 0.87,
 "mAP50_95": 0.68
 },
 "device": "cpu"
}
```

---

## 7. Health Checks

### GET `/health`
Liveness probe.

**Auth Required:** No

**Response (200 OK):**
```json
{
 "status": "healthy",
 "timestamp": "2026-06-02T00:10:00Z",
 "version": "1.0.0"
}
```

---

### GET `/health/ready`
Readiness probe — checks all dependencies.

**Auth Required:** No

**Response (200 OK):**
```json
{
 "ready": true,
 "checks": {
 "database": { "status": "up", "latency_ms": 2 },
 "redis": { "status": "up", "latency_ms": 1 },
 "ml_service": { "status": "up", "latency_ms": 5 },
 "ollama": { "status": "up", "model_loaded": "llama3.1:8b" }
 }
}
```

---

### GET `/metrics`
Prometheus metrics endpoint.

**Auth Required:** No

**Response (200 OK):** Prometheus text exposition format
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/detections",status="200"} 1234

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{le="0.1"} 980

# HELP ml_inference_duration_seconds ML inference time
# TYPE ml_inference_duration_seconds histogram
ml_inference_duration_seconds_bucket{le="0.5"} 456
```

---

## 8. Error Response Format

All errors follow a consistent format:

```json
{
 "detail": "Human-readable error message",
 "status_code": 400,
 "error_type": "validation_error",
 "errors": [
 {
 "field": "email",
 "message": "Invalid email format"
 }
 ]
}
```

| Status Code | Meaning |
|-------------|---------|
| `400` | Bad Request (validation error) |
| `401` | Unauthorized (missing/invalid JWT) |
| `403` | Forbidden (insufficient role) |
| `404` | Not Found |
| `409` | Conflict (duplicate resource) |
| `413` | Payload Too Large (file > 10MB) |
| `422` | Unprocessable Entity |
| `429` | Too Many Requests (rate limited) |
| `500` | Internal Server Error |
| `503` | Service Unavailable (dependency down) |
