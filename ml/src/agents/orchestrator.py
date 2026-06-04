"""Orchestrator - Chains all agents into a single analysis pipeline."""

import time
import logging
from typing import Any

from src.schemas import InferenceResponse
from src.agents.perception import PerceptionAgent
from src.agents.severity import SeverityAgent
from src.agents.prioritization import PrioritizationAgent

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Manages the execution flow of all agentic AI agents.

    Pipeline:
        InferenceResponse -> Perception -> Severity -> Prioritization -> Final Report
    """

    def __init__(self):
        self.perception = PerceptionAgent()
        self.severity = SeverityAgent()
        self.prioritization = PrioritizationAgent()

    def run_pipeline(
        self, inference: InferenceResponse, image_metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Execute the full agentic AI analysis pipeline.

        Args:
            inference: Raw YOLO detection output.
            image_metadata: Optional context (GPS, road type, etc.).

        Returns:
            Combined report from all agents with timing and logs.
        """
        start_time = time.time()
        agent_logs: list[str] = []

        # Step 1: Perception
        try:
            agent_logs.append("PerceptionAgent: started")
            perception_report = self.perception.analyze(inference, image_metadata)
            agent_logs.append(f"PerceptionAgent: completed - found {perception_report['pothole_count']} potholes")
        except Exception as e:
            logger.error(f"PerceptionAgent failed: {e}")
            agent_logs.append(f"PerceptionAgent: FAILED - {e}")
            return self._error_report("Perception analysis failed", agent_logs, start_time)

        # Step 2: Severity
        try:
            agent_logs.append("SeverityAgent: started")
            severity_report = self.severity.assess(perception_report)
            agent_logs.append(f"SeverityAgent: completed - score={severity_report['score']}")
        except Exception as e:
            logger.error(f"SeverityAgent failed: {e}")
            agent_logs.append(f"SeverityAgent: FAILED - {e}")
            return self._error_report("Severity assessment failed", agent_logs, start_time)

        # Step 3: Prioritization
        try:
            agent_logs.append("PrioritizationAgent: started")
            priority_report = self.prioritization.prioritize(severity_report)
            agent_logs.append(f"PrioritizationAgent: completed - timeline={priority_report['repair_timeline']}")
        except Exception as e:
            logger.error(f"PrioritizationAgent failed: {e}")
            agent_logs.append(f"PrioritizationAgent: FAILED - {e}")
            return self._error_report("Prioritization failed", agent_logs, start_time)

        total_time_ms = (time.time() - start_time) * 1000
        agent_logs.append(f"Pipeline completed in {total_time_ms:.0f}ms")

        return {
            "perception": perception_report,
            "severity": severity_report,
            "priority": priority_report,
            "agent_logs": agent_logs,
            "pipeline_time_ms": round(total_time_ms, 2),
            "pipeline_version": "agentic_ai_v1",
        }

    def _error_report(
        self, error_msg: str, agent_logs: list[str], start_time: float
    ) -> dict[str, Any]:
        """Generate a structured error report when the pipeline fails."""
        total_time_ms = (time.time() - start_time) * 1000
        return {
            "error": error_msg,
            "perception": None,
            "severity": None,
            "priority": None,
            "agent_logs": agent_logs,
            "pipeline_time_ms": round(total_time_ms, 2),
            "pipeline_version": "agentic_ai_v1",
        }
