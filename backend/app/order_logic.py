"""
Pure logic for order state transitions and commission math. No I/O,
no Supabase -- kept separate so every rule is trivially unit testable.
"""

COMMISSION_RATE = 0.10

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


def calculate_seller_payout(price_cents: int, commission_cents: int) -> int:
    """What actually gets transferred to the seller once escrow releases."""
    return price_cents - commission_cents


def should_refund(payment_status: str) -> bool:
    """Only refund if a payment was actually captured -- 'pending' or 'failed' mean there's nothing to give back."""
    return payment_status == "paid"


def check_transition(current_status: str, new_status: str, is_buyer: bool, is_seller: bool) -> str | None:
    """
    Returns None if the transition is allowed, or a human-readable
    error string if it isn't.
    """
    rule = TRANSITION_RULES.get((current_status, new_status))
    if rule is None:
        return f"Can't move from '{current_status}' to '{new_status}'."
    if rule == "seller" and not is_seller:
        return "Only the seller can make this change."
    if rule == "buyer" and not is_buyer:
        return "Only the buyer can make this change."
    return None
