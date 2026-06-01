# Agentic AI Pipeline Design

## Road Pothole Detection System

---

## 1. Overview

The Agentic AI system is a **custom-built multi-agent pipeline** that autonomously processes pothole detections through four specialized agents. Each agent has a single responsibility, operates independently, and communicates through a structured data pipeline managed by an orchestrator.

**Why Agentic AI (not a monolithic script):**
- Each agent can be independently tested, debugged, and improved
- Agents can fail independently — the orchestrator handles retries and graceful degradation
- New agents can be added without modifying existing ones (Open/Closed Principle)
- Demonstrates the 2025-26 paradigm shift from "ML models" to "AI systems"

**LLM Backend:** Ollama running locally (Llama 3.1 8B / Mistral 7B)

---

## 2. Pipeline Architecture

```
                    ┌──────────────────────────────────────────┐
                    │           ORCHESTRATOR                    │
                    │  (Manages flow, retries, logging)         │
                    │                                          │
                    │   Input: Detection record + image data    │
                    │                                          │
                    │   ┌─────────────────────────────────┐    │
                    │   │   1. PERCEPTION AGENT            │    │
                    │   │   Analyzes visual characteristics │    │
                    │   │   Output → perception_report      │    │
                    │   └──────────────┬──────────────────┘    │
                    │                  │                        │
                    │                  ▼                        │
                    │   ┌─────────────────────────────────┐    │
                    │   │   2. SEVERITY AGENT              │    │
                    │   │   Multi-criteria scoring          │    │
                    │   │   Output → severity_result        │    │
                    │   └──────────────┬──────────────────┘    │
                    │                  │                        │
                    │                  ▼                        │
                    │   ┌─────────────────────────────────┐    │
                    │   │   3. PRIORITIZATION AGENT        │    │
                    │   │   Global ranking & clustering     │    │
                    │   │   Output → priority_result        │    │
                    │   └──────────────┬──────────────────┘    │
                    │                  │                        │
                    │                  ▼                        │
                    │   ┌─────────────────────────────────┐    │
                    │   │   4. REPORTING AGENT             │    │
                    │   │   LLM-powered report generation   │    │
                    │   │   Output → report_text            │    │
                    │   └─────────────────────────────────┘    │
                    │                                          │
                    │   Output: Combined analysis record        │
                    └──────────────────────────────────────────┘
```

---

## 3. Agent Specifications

### 3.1 Agent Base Class

Every agent implements a common interface:

```python
# Abstract base for all agents
class BaseAgent:
    name: str                    # Agent identifier
    description: str             # What this agent does
    version: str                 # Semantic version

    async def execute(self, context: AgentContext) -> AgentResult:
        """Execute the agent's task. Must be implemented by subclasses."""
        ...

    async def validate_input(self, context: AgentContext) -> bool:
        """Validate that required inputs are present."""
        ...

# Shared data structures
class AgentContext:
    detection_id: str
    image_path: str
    bbox_data: dict
    latitude: float | None
    longitude: float | None
    previous_results: dict       # Results from previous agents in pipeline
    metadata: dict               # Additional context (model version, etc.)

class AgentResult:
    agent_name: str
    status: str                  # "success" | "failed" | "skipped"
    data: dict                   # Agent-specific output
    execution_time_ms: int
    error: str | None
```

---

### 3.2 Perception Agent

**Purpose:** Analyze the visual characteristics of the detected pothole from the image.

| Property | Value |
|----------|-------|
| **Input** | Cropped pothole image region (from bbox), full image context |
| **Output** | Structured perception report |
| **LLM Used** | Ollama (Llama 3.1 8B) — vision analysis via text description |
| **Fallback** | Rule-based estimation from bbox dimensions |

**Logic:**

```
1. Extract pothole region from image using bbox coordinates
2. Calculate pothole area relative to image (size estimation)
3. Analyze bbox aspect ratio (width vs height → shape classification)
4. Send image description + bbox data to Ollama with structured prompt
5. Parse LLM response into structured format

Size estimation rules:
  - bbox_area / image_area < 0.05  → "small"
  - bbox_area / image_area < 0.15  → "medium"
  - bbox_area / image_area >= 0.15 → "large"

Depth estimation (from LLM analysis):
  - Based on shadow patterns described by LLM
  - Categories: "shallow", "moderate", "deep"
```

**Output Schema:**
```json
{
  "estimated_size": "large",
  "size_ratio": 0.18,
  "estimated_depth": "deep",
  "shape": "irregular",
  "road_type": "urban",
  "surface_condition": "cracked_asphalt",
  "surrounding_damage": true,
  "water_present": false,
  "confidence": 0.85
}
```

**Ollama Prompt Template:**
```
You are an expert road infrastructure analyst. Analyze this pothole detection:

Image dimensions: {width}x{height}
Pothole bounding box: x_min={x_min}, y_min={y_min}, x_max={x_max}, y_max={y_max}
Pothole area ratio: {area_ratio:.2%} of total image
Detection confidence: {confidence}
GPS Location: {latitude}, {longitude}

Based on the bounding box size and position, assess:
1. Estimated physical size (small/medium/large)
2. Estimated depth (shallow/moderate/deep)
3. Road type (highway/urban/rural/residential)
4. Surface material (asphalt/concrete/gravel/dirt)
5. Is there surrounding road damage? (yes/no)

Respond in JSON format only.
```

