# Technology Stack Justification

## Road Pothole Detection System

> This document provides a rationale for every technology choice in the system, comparing alternatives and justifying why each was selected for this project's specific requirements.

---

## 1. AI/ML Layer

### 1.1 Object Detection Model — YOLOv8/v9 (Ultralytics)

| Criteria | YOLOv8 | Faster R-CNN | SSD | EfficientDet |
|----------|--------|-------------|-----|-------------|
| **Inference Speed** | 5/5 (~10ms GPU) | 2/5 (~80ms GPU) | 4/5 (~15ms GPU) | 3/5 (~30ms GPU) |
| **Accuracy (mAP)** | 4/5 | 5/5 | 3/5 | 4/5 |
| **Ease of Fine-tuning** | 5/5 | 2/5 | 3/5 | 3/5 |
| **Community/Docs** | 5/5 | 4/5 | 3/5 | 3/5 |
| **Export Formats** | ONNX, TensorRT, CoreML | Limited | Limited | TFLite |

**Decision:** YOLOv8 — best balance of speed, accuracy, and developer experience. Ultralytics provides a one-line training API, built-in augmentation, and export to multiple deployment formats. Critical for real-time pothole detection where inference speed directly impacts user experience.

### 1.2 LLM Runtime — Ollama (Local)

| Criteria | Ollama (Local) | OpenAI API | Google Gemini API | Hugging Face Transformers |
|----------|---------------|------------|-------------------|--------------------------|
| **Cost** | 5/5 (Free) | 2/5 (Pay per token) | 3/5 (Free tier limited) | 4/5 (Free, self-hosted) |
| **Privacy** | 5/5 (All local) | 1/5 (Data sent to cloud) | 1/5 (Data sent to cloud) | 5/5 (All local) |
| **Ease of Setup** | 5/5 (Docker image) | 4/5 (API key) | 4/5 (API key) | 2/5 (Complex setup) |
| **Offline Capable** | 5/5 | 1/5 | 1/5 | 5/5 |
| **Docker Integration** | 5/5 (Official image) | N/A | N/A | 2/5 (Heavy images) |

**Decision:** Ollama — runs completely free and offline. Docker-native with `ollama/ollama` image. Supports Llama 3.1 8B and Mistral 7B which are sufficient for generating pothole analysis reports. No API keys, no usage limits, no data privacy concerns.

### 1.3 Agentic AI Framework — Custom Built

| Criteria | Custom Framework | LangGraph | CrewAI | Google ADK |
|----------|-----------------|-----------|--------|------------|
| **Learning Value** | 5/5 | 3/5 | 2/5 | 3/5 |
| **Simplicity** | 5/5 | 3/5 | 3/5 | 2/5 |
| **Dependencies** | 5/5 (Zero) | 2/5 (LangChain stack) | 2/5 (Heavy deps) | 3/5 |
| **Customization** | 5/5 | 4/5 | 3/5 | 3/5 |
| **Cost** | 5/5 (Free) | 5/5 (Free) | 5/5 (Free) | 5/5 (Free) |

**Decision:** Custom framework — maximum learning value for internship. Building agents from scratch means understanding the agent pattern deeply (perception → reasoning → action → observation loop). No third-party dependencies to manage. Can always migrate to LangGraph later if needed.

---

## 2. Backend Layer

### 2.1 API Framework — FastAPI (Python)

| Criteria | FastAPI | Django REST | Flask | Express.js |
|----------|---------|-------------|-------|-----------|
| **Async Support** | 5/5 (Native) | 2/5 (Partial) | 2/5 (Extensions) | 5/5 (Native) |
| **Auto API Docs** | 5/5 (Swagger) | 3/5 (DRF) | 2/5 (Manual) | 2/5 (Manual) |
| **Type Safety** | 5/5 (Pydantic) | 3/5 (Serializers) | 1/5 (None) | 3/5 (TypeScript) |
| **ML Integration** | 5/5 (Same Python) | 4/5 (Same Python) | 4/5 (Same Python) | 1/5 (Different lang) |
| **Performance** | 5/5 | 3/5 | 3/5 | 4/5 |

**Decision:** FastAPI — async by default (critical for handling image uploads + ML inference without blocking), automatic OpenAPI documentation, Pydantic validation, and same-language integration with Python ML stack. Perfect for backend learning: teaches modern API design, dependency injection, and type safety.

### 2.2 Database — PostgreSQL + PostGIS

| Criteria | PostgreSQL + PostGIS | MongoDB + GeoJSON | SQLite + SpatiaLite | MySQL |
|----------|---------------------|-------------------|---------------------|-------|
| **Geospatial Queries** | 5/5 (Native) | 4/5 (Good) | 2/5 (Limited) | 2/5 (Basic) |
| **ACID Compliance** | 5/5 | 2/5 (Eventual) | 4/5 | 4/5 |
| **JSON Support** | 5/5 (JSONB) | 5/5 (Native) | 2/5 | 3/5 |
| **Industry Adoption** | 5/5 | 4/5 | 2/5 (Dev only) | 4/5 |
| **Docker Support** | 5/5 | 5/5 | N/A (embedded) | 5/5 |

**Decision:** PostgreSQL + PostGIS — the gold standard for applications requiring both relational integrity and geospatial capabilities. PostGIS enables queries like "find all potholes within 5km" with spatial indexing. JSONB columns allow flexible storage for bounding box data and AI analysis reports without schema changes. Runs perfectly in Docker.

