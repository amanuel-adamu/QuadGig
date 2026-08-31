from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.db import get_supabase
from app.deps import get_current_user

router = APIRouter(prefix="/listings", tags=["listings"])


class ListingCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    price_cents: int = Field(gt=0)
    category: str = Field(min_length=1, max_length=50)


class ListingResponse(BaseModel):
    id: str
    seller_id: str
    title: str
    description: Optional[str] = None
    price_cents: int
    category: str
    status: str


@router.post("", response_model=ListingResponse, status_code=201)
def create_listing(payload: ListingCreate, user: dict = Depends(get_current_user)):
    supabase = get_supabase()
    result = supabase.table("listings").insert({
        "seller_id": user["id"],
        "title": payload.title,
        "description": payload.description,
        "price_cents": payload.price_cents,
        "category": payload.category,
    }).execute()
    return result.data[0]


@router.get("", response_model=list[ListingResponse])
def browse_listings():
    """Public -- no auth required. Only ever shows active listings."""
    supabase = get_supabase()
    try:
        result = supabase.table("listings").select("*").eq("status", "active").execute()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Couldn't reach the database: {e}")
    return result.data
@router.get("/mine", response_model=list[ListingResponse])
def list_my_listings(user: dict = Depends(get_current_user)):
    """
    Lists every listing the current user has created, regardless of
    status (active, paused, or deleted) -- unlike the public browse
    endpoint above, which only shows active ones.
    """
    supabase = get_supabase()
    try:
        result = supabase.table("listings").select("*").eq("seller_id", user["id"]).execute()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Couldn't reach the database: {e}")
    return result.data

@router.get("/{listing_id}", response_model=ListingResponse)
def get_listing(listing_id: str):
    """Public -- no auth required."""
    supabase = get_supabase()
    try:
        result = supabase.table("listings").select("*").eq("id", listing_id).execute()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Couldn't reach the database: {e}")
    if not result.data:
        raise HTTPException(status_code=404, detail="Listing not found.")
    return result.data[0]
