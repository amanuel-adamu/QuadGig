"""
Pure logic for deciding whether an email belongs to an accredited
school. No I/O, no Supabase -- kept separate so it's trivial to
unit test without any network access.
"""


def extract_domain(email: str) -> str:
    return email.strip().lower().split("@")[-1]


def is_edu_email(email: str) -> bool:
    """MVP rule: domain ends in '.edu' -- covers Williams and most US colleges."""
    return extract_domain(email).endswith(".edu")
