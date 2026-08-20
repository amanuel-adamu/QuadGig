from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.db import get_supabase
from app.deps import get_current_user
from app.order_logic import calculate_commission, check_transition

router = APIRouter(prefix="/orders", tags=["orders"])


class OrderCreate(BaseModel):
    listing_id: str


class OrderStatusUpdate(BaseModel):
    status: str


class OrderResponse(BaseModel):
    id: str
    listing_id: str
    buyer_id: str
    seller_id: str
    price_cents: int
    commission_cents: int
    status: str


@router.post("", response_model=OrderResponse, status_code=201)
def create_order(payload: OrderCreate, user: dict = Depends(get_current_user)):
    supabase = get_supabase()

    listing_result = supabase.table("listings").select("*").eq("id", payload.listing_id).execute()
    if not listing_result.data:
        raise HTTPException(status_code=404, detail="Listing not found.")
    listing = listing_result.data[0]

    if listing["status"] != "active":
        raise HTTPException(status_code=400, detail="This listing is not currently available.")

    if listing["seller_id"] == user["id"]:
        raise HTTPException(status_code=400, detail="You can't order your own listing.")

    price_cents = listing["price_cents"]
    commission_cents = calculate_commission(price_cents)

    result = supabase.table("orders").insert({
        "listing_id": listing["id"],
        "buyer_id": user["id"],
        "seller_id": listing["seller_id"],
        "price_cents": price_cents,
        "commission_cents": commission_cents,
        "status": "requested",
    }).execute()

    return result.data[0]


@router.patch("/{order_id}", response_model=OrderResponse)
def update_order_status(order_id: str, payload: OrderStatusUpdate, user: dict = Depends(get_current_user)):
    supabase = get_supabase()

    order_result = supabase.table("orders").select("*").eq("id", order_id).execute()
    if not order_result.data:
        raise HTTPException(status_code=404, detail="Order not found.")
    order = order_result.data[0]

    is_buyer = user["id"] == order["buyer_id"]
    is_seller = user["id"] == order["seller_id"]
    if not is_buyer and not is_seller:
        raise HTTPException(status_code=403, detail="You're not part of this order.")

    error = check_transition(order["status"], payload.status, is_buyer, is_seller)
    if error:
        raise HTTPException(status_code=400, detail=error)

    result = supabase.table("orders").update({"status": payload.status}).eq("id", order_id).execute()
    return result.data[0]