### 2.3 ORM — SQLAlchemy 2.0 (Async)

**Why SQLAlchemy over raw SQL:** ORM provides Python-class-to-table mapping, automatic SQL injection prevention, migration support via Alembic, and the ability to switch databases without rewriting queries.

**Why Async:** FastAPI is async; blocking database calls would negate its performance advantage. `asyncpg` driver provides non-blocking PostgreSQL connections.

### 2.4 Cache & Queue — Redis

**Why Redis:** Ultra-fast in-memory store for two purposes:
1. **Response caching:** Cache frequently-accessed map data and analytics to reduce DB load
2. **Task queue:** Queue heavy ML inference tasks for async processing, preventing API timeouts

---

## 3. Frontend Layer

### 3.1 Framework — Next.js 14+

| Criteria | Next.js | React (Vite) | Angular | Vue.js |
|----------|---------|-------------|---------|--------|
| **SSR/SSG** | 5/5 (Built-in) | 1/5 (None) | 4/5 (Universal) | 4/5 (Nuxt) |
| **Routing** | 5/5 (File-based) | 3/5 (React Router) | 4/5 (Built-in) | 4/5 (Vue Router) |
| **API Routes** | 5/5 (Built-in) | 1/5 (None) | 1/5 (None) | 1/5 (None) |
| **Learning Value** | 5/5 | 4/5 | 3/5 | 4/5 |
| **Job Market** | 5/5 | 5/5 | 4/5 | 3/5 |

**Decision:** Next.js 14+ with App Router — provides SSR for SEO and initial load performance, file-based routing (no manual route configuration), built-in API routes for BFF (Backend for Frontend) pattern, and React Server Components for optimal performance. Massively popular in the 2025-26 job market.

### 3.2 Map Library — Leaflet.js (react-leaflet)

**Why Leaflet over Google Maps / Mapbox:** Free and open-source with no API key requirements. Lightweight (~40KB). Supports OpenStreetMap tiles, marker clustering, heatmaps, and custom popups. react-leaflet provides React component wrappers.

### 3.3 Charts — Recharts

**Why Recharts over Chart.js / D3.js:** Built specifically for React with declarative components. Simpler API than D3.js while more customizable than Chart.js. Supports all chart types needed: line, bar, pie, area.

---

## 4. Infrastructure & DevOps Layer

### 4.1 Containerization — Docker + Docker Compose

**Why Docker:**
- Consistent environment across dev/staging/production (eliminates "works on my machine")
- Each microservice isolated with its own dependencies
- **CCVT specialization showcase:** demonstrates container virtualization concepts

**Why Docker Compose (over Kubernetes):**
- Single-server deployment (v1.0 scope)
- Simpler learning curve for internship timeline
- One command (`docker compose up`) runs 9 services
- Kubernetes can be added later as a scaling layer

### 4.2 CI/CD — GitHub Actions

**Why GitHub Actions over Jenkins / GitLab CI / CircleCI:**
- Free for public repos (unlimited minutes)
- Tightly integrated with GitHub (no separate server)
- YAML-based pipeline definition (Infrastructure as Code)
- Rich marketplace of pre-built actions
- **DevOps specialization showcase:** demonstrates CI/CD best practices

### 4.3 Reverse Proxy — Nginx

**Why Nginx:** Industry-standard reverse proxy for routing requests to microservices, SSL termination, static file serving, gzip compression, and load balancing. Lightweight and battle-tested.

### 4.4 Monitoring — Prometheus + Grafana

**Why this stack:**
- **Prometheus:** Pull-based metrics collection, time-series database, alerting rules. Industry standard for containerized applications.
- **Grafana:** Beautiful dashboards, multiple data source support, pre-built templates for Docker and FastAPI.
- **DevOps + CCVT showcase:** demonstrates production-grade observability

---

## 5. Development Tools

| Tool | Purpose | Why This One |
|------|---------|-------------|
| **ruff** | Python linting + formatting | 10-100x faster than flake8+black combined, all-in-one |
| **mypy** | Python type checking | Catches type errors before runtime |
| **pytest** | Python testing | Most popular, rich plugin ecosystem, fixtures |
| **ESLint** | JavaScript linting | Industry standard for JS/TS |
| **Prettier** | JavaScript formatting | Opinionated formatter, consistent code style |
| **Alembic** | Database migrations | SQLAlchemy-native migration tool |
| **pre-commit** | Git hooks | Auto-run lint+format before every commit |
| **httpx** | Async HTTP client | For testing FastAPI + inter-service communication |

---

## 6. Specialization Alignment Summary

| Technology | CCVT Yes | AIML Yes | DevOps Yes |
|-----------|---------|---------|-----------|
| Docker + Docker Compose | Containerization, Virtualization | — | Container orchestration |
| YOLOv8 | — | Deep Learning, Computer Vision | — |
| Ollama (Llama 3.1) | Containerized LLM | LLM-powered AI Agents | — |
| Custom Agentic Framework | — | Autonomous AI Systems | Automated workflows |
| FastAPI Microservices | Microservice architecture | ML model serving | API-first design |
| PostgreSQL + PostGIS | Virtualized database | — | IaC (Docker volume) |
| GitHub Actions CI/CD | — | ML pipeline automation | CI/CD best practices |
| Prometheus + Grafana | Cloud-native monitoring | — | Observability |
| Nginx | Network virtualization | — | Load balancing, SSL |
| Redis | Virtualized cache | — | Distributed task queue |
