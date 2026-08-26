from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.config import settings

ISSUER = f"{settings.supabase_url}/auth/v1"
JWKS_URL = f"{ISSUER}/.well-known/jwks.json"

# auto_error=False so a missing header returns None here instead of
# FastAPI's own default 403 -- lets us keep raising 401 ourselves,
# matching the behavior every existing test already expects.
_bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def _jwks_client() -> PyJWKClient:
    # Cached so Supabase's public signing keys are fetched once per
    # server run, not on every single request.
    return PyJWKClient(JWKS_URL)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme)) -> dict:
    """
    Verifies the JWT Supabase issued at login and returns the user's
    id and email. Raises 401 for anything that doesn't check out.

    Uses FastAPI's HTTPBearer security scheme specifically so it
    registers in the OpenAPI schema -- that's what makes Swagger's
    "Authorize" button actually appear, rather than needing the
    Authorization header typed into every endpoint's own form.

    Deliberately does NOT use supabase.auth.get_user() -- that method
    has a documented history of breaking after Supabase's JWT signing
    key migrations (see supabase-py issue #1183). Verifying the token
    directly against Supabase's public JWKS endpoint is the more
    robust path, and doesn't require a round trip to Supabase on
    every authenticated request either.
    """
    if credentials is None:
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header.")

    token = credentials.credentials

    try:
        signing_key = _jwks_client().get_signing_key_from_jwt(token).key
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256", "ES256"],
            issuer=ISSUER,
            audience="authenticated",
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid or expired token: {e}")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing user id.")

    return {"id": user_id, "email": payload.get("email")}