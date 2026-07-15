"""
Impact Simulator Utility

This module calculates the impact of checking off simulated fixes on the
website audit scores.
"""

from utils.scoring import (
    rating_for_score,
    compute_overall_grade,
    SECURITY_THRESHOLDS,
    ACCESSIBILITY_THRESHOLDS,
    PERFORMANCE_THRESHOLDS,
    SEO_THRESHOLDS
)

def simulate_fixes(report: dict, fixed_ids: set[str]) -> dict:
    """
    Simulates the audit score changes assuming the target deduction IDs are fixed.
    
    Returns:
        dict: A dictionary holding the recalculated scores and ratings.
    """
    security_deductions = report.get("security", {}).get("deductions", [])
    accessibility_deductions = report.get("accessibility", {}).get("deductions", [])
    performance_deductions = report.get("performance", {}).get("deductions", [])
    seo_deductions = report.get("seo", {}).get("deductions", [])

    def calculate_category_score(deductions, fixed_ids):
        sum_points = 0
        for d in deductions:
            if d["id"] not in fixed_ids:
                sum_points += d["points"]
        return max(0, 100 - sum_points)

    sec_score = calculate_category_score(security_deductions, fixed_ids)
    acc_score = calculate_category_score(accessibility_deductions, fixed_ids)
    perf_score = calculate_category_score(performance_deductions, fixed_ids)
    seo_score = calculate_category_score(seo_deductions, fixed_ids)

    # Recompute overall score as average of all four categories
    overall_score = round((sec_score + acc_score + perf_score + seo_score) / 4, 1)
    grade, status = compute_overall_grade(overall_score)

    return {
        "security_score": sec_score,
        "accessibility_score": acc_score,
        "performance_score": perf_score,
        "seo_score": seo_score,
        "overall_score": overall_score,
        "grade": grade,
        "status": status,
        "security_level": rating_for_score(sec_score, SECURITY_THRESHOLDS),
        "accessibility_level": rating_for_score(acc_score, ACCESSIBILITY_THRESHOLDS),
        "performance_rating": rating_for_score(perf_score, PERFORMANCE_THRESHOLDS),
        "seo_rating": rating_for_score(seo_score, SEO_THRESHOLDS)
    }
