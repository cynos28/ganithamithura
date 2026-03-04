"""
Game diagnostic utilities
=========================

• diagnose_performance  — Legacy rule-based engine (used by non-IRT variants)
• diagnose_with_irt     — Wrapper that translates IRT θ changes into the
                          same "increase" / "decrease" / "maintain" vocabulary
                          so callers can use a unified interface.
"""


def diagnose_performance(attempts: int, time_spent: float, target_time: float, hints_used: int):
    """
    Universal rule-based diagnostic engine.
    Returns: "increase", "decrease", "maintain"
    """

    # Rule 1 — Increase difficulty
    if attempts <= 2 and time_spent <= target_time and hints_used <= 1:
        return "increase"

    # Rule 2 — Decrease difficulty
    if attempts >= 2 and time_spent > target_time and hints_used >= 2:
        return "decrease"

    # Otherwise maintain
    return "maintain"


def diagnose_with_irt(theta_before: float, theta_after: float) -> str:
    """
    Translate a θ update into a human-readable direction.

    Used for logging and dashboard display so that the rule-based and
    IRT-based code paths produce the same vocabulary.
    """
    delta = theta_after - theta_before
    if delta > 0.05:
        return "increase"
    elif delta < -0.05:
        return "decrease"
    return "maintain"