---

### 3.3 Severity Agent

**Purpose:** Score the pothole severity using a weighted multi-criteria formula.

| Property | Value |
|----------|-------|
| **Input** | Perception report, GPS location, historical data |
| **Output** | Severity score (0-100) and classification |
| **LLM Used** | None (pure algorithmic scoring) |
| **Fallback** | Score based on size + confidence only |

**Scoring Formula:**

```
severity_score = (
    size_score      × 0.30 +    # 30% weight: pothole size
    road_type_score × 0.20 +    # 20% weight: road importance
    traffic_score   × 0.25 +    # 25% weight: estimated traffic
    recurrence_score × 0.25     # 25% weight: repeated at same location?
)
```

**Score Components:**

| Component | Calculation |
|-----------|------------|
| `size_score` | `small=30, medium=60, large=90` + depth modifier (`shallow=0, moderate=+5, deep=+10`) |
| `road_type_score` | `highway=90, urban=70, residential=50, rural=30` |
| `traffic_score` | Based on road type proxy: `highway=85, urban=70, residential=40, rural=20` |
| `recurrence_score` | Query DB for detections within 50m radius in last 90 days. `0 previous=20, 1-2=50, 3-5=75, 6+=95` |

**Classification Thresholds:**

| Score Range | Severity | Color |
|-------------|----------|-------|
| 0 - 25 | Low | Green |
| 26 - 50 | Medium | Yellow |
| 51 - 75 | High | Orange |
| 76 - 100 | Critical | Red |

**Output Schema:**
```json
{
  "score": 78,
  "classification": "critical",
  "factors": {
    "size_score": 90,
    "road_type_score": 70,
    "traffic_score": 70,
    "recurrence_score": 80
  },
  "weights": {
    "size": 0.30,
    "road_type": 0.20,
    "traffic": 0.25,
    "recurrence": 0.25
  },
  "recurrence_count": 4,
  "nearby_detections": 4
}
```

---

### 3.4 Prioritization Agent

**Purpose:** Rank this detection against all active potholes and suggest batch repairs.

| Property | Value |
|----------|-------|
| **Input** | Severity result, all active detections from DB |
| **Output** | Priority rank, batch repair clusters, cost estimate |
| **LLM Used** | None (algorithmic ranking) |
| **Fallback** | Simple severity-based ranking |

**Logic:**

```
1. Fetch all active (non-resolved) detections from database
2. Calculate priority_score for each:
   priority_score = severity_score × 0.7 + recency_score × 0.3
   
   recency_score = max(0, 100 - days_since_detection × 2)
   (newer detections get higher recency; >50 days old → 0)

3. Rank by priority_score descending
4. Cluster nearby potholes (within 200m radius) for batch repair
5. Estimate cost per pothole:
   - Low severity: ₹500-1000
   - Medium: ₹1000-3000
   - High: ₹3000-8000
   - Critical: ₹8000-15000
```

**Output Schema:**
```json
{
  "priority_score": 82.5,
  "rank": 3,
  "total_active": 142,
  "percentile": 97.9,
  "cluster": {
    "cluster_id": "cluster-28.61-77.21",
    "nearby_count": 4,
    "cluster_severity": "high",
    "batch_repair_recommended": true
  },
  "cost_estimate": {
    "individual": 12000,
    "currency": "INR",
    "cluster_total": 35000
  }
}
```

---

### 3.5 Reporting Agent

**Purpose:** Generate a human-readable analysis report using Ollama LLM.

| Property | Value |
|----------|-------|
| **Input** | All previous agent outputs |
| **Output** | Natural language report |
| **LLM Used** | Ollama (Llama 3.1 8B) |
| **Fallback** | Template-based report (no LLM) |

**Ollama Prompt Template:**

```
You are an AI road infrastructure analyst generating a repair assessment report.

## Detection Data
- Detection ID: {detection_id}
- Location: {latitude}, {longitude}
- Detected: {detected_at}
- Source: {source_type}
- Model confidence: {confidence}

## Perception Analysis
- Size: {estimated_size}
- Depth: {estimated_depth}
- Road type: {road_type}
- Surface: {surface_condition}
- Surrounding damage: {surrounding_damage}

## Severity Assessment
- Score: {severity_score}/100 ({classification})
- Size factor: {size_score}
- Road importance: {road_type_score}
- Traffic impact: {traffic_score}
- Recurrence: {recurrence_score} ({recurrence_count} previous detections nearby)

## Priority
- Rank: #{rank} of {total_active} active potholes
- Cluster: {nearby_count} potholes within 200m
- Estimated repair cost: ₹{cost_estimate}

Generate a concise professional report (150-200 words) with:
1. Summary of the pothole condition
2. Risk assessment for road users
3. Recommended repair action and urgency
4. Cost-benefit analysis for immediate vs delayed repair

Use a professional, factual tone suitable for a municipal engineering report.
```

