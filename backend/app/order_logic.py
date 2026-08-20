"""
Pure logic for order state transitions and commission math. No I/O,
no Supabase -- kept separate so every rule is trivially unit testable.
"""

COMMISSION_RATE = 0.10

# (from_status, to_status) -> who is allowed to make this move.
# "either" covers cancellation, which either party can initiate.
TRANSITION_RULES = {
    ("requested", "accepted"): "seller",
    ("requested", "cancelled"): "either",
    ("accepted", "in_progress"): "seller",
    ("accepted", "cancelled"): "either",
    ("in_progress", "delivered"): "seller",
    ("in_progress", "cancelled"): "either",
    ("delivered", "confirmed"): "buyer",
    ("delivered", "disputed"): "either",
    ("disputed", "confirmed"): "buyer",
    ("disputed", "cancelled"): "either",
}


def calculate_commission(price_cents: int) -> int:
    """10% commission, rounded to the nearest cent."""
    return round(price_cents * COMMISSION_RATE)


def check_transition(current_status: str, new_status: str, is_buyer: bool, is_seller: bool) -> str | None:
    """
    Returns None if the transition is allowed, or a human-readable
    error string if it isn't. Covers both "is this move legal at all"
    and "is *this person* allowed to make it."
    """
    rule = TRANSITION_RULES.get((current_status, new_status))
    if rule is None:
        return f"Can't move from '{current_status}' to '{new_status}'."
    if rule == "seller" and not is_seller:
        return "Only the seller can make this change."
    if rule == "buyer" and not is_buyer:
        return "Only the buyer can make this change."
    return None
