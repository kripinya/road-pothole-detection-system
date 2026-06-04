"""Severity Assessment Agent - Scores pothole danger using weighted criteria."""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Weights for the scoring formula (must sum to 1.0)
WEIGHTS = {
    "size": 0.30,
    "confidence": 0.20,
    "count": 0.25,
    "road_type": 0.25,
}

# Road types mapped to a danger multiplier
# Highway potholes are far more dangerous than rural ones due to speed
ROAD_TYPE_SCORES = {
    "highway": 95,
    "urban": 75,
    "suburban": 55,
    "rural": 35,
    "unknown": 50,
}

# Size classification mapped to a numeric score
SIZE_SCORES = {
    "critical": 100,
    "large": 75,
    "medium": 50,
    "small": 25,
    "none": 0,
}


class SeverityAgent:
    """Agent that computes a 0-100 severity score from perception data."""

    def assess(self, perception_report: dict[str, Any]) -> dict[str, Any]:
        """Run multi-criteria severity assessment.

        Args:
            perception_report: Output from PerceptionAgent.analyze().

        Returns:
            Dictionary with score, classification, and reasoning breakdown.
        """
        logger.info("SeverityAgent running assessment")

        pothole_count = perception_report.get("pothole_count", 0)

        if pothole_count == 0:
            return {
                "score": 0.0,
                "classification": "low",
                "reasoning": "No potholes detected in the image.",
                "factor_breakdown": {},
            }

        # Factor 1: Size score
        size_label = perception_report.get("overall_estimated_size", "small")
        size_score = SIZE_SCORES.get(size_label, 25)

        # Factor 2: Model confidence (higher confidence = more certain it is real)
        confidence_avg = perception_report.get("confidence_avg", 0.5)
        confidence_score = confidence_avg * 100

        # Factor 3: Count score (more potholes in one image = worse road condition)
        count_score = min(pothole_count * 20, 100)

        # Factor 4: Road type danger
        road_type = perception_report.get("road_type_context", "unknown")
        road_score = ROAD_TYPE_SCORES.get(road_type, 50)

        # Weighted sum
        final_score = (
            WEIGHTS["size"] * size_score
            + WEIGHTS["confidence"] * confidence_score
            + WEIGHTS["count"] * count_score
            + WEIGHTS["road_type"] * road_score
        )

        # Clamp to 0-100
        final_score = max(0.0, min(100.0, final_score))

        # Classify
        if final_score >= 75:
            classification = "critical"
        elif final_score >= 50:
            classification = "high"
        elif final_score >= 25:
            classification = "medium"
        else:
            classification = "low"

        return {
            "score": round(final_score, 2),
            "classification": classification,
            "reasoning": (
                f"Detected {pothole_count} pothole(s). "
                f"Largest is '{size_label}' on a '{road_type}' road. "
                f"Average model confidence: {confidence_avg:.0%}."
            ),
            "factor_breakdown": {
                "size": {"value": size_label, "score": size_score, "weight": WEIGHTS["size"]},
                "confidence": {"value": f"{confidence_avg:.2f}", "score": confidence_score, "weight": WEIGHTS["confidence"]},
