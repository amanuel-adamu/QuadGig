from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field

from app.db import get_supabase
from app.edu_verification import is_edu_email

router = APIRouter(prefix="/auth", tags=["auth"])


# ---------- request/response models ----------

class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    display_name: str = Field(min_length=1, max_length=100)


class SignupResponse(BaseModel):
    id: str
    email: str
    message: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
    user_id: str
    edu_verified: bool


# ---------- routes ----------

@router.post("/signup", response_model=SignupResponse, status_code=201)
def signup(payload: SignupRequest):
    if not is_edu_email(payload.email):
        raise HTTPException(
            status_code=400,
            detail="Please sign up with a .edu email address.",
        )

    supabase = get_supabase()

    try:
        auth_response = supabase.auth.sign_up({
            "email": payload.email,
            "password": payload.password,
            "options": {"data": {"display_name": payload.display_name}},
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = auth_response.user
    if user is None:
        raise HTTPException(status_code=400, detail="Signup failed.")

    # public.users is now populated automatically by the on_auth_user_created
    # trigger the moment the auth.users row commits -- this avoids the
    # foreign-key race where our own insert could run before that row was
    # fully visible.

    return SignupResponse(
        id=user.id,
        email=payload.email,
        message="Check your inbox to confirm your email before logging in.",
    )
@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    supabase = get_supabase()

    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": payload.email,
            "password": payload.password,
        })
    except Exception as e:
        if "confirm" in str(e).lower():
            raise HTTPException(
                status_code=403,
                detail="Please confirm your email before logging in — check your inbox for the link.",
            )
        raise HTTPException(status_code=401, detail=f"Login failed: {e}")

    user = auth_response.user
    session = auth_response.session

    supabase.table("users").update({"edu_verified": True}).eq("id", user.id).execute()

    return LoginResponse(
        access_token=session.access_token,
        user_id=user.id,
        edu_verified=True,
    )