from app.utils.game_rules import diagnose_performance
from app.utils.game_domain_adapter import DOMAIN_ADAPTERS
from app.models.games import GameParameters, GameSession
from app.utils.game_variant_switcher import switch_variant



async def evaluate_session(session_data: dict):
    domain = session_data["domain"]

    attempts = session_data["attempts"]
    time_spent = session_data["time"]
    target_time = session_data["target_time"]
    hints_used = session_data["hints"]

    # Step 1: Global diagnostic
    diagnosis = diagnose_performance(
        attempts, time_spent, target_time, hints_used
    )

    # Step 2: Load parameter set for domain
    params_doc = await GameParameters.find_one(
        GameParameters.domain == domain
    )

    if not params_doc:
        raise Exception(f"No parameters found for domain {domain}")

    # ✅ FIX: assign params FIRST
    params = params_doc.params

    # Step 3: Variant switching (SAFE DEFAULT)
    current_variant = params.get(
        "current_variant",
        f"{domain[0].upper()}-V1"
    )

    new_variant = switch_variant(domain, current_variant, diagnosis)
    params["current_variant"] = new_variant

    # Step 4: Apply domain-specific adjustment
    adapter = DOMAIN_ADAPTERS[domain]
    new_params = adapter(diagnosis, params)

    # Step 5: Save updated parameters
    params_doc.params = new_params
    await params_doc.save()

    # Step 6: Save session trace
    session = GameSession(
        user_id=session_data.get("user_id"),
        domain=domain,
        attempts=attempts,
        time_spent=time_spent,
        target_time=target_time,
        hints_used=hints_used,
        diagnosis=diagnosis
    )
    await session.insert()

    return {
        "diagnosis": diagnosis,
        "new_params": new_params
    }
