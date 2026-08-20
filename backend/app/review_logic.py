"""
Pure logic for review aggregation. No I/O -- kept separate so it's
trivially unit testable, same pattern as order_logic.py.
"""


def calculate_average_rating(ratings: list[int]) -> float | None:
    """Average of a list of 1-5 star ratings, rounded to 2 decimal places. None if there are no ratings yet."""
    if not ratings:
        return None
    return round(sum(ratings) / len(ratings), 2)
