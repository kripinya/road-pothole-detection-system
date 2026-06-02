# Software Requirements Specification (SRS)

## Road Pothole Detection System — v1.0

**Document Version:** 1.0 
**Date:** June 2026 
**Author:** Ananya Karn 
**Organization:** IBM (Internship Project)

---

## 1. Introduction

### 1.1 Purpose
This Software Requirements Specification (SRS) document provides a complete description of the functional and non-functional requirements for the Road Pothole Detection System. It serves as a contract between the development team and stakeholders, defining exactly what the system will and will not do.

### 1.2 Product Scope
The Road Pothole Detection System is an AI-powered web platform that automates the detection, classification, mapping, and repair prioritization of road potholes. It combines computer vision (YOLOv8), Agentic AI (Ollama-powered LLM agents), geographic intelligence (PostGIS), and cloud-native architecture (Docker microservices) into a single integrated solution.

### 1.3 Definitions & Acronyms

| Term | Definition |
|------|-----------|
| YOLO | You Only Look Once — real-time object detection algorithm |
| mAP | Mean Average Precision — standard object detection accuracy metric |
| JWT | JSON Web Token — stateless authentication mechanism |
| PostGIS | Spatial database extension for PostgreSQL |
| Agentic AI | AI system composed of autonomous agents that perceive, reason, and act |
| Ollama | Local LLM runtime that runs open-source models (Llama 3.1, Mistral) |
| CRUD | Create, Read, Update, Delete — standard database operations |
| CI/CD | Continuous Integration / Continuous Deployment |
| GeoJSON | Open standard format for encoding geographic data structures |
| RBAC | Role-Based Access Control |

---

## 2. Overall Description

### 2.1 System Architecture Overview

The system follows a **microservices architecture** with the following services:

| Service | Technology | Port | Responsibility |
|---------|-----------|------|---------------|
| Frontend | Next.js 14+ | 3000 | User interface, dashboard, map |
| Backend API | FastAPI (Python) | 8000 | REST API, authentication, business logic |
| ML Service | FastAPI (Python) | 8001 | YOLO inference, Agentic AI pipeline |
| Database | PostgreSQL + PostGIS | 5432 | Persistent storage, geospatial queries |
| Cache/Queue | Redis | 6379 | Task queuing, response caching |
| LLM Runtime | Ollama | 11434 | Local LLM inference (Llama 3.1, Mistral) |
| Reverse Proxy | Nginx | 80/443 | Routing, SSL termination, load balancing |
| Metrics | Prometheus | 9090 | Metrics collection |
| Dashboards | Grafana | 3001 | Monitoring and alerting |

### 2.2 User Classes

| User Class | Access Level | Description |
|-----------|-------------|-------------|
| **Admin** | Full access | System configuration, user management, all features |
| **Operator** | Read + Write | Upload images, view detections, submit reports |
| **Viewer** | Read only | View dashboard, map, analytics (no uploads) |
| **System (Agentic AI)** | Internal | Autonomous agents that process detections without human intervention |

### 2.3 Operating Environment

- **Deployment:** Docker containers orchestrated via Docker Compose
- **OS:** Platform-independent (Linux containers)
- **Browser:** Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Hardware (minimum):** 4 CPU cores, 8GB RAM, 20GB disk (without GPU)
- **Hardware (recommended):** 8 CPU cores, 16GB RAM, NVIDIA GPU for faster inference

### 2.4 Constraints

- LLM inference via Ollama requires minimum 8GB RAM for Llama 3.1 8B model
- YOLOv8 inference on CPU is slower (~200-500ms/frame) vs GPU (~10-30ms/frame)
- PostGIS geospatial queries require PostgreSQL 14+ with PostGIS 3.3+ extension
- System designed for single-server deployment (v1.0); Kubernetes scaling is out of scope

---

## 3. Functional Requirements

### 3.1 Authentication & Authorization

| ID | Requirement | Priority | Input | Output |
|----|-------------|----------|-------|--------|
| FR-AUTH-01 | Users can register with email and password | Must Have | email, password, name | JWT access token + refresh token |
| FR-AUTH-02 | Users can log in with credentials | Must Have | email, password | JWT access token + refresh token |
| FR-AUTH-03 | JWT tokens expire after 30 minutes; refresh tokens after 7 days | Must Have | refresh token | New access token |
| FR-AUTH-04 | Admin can assign roles (admin/operator/viewer) to users | Should Have | user_id, role | Updated user record |
| FR-AUTH-05 | Protected endpoints reject requests without valid JWT | Must Have | Invalid/missing token | 401 Unauthorized |

### 3.2 Pothole Detection

