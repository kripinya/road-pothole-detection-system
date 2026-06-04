"""Prioritization Agent - Ranks potholes for repair scheduling."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Estimated repair cost per severity level (in INR)
COST_ESTIMATES = {
    "critical": 25000,
    "high": 15000,
    "medium": 8000,
    "low": 3000,
}

# Recommended actions per severity
ACTIONS = {
    "critical": "Immediate repair required. Deploy emergency crew within 24 hours.",
    "high": "Schedule repair within 3 days. Mark area with warning signs.",
    "medium": "Add to weekly maintenance queue. Monitor for worsening.",
    "low": "Log for next scheduled maintenance cycle. No immediate action needed.",
}


class PrioritizationAgent:
    """Agent that generates repair priority and cost estimates."""

    def prioritize(self, severity_report: dict[str, Any]) -> dict[str, Any]:
        """Generate a repair priority recommendation.

        Args:
            severity_report: Output from SeverityAgent.assess().

        Returns:
            Dictionary with priority score, cost estimate, and action.
        """
        logger.info("PrioritizationAgent generating priority")

        classification = severity_report.get("classification", "low")
        score = severity_report.get("score", 0.0)

        # Priority score is derived from severity but factors in urgency
        # Critical potholes get a boosted priority to jump the queue
        priority_score = score
        if classification == "critical":
            priority_score = min(score * 1.2, 100.0)

        estimated_cost = COST_ESTIMATES.get(classification, 3000)
        recommended_action = ACTIONS.get(classification, ACTIONS["low"])

        # Determine repair timeline
        if classification == "critical":
            timeline = "within_24_hours"
        elif classification == "high":
            timeline = "within_3_days"
        elif classification == "medium":
            timeline = "within_1_week"
        else:
            timeline = "next_maintenance_cycle"

        return {
            "priority_score": round(priority_score, 2),
            "estimated_cost_inr": estimated_cost,
            "recommended_action": recommended_action,
            "repair_timeline": timeline,
            "classification": classification,
        }
