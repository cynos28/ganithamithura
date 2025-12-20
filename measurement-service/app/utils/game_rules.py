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