**Output Schema:**
```json
{
  "summary": "A large, deep pothole has been detected on an urban asphalt road...",
  "risk_level": "HIGH",
  "recommended_action": "Immediate patch repair within 48 hours",
  "urgency": "urgent",
  "cost_benefit": "Estimated repair cost of ₹12,000 is significantly lower than...",
  "full_report": "Complete 200-word report text...",
  "model_used": "llama3.1:8b",
  "tokens_used": 450,
  "generation_time_ms": 2100
}
```

---

## 4. Orchestrator Design

### 4.1 Execution Flow

```python
class PipelineOrchestrator:
    """Manages sequential execution of all agents."""

    agents = [
        PerceptionAgent(),
        SeverityAgent(),
        PrioritizationAgent(),
        ReportingAgent(),
    ]

    async def run(self, detection_data: dict) -> PipelineResult:
        context = AgentContext(detection_data)
        results = {}

        for agent in self.agents:
            try:
                # Validate input
                if not await agent.validate_input(context):
                    results[agent.name] = AgentResult(status="skipped")
                    continue

                # Execute with timeout
                result = await asyncio.wait_for(
                    agent.execute(context),
                    timeout=30.0  # 30 second timeout per agent
                )
                results[agent.name] = result
                context.previous_results[agent.name] = result.data

            except asyncio.TimeoutError:
                results[agent.name] = AgentResult(status="timeout")
                # Continue to next agent — don't fail entire pipeline

            except Exception as e:
                # Retry once
                try:
                    result = await agent.execute(context)
                    results[agent.name] = result
                except Exception:
                    results[agent.name] = AgentResult(status="failed", error=str(e))
                    # Continue — graceful degradation

        return PipelineResult(
            detection_id=detection_data["id"],
            results=results,
            status="complete" if all(r.status == "success" for r in results.values()) else "partial"
        )
```

### 4.2 Error Handling Strategy

| Failure Scenario | Behavior | Fallback |
|-----------------|----------|----------|
| Perception Agent fails | Continue pipeline | Use bbox dimensions for basic size estimation |
| Severity Agent fails | Continue pipeline | Default to confidence-score-based severity |
| Prioritization Agent fails | Continue pipeline | Skip ranking, assign default priority |
| Reporting Agent fails | Continue pipeline | Generate template-based report (no LLM) |
| Ollama is down | Reporting Agent uses fallback | Template: "Severity: {severity}. Size: {size}. Action: {action}" |
| All agents fail | Mark detection as "analysis_pending" | Retry via background scheduler |
| Timeout (>30s per agent) | Skip agent, continue | Log timeout for monitoring |

### 4.3 Logging & Observability

Every agent execution is logged:

```json
{
  "timestamp": "2026-06-02T00:10:05Z",
  "pipeline_id": "pipe-uuid",
  "detection_id": "det-uuid",
  "agent": "severity_agent",
  "status": "success",
  "execution_time_ms": 45,
  "input_summary": { "size": "large", "road_type": "urban" },
  "output_summary": { "score": 78, "classification": "critical" }
}
```

Prometheus metrics exposed:
- `agent_execution_total{agent, status}` — counter
- `agent_execution_duration_seconds{agent}` — histogram
- `pipeline_completion_total{status}` — counter
- `ollama_request_duration_seconds` — histogram

---

## 5. Ollama Integration

### 5.1 Connection

```python
# ML Service connects to Ollama via Docker network
OLLAMA_BASE_URL = "http://ollama:11434"

# API call
POST http://ollama:11434/api/generate
{
    "model": "llama3.1:8b",
    "prompt": "...",
    "stream": false,
    "options": {
        "temperature": 0.3,      # Low temp for factual output
        "top_p": 0.9,
        "num_predict": 500,      # Max tokens
        "stop": ["\n\n\n"]
    }
}
```

### 5.2 Model Management

```bash
# Pull models on first startup (via init script)
docker exec ollama ollama pull llama3.1:8b
docker exec ollama ollama pull mistral:7b

# Models are cached in Docker volume (ollama_data)
# No re-download needed after first pull
```

### 5.3 Fallback Strategy

```
Primary:   Ollama → llama3.1:8b
Fallback:  Ollama → mistral:7b (if primary fails)
Last resort: Template-based report (no LLM)
```

---

## 6. Testing Strategy

| Test Type | What's Tested | Tool |
|-----------|--------------|------|
| Unit Tests | Each agent in isolation with mock data | pytest |
| Integration Test | Full pipeline with mock Ollama | pytest + httpx |
| LLM Quality Test | Report quality scoring (manual review) | Jupyter notebook |
| Performance Test | Pipeline latency under load | locust |
| Chaos Test | Random agent failures → verify graceful degradation | pytest |

**Example unit test:**
```python
async def test_severity_agent_critical():
    agent = SeverityAgent()
    context = AgentContext(
        perception={"estimated_size": "large", "road_type": "highway"},
        recurrence_count=5
    )
    result = await agent.execute(context)
    assert result.data["classification"] == "critical"
    assert result.data["score"] >= 76
```
