from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.db import get_supabase
from app.deps import get_current_user
from app.review_logic import calculate_average_rating

router = APIRouter(tags=["reviews"])


class ReviewCreate(BaseModel):
    order_id: str
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=1000)


class ReviewResponse(BaseModel):
    id: str
    order_id: str
    reviewer_id: str
    reviewee_id: str
    rating: int
    comment: Optional[str] = None


class UserReviewsResponse(BaseModel):
    reviews: list[ReviewResponse]
    review_count: int
    average_rating: Optional[float] = None


@router.post("/reviews", response_model=ReviewResponse, status_code=201)
def create_review(payload: ReviewCreate, user: dict = Depends(get_current_user)):
    supabase = get_supabase()

    order_result = supabase.table("orders").select("*").eq("id", payload.order_id).execute()
    if not order_result.data:
        raise HTTPException(status_code=404, detail="Order not found.")
    order = order_result.data[0]

    if order["buyer_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Only the buyer can leave a review for this order.")

    if order["status"] != "confirmed":
        raise HTTPException(status_code=400, detail="Can only review orders that have been confirmed as complete.")

    try:
        result = supabase.table("reviews").insert({
            "order_id": order["id"],
            "reviewer_id": user["id"],
            "reviewee_id": order["seller_id"],
            "rating": payload.rating,
            "comment": payload.comment,
        }).execute()
    except Exception as e:
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            raise HTTPException(status_code=400, detail="You've already reviewed this order.")
        raise HTTPException(status_code=502, detail=f"Couldn't submit review: {e}")

    return result.data[0]


@router.get("/users/{user_id}/reviews", response_model=UserReviewsResponse)
def get_user_reviews(user_id: str):
    """Public -- no auth required. Shows every review a seller has received."""
    supabase = get_supabase()
    try:
        result = supabase.table("reviews").select("*").eq("reviewee_id", user_id).execute()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Couldn't reach the database: {e}")

    reviews = result.data
    ratings = [r["rating"] for r in reviews]

    return {
        "reviews": reviews,
        "review_count": len(reviews),
        "average_rating": calculate_average_rating(ratings),
    }