| ID | Requirement | Priority | Input | Output |
|----|-------------|----------|-------|--------|
| FR-DET-01 | Upload a single image for pothole detection | Must Have | Image file (JPEG/PNG) + GPS coords | Detection result with bounding boxes, confidence scores |
| FR-DET-02 | Upload multiple images in batch | Should Have | Array of image files + GPS coords | Array of detection results |
| FR-DET-03 | Process video stream frame-by-frame | Must Have | Video file (MP4/AVI) or stream URL | Annotated frames with detections |
| FR-DET-04 | Accept drone/aerial imagery | Should Have | High-resolution aerial image + GPS | Detection results adjusted for aerial perspective |
| FR-DET-05 | Draw bounding boxes around detected potholes | Must Have | Raw image | Annotated image with bbox overlays |
| FR-DET-06 | Return confidence score for each detection | Must Have | — | Float 0.0-1.0 per detection |

### 3.3 Severity Classification & Agentic AI

| ID | Requirement | Priority | Input | Output |
|----|-------------|----------|-------|--------|
| FR-AI-01 | Classify pothole severity into 4 levels: Low, Medium, High, Critical | Must Have | Detection data | Severity enum + score (0-100) |
| FR-AI-02 | Perception Agent analyzes pothole size, estimated depth, and road type | Must Have | Bounding box + image region | Structured perception report (JSON) |
| FR-AI-03 | Severity Agent scores using weighted multi-criteria formula | Must Have | Perception report + location | Severity score + classification |
| FR-AI-04 | Prioritization Agent ranks all active potholes for repair | Must Have | All active detections | Sorted priority queue |
| FR-AI-05 | Reporting Agent generates human-readable analysis using Ollama LLM | Must Have | All agent outputs | Natural language report |
| FR-AI-06 | Orchestrator manages agent pipeline execution with error handling | Must Have | New detection trigger | Complete analysis record |

### 3.4 Geographic Mapping

| ID | Requirement | Priority | Input | Output |
|----|-------------|----------|-------|--------|
| FR-MAP-01 | Display all detections as markers on interactive map | Must Have | — | Leaflet map with markers |
| FR-MAP-02 | Color-code markers by severity (green/yellow/orange/red) | Must Have | — | Color-coded markers |
| FR-MAP-03 | Cluster nearby markers at lower zoom levels | Must Have | — | Clustered marker groups |
| FR-MAP-04 | Toggle heatmap layer showing pothole density | Should Have | — | Heatmap overlay |
| FR-MAP-05 | Click marker to view detection details in popup | Must Have | Marker click | Detection summary popup |
| FR-MAP-06 | Draw area to filter potholes within a geographic region | Nice to Have | Drawn polygon | Filtered detection list |
| FR-MAP-07 | Query potholes within N km of a point | Should Have | lat, lng, radius | GeoJSON feature collection |

### 3.5 CRUD Operations on Detections

