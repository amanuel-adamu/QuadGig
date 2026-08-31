from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.db import get_supabase
from app.deps import get_current_user
from app.order_logic import calculate_commission, calculate_seller_payout, check_transition, should_refund
from app.stripe_client import get_stripe

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
    payment_status: str


class OrderCreateResponse(OrderResponse):
    client_secret: Optional[str] = None
@router.get("", response_model=list[OrderResponse])
def list_orders(user: dict = Depends(get_current_user)):
    """
    Lists every order where the current user is either the buyer or the
    seller, most recent first.
    """
    supabase = get_supabase()

    try:
        result = (
            supabase.table("orders")
            .select("*")
            .or_(f"buyer_id.eq.{user['id']},seller_id.eq.{user['id']}")
            .order("created_at", desc=True)
            .execute()
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Couldn't list orders: {e}")

    return result.data
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: str, user: dict = Depends(get_current_user)):
    """
    Fetches a single order. Only the buyer or seller on that order can
    view it -- prevents anyone from looking up an arbitrary order by
    guessing its UUID.
    """
    supabase = get_supabase()

    try:
        order_result = supabase.table("orders").select("*").eq("id", order_id).execute()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Couldn't look up order: {e}")

    if not order_result.data:
        raise HTTPException(status_code=404, detail="Order not found.")
    order = order_result.data[0]

    if user["id"] not in (order["buyer_id"], order["seller_id"]):
        raise HTTPException(status_code=403, detail="You're not part of this order.")

    return order
@router.post("", response_model=OrderCreateResponse, status_code=201)
def create_order(payload: OrderCreate, user: dict = Depends(get_current_user)):
    supabase = get_supabase()

    try:
        listing_result = supabase.table("listings").select("*").eq("id", payload.listing_id).execute()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Couldn't look up listing: {e}")

    if not listing_result.data:
        raise HTTPException(status_code=404, detail="Listing not found.")
    listing = listing_result.data[0]

    if listing["status"] != "active":
        raise HTTPException(status_code=400, detail="This listing is not currently available.")

    if listing["seller_id"] == user["id"]:
        raise HTTPException(status_code=400, detail="You can't order your own listing.")

    price_cents = listing["price_cents"]
    commission_cents = calculate_commission(price_cents)

    stripe = get_stripe()
    try:
        payment_intent = stripe.v1.payment_intents.create({
            "amount": price_cents,
            "currency": "usd",
            "automatic_payment_methods": {"enabled": True},
            "metadata": {"listing_id": listing["id"], "buyer_id": user["id"]},
        })
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Couldn't start payment: {e}")

    try:
        result = supabase.table("orders").insert({
            "listing_id": listing["id"],
            "buyer_id": user["id"],
            "seller_id": listing["seller_id"],
            "price_cents": price_cents,
            "commission_cents": commission_cents,
            "status": "requested",
            "stripe_payment_intent_id": payment_intent.id,
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment started, but saving the order failed: {e}")

    order = result.data[0]
    order["client_secret"] = payment_intent.client_secret
    return order


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

    update_fields = {"status": payload.status}

    if payload.status == "confirmed":
        _release_escrow(supabase, order)
    elif payload.status == "cancelled":
        if _refund_payment(order):
            update_fields["payment_status"] = "refunded"

    result = supabase.table("orders").update(update_fields).eq("id", order_id).execute()
    return result.data[0]


def _refund_payment(order: dict) -> bool:
    """
    Refunds the buyer in full if a payment was actually captured.
    Returns True if a refund was issued (caller should record
    payment_status as 'refunded'), False if there was nothing to
    refund. Safe to call on any cancellation: check_transition()
    only allows 'cancelled' from states reachable before 'confirmed'
    -- the one status that moves money out of the platform's balance
    -- so the funds are always still sitting there to give back.
    """
    if not should_refund(order["payment_status"]):
        return False

    stripe = get_stripe()
    try:
        stripe.v1.refunds.create({"payment_intent": order["stripe_payment_intent_id"]})
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Refund failed: {e}")

    return True


def _release_escrow(supabase, order: dict) -> None:
    """
    Transfers the seller's cut (price minus commission) out of the
    platform's Stripe balance and into their connected account.
    """
    if order["payment_status"] != "paid":
        raise HTTPException(status_code=400, detail="Payment hasn't been confirmed yet -- can't release funds.")

    seller_result = supabase.table("users").select("stripe_connect_account_id").eq("id", order["seller_id"]).execute()
    seller_account_id = seller_result.data[0]["stripe_connect_account_id"] if seller_result.data else None
    if not seller_account_id:
        raise HTTPException(status_code=400, detail="Seller hasn't completed Stripe onboarding yet.")

    stripe = get_stripe()
    try:
        stripe.v1.transfers.create({
            "amount": calculate_seller_payout(order["price_cents"], order["commission_cents"]),
            "currency": "usd",
            "destination": seller_account_id,
            "transfer_group": order["id"],
        })
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Payment transfer to seller failed: {e}")