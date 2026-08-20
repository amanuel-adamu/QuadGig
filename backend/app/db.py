from supabase import create_client, Client

from app.config import settings


def get_supabase() -> Client:
    """
    Fresh client per call, no reuse across requests. That already
    gives each request its own isolated client/session — no shared
    state to leak between users — without needing to touch
    ClientOptions, whose shape keeps shifting across supabase-py
    versions (that's what broke here originally).
    """
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
    )