| ID | Requirement | Priority | Input | Output |
|----|-------------|----------|-------|--------|
| FR-CRUD-01 | List all detections with pagination and filtering | Must Have | page, limit, filters (severity, status, date range) | Paginated detection list |
| FR-CRUD-02 | Get single detection by ID with full details | Must Have | detection_id | Complete detection record |
| FR-CRUD-03 | Update detection status (detected → verified → repair_scheduled → resolved) | Must Have | detection_id, new_status | Updated record |
| FR-CRUD-04 | Update detection severity (manual override) | Should Have | detection_id, new_severity | Updated record |
| FR-CRUD-05 | Soft-delete a detection (mark as deleted, don't remove) | Must Have | detection_id | Soft-deleted record |

### 3.6 Analytics & Reporting

| ID | Requirement | Priority | Input | Output |
|----|-------------|----------|-------|--------|
| FR-ANL-01 | Dashboard summary: total detections, by severity, by status | Must Have | — | Summary statistics (JSON) |
| FR-ANL-02 | Time-series trend: detections over time (daily/weekly/monthly) | Must Have | time_range, granularity | Time-series data |
| FR-ANL-03 | Severity distribution chart data | Must Have | — | Pie/bar chart data |
| FR-ANL-04 | Generate PDF report for a time range or area | Nice to Have | date_range, area | Downloadable PDF |

### 3.7 System Health & Monitoring

| ID | Requirement | Priority | Input | Output |
|----|-------------|----------|-------|--------|
| FR-HLT-01 | Liveness endpoint (`/health`) returns system status | Must Have | — | `{ "status": "healthy" }` |
| FR-HLT-02 | Readiness endpoint (`/health/ready`) checks DB + Redis + ML service | Must Have | — | `{ "ready": true/false, "checks": {...} }` |
| FR-HLT-03 | Prometheus metrics endpoint (`/metrics`) exposes request counts, latencies | Must Have | — | Prometheus text format |

---

## 4. Non-Functional Requirements

### 4.1 Performance

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-PERF-01 | API response time for CRUD operations | < 200ms (p95) |
| NFR-PERF-02 | Single image inference time (CPU) | < 500ms |
| NFR-PERF-03 | Single image inference time (GPU) | < 50ms |
| NFR-PERF-04 | Agentic AI pipeline completion | < 10 seconds |
| NFR-PERF-05 | Map rendering with 1000+ markers | < 2 seconds |
| NFR-PERF-06 | Concurrent API requests supported | 100+ simultaneous |

### 4.2 Security

| ID | Requirement | Implementation |
|----|-------------|---------------|
| NFR-SEC-01 | All passwords hashed with bcrypt (cost factor 12) | passlib + bcrypt |
| NFR-SEC-02 | JWT-based stateless authentication | python-jose |
| NFR-SEC-03 | HTTPS enforced in production | Nginx SSL termination |
| NFR-SEC-04 | SQL injection prevention | SQLAlchemy ORM (parameterized queries) |
| NFR-SEC-05 | XSS prevention | Next.js auto-escaping + CSP headers |
| NFR-SEC-06 | CORS restricted to allowed origins | FastAPI CORSMiddleware |
| NFR-SEC-07 | Rate limiting on auth endpoints | slowapi or custom middleware |

### 4.3 Reliability & Availability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-REL-01 | System uptime | 99.5% |
| NFR-REL-02 | Graceful degradation if ML service is down | API continues, detection queued |
| NFR-REL-03 | Database backup strategy | Daily automated pg_dump |
| NFR-REL-04 | Container auto-restart on failure | Docker `restart: unless-stopped` |

### 4.4 Scalability (CCVT)

| ID | Requirement | Approach |
|----|-------------|----------|
| NFR-SCL-01 | Horizontally scale ML service | Multiple container replicas |
| NFR-SCL-02 | Database connection pooling | SQLAlchemy async pool (max 20) |
| NFR-SCL-03 | Static asset serving via CDN | Nginx caching + gzip |
| NFR-SCL-04 | Async task processing | Redis queue + worker pattern |

### 4.5 DevOps & Deployment

| ID | Requirement | Implementation |
|----|-------------|---------------|
| NFR-DEV-01 | Containerized deployment | Docker + Docker Compose |
| NFR-DEV-02 | CI pipeline: lint + test + build on every push | GitHub Actions |
| NFR-DEV-03 | CD pipeline: auto-deploy on merge to main | GitHub Actions |
| NFR-DEV-04 | Infrastructure as Code | docker-compose.yml + .env |
| NFR-DEV-05 | Monitoring and alerting | Prometheus + Grafana |
| NFR-DEV-06 | Centralized logging | Docker logs + structured JSON logging |
| NFR-DEV-07 | Pre-commit hooks for code quality | ruff, black, mypy |

### 4.6 Maintainability

| ID | Requirement | Target |
|----|-------------|--------|
| NFR-MNT-01 | Code test coverage | > 80% |
| NFR-MNT-02 | API documentation | Auto-generated via FastAPI OpenAPI/Swagger |
| NFR-MNT-03 | Database migrations | Alembic version-controlled migrations |
| NFR-MNT-04 | Code style enforcement | ruff + black (Python), eslint + prettier (JS) |

---

## 5. Data Requirements

### 5.1 Training Data

| Dataset | Size | Source | Format |
|---------|------|--------|--------|
| Kaggle Pothole Dataset | ~6,000 images | Kaggle (open source) | JPEG + YOLO annotations |
| RDD2022 (Road Damage Detection) | ~26,000 images | IEEE Big Data Cup | JPEG + VOC/COCO annotations |
| Custom Augmented Data | ~10,000 images | Generated via Albumentations | JPEG + YOLO annotations |

### 5.2 Runtime Data

| Data Type | Storage | Retention |
|-----------|---------|-----------|
| Detection images | Local filesystem (Docker volume) | Indefinite |
| Detection metadata | PostgreSQL | Indefinite |
| GPS coordinates | PostgreSQL + PostGIS | Indefinite |
| AI analysis reports | PostgreSQL (JSONB) | Indefinite |
| Audit logs | PostgreSQL | 90 days |
| Prometheus metrics | Prometheus TSDB | 15 days |
| User sessions (JWT) | Stateless (no storage) | Token expiry |
| Redis cache | Redis (in-memory) | TTL-based (1 hour default) |

---

## 6. Interface Requirements

### 6.1 API Interface

- **Protocol:** HTTP/HTTPS (REST)
- **Format:** JSON (request and response bodies)
- **Authentication:** Bearer token (JWT) in `Authorization` header
- **Versioning:** URL-based (`/api/v1/`)
- **Documentation:** Auto-generated Swagger UI at `/docs`
- **Error Format:** Consistent JSON: `{ "detail": "message", "status_code": 400 }`

### 6.2 ML Service Interface (Internal)

- **Protocol:** HTTP (internal Docker network, no external access)
- **Endpoints:** `/detect`, `/analyze`, `/model/info`, `/health`
- **Image Transfer:** Multipart form-data (file upload)

### 6.3 Ollama Interface (Internal)

- **Protocol:** HTTP REST API
- **Endpoint:** `http://ollama:11434/api/generate`
- **Models:** `llama3.1:8b`, `mistral:7b`
- **Format:** JSON streaming response

### 6.4 User Interface

- **Framework:** Next.js 14+ (App Router)
- **Responsive:** Mobile-first design, breakpoints at 640px, 768px, 1024px, 1280px
- **Map:** Leaflet.js with OpenStreetMap tiles
- **Charts:** Recharts library
- **Theme:** Dark mode with road/safety-themed accent colors
