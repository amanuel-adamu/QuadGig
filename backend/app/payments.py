import stripe as stripe_module
from fastapi import APIRouter, Depends, HTTPException, Request

from app.config import settings
from app.db import get_supabase
from app.deps import get_current_user
from app.stripe_client import get_stripe

router = APIRouter(tags=["payments"])


@router.post("/payments/onboard")
def onboard_seller(user: dict = Depends(get_current_user)):
    """
    Creates (or reuses) a Stripe Connect Express account for the
    current user and returns a fresh onboarding link. Account Links
    expire quickly, so a new one is generated on every call rather
    than caching the URL.

    NOTE: refresh_url/return_url below are placeholders. Once Adamu
    has deep-linking set up in the Expo app, these should point at
    real app URLs (e.g. quadgig://onboarding-complete) instead.
    """
    supabase = get_supabase()
    stripe = get_stripe()

    user_row = supabase.table("users").select("stripe_connect_account_id").eq("id", user["id"]).execute()
    account_id = user_row.data[0]["stripe_connect_account_id"] if user_row.data else None

    if not account_id:
        try:
            account = stripe.v1.accounts.create({
                "type": "express",
                "email": user["email"],
                "capabilities": {"transfers": {"requested": True}},
            })
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Couldn't create Stripe account: {e}")

        account_id = account.id
        supabase.table("users").update({"stripe_connect_account_id": account_id}).eq("id", user["id"]).execute()

    try:
        link = stripe.v1.account_links.create({
            "account": account_id,
            "refresh_url": "https://example.com/onboarding-refresh",  # TODO: replace with real app URL
            "return_url": "https://example.com/onboarding-complete",  # TODO: replace with real app URL
            "type": "account_onboarding",
        })
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Couldn't create onboarding link: {e}")

    return {"onboarding_url": link.url}


@router.get("/payments/onboard/status")
def onboard_status(user: dict = Depends(get_current_user)):
    """
    Definitive check of whether onboarding actually completed,
    straight from Stripe -- rather than inferring it from whatever
    page the browser happened to land on.
    """
    supabase = get_supabase()
    user_row = supabase.table("users").select("stripe_connect_account_id").eq("id", user["id"]).execute()
    account_id = user_row.data[0]["stripe_connect_account_id"] if user_row.data else None

    if not account_id:
        return {"has_account": False, "details_submitted": False, "payouts_enabled": False}

    stripe = get_stripe()
    try:
        account = stripe.v1.accounts.retrieve(account_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Couldn't check account status: {e}")

    return {
        "has_account": True,
        "details_submitted": account.details_submitted,
        "payouts_enabled": account.payouts_enabled,
    }


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """
    Confirms payment success asynchronously rather than trusting the
    client alone. For LOCAL testing, this endpoint needs the Stripe
    CLI (`stripe listen --forward-to localhost:8000/webhooks/stripe`)
    since Stripe's servers can't reach 127.0.0.1 directly.
    """
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    try:
        event = stripe_module.Webhook.construct_event(payload, sig_header, settings.stripe_webhook_secret)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Webhook signature verification failed: {e}")

    supabase = get_supabase()

    if event["type"] == "payment_intent.succeeded":
        payment_intent_id = event["data"]["object"]["id"]
        try:
            supabase.table("orders").update({"payment_status": "paid"}) \
                .eq("stripe_payment_intent_id", payment_intent_id).execute()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update order: {e}")

    elif event["type"] == "charge.refunded":
        payment_intent_id = event["data"]["object"]["payment_intent"]
        try:
            supabase.table("orders").update({"payment_status": "refunded"}) \
                .eq("stripe_payment_intent_id", payment_intent_id).execute()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update order: {e}")

    return {"received": True}