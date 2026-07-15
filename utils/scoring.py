"""
Scoring Utility

This module centralizes score classification ratings and grade evaluations
across all diagnostic modules.
"""

def rating_for_score(score: float, thresholds: list[tuple[float, str]]) -> str:
    """
    Looks up the rating label for a given score based on a list of descending thresholds.
    """
    for limit, label in thresholds:
        if score >= limit:
            return label
    return thresholds[-1][1] if thresholds else ""

def compute_overall_grade(overall_score: float) -> tuple[str, str]:
    """
    Evaluates the overall letter grade and status string for a given average score.
    """
    if overall_score >= 90:
        return "A", "Excellent"
    elif overall_score >= 80:
        return "B", "Good"
    elif overall_score >= 70:
        return "C", "Average"
    else:
        return "D", "Needs Improvement"

# Diagnostic module thresholds
SECURITY_THRESHOLDS = [(90, "Good"), (60, "Moderate"), (0, "Poor")]
ACCESSIBILITY_THRESHOLDS = [(85, "Excellent"), (65, "Needs Improvement"), (0, "Poor")]
PERFORMANCE_THRESHOLDS = [(85, "Excellent"), (70, "Good"), (50, "Average"), (0, "Poor")]
SEO_THRESHOLDS = [(90, "Excellent"), (75, "Good"), (50, "Average"), (0, "Poor")]
