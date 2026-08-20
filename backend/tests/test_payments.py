import hashlib
import hmac
import json
import os
import time

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_fake")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_fake")

WEBHOOK_SECRET = "whsec_fake"

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _sign(payload: bytes, secret: str = WEBHOOK_SECRET) -> str:
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.{payload.decode()}"
    signature = hmac.new(secret.encode(), signed_payload.encode(), hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={signature}"


def test_webhook_rejects_missing_signature():
    payload = json.dumps({"type": "payment_intent.succeeded"}).encode()
    response = client.post("/webhooks/stripe", content=payload)
    assert response.status_code == 400


def test_webhook_rejects_invalid_signature():
    payload = json.dumps({"type": "payment_intent.succeeded"}).encode()
    response = client.post(
        "/webhooks/stripe",
        content=payload,
        headers={"stripe-signature": "t=123,v1=not_a_real_signature"},
    )
    assert response.status_code == 400


def test_webhook_accepts_correctly_signed_payload():
    payload = json.dumps({
        "id": "evt_test",
        "type": "payment_intent.succeeded",
        "data": {"object": {"id": "pi_test", "amount": 2000}},
    }).encode()
    response = client.post(
        "/webhooks/stripe",
        content=payload,
        headers={"stripe-signature": _sign(payload)},
    )
    assert response.status_code == 500


def test_webhook_handles_charge_refunded_event():
    payload = json.dumps({
        "id": "evt_test_refund",
        "type": "charge.refunded",
        "data": {"object": {"id": "ch_test", "payment_intent": "pi_test"}},
    }).encode()
    response = client.post(
        "/webhooks/stripe",
        content=payload,
        headers={"stripe-signature": _sign(payload)},
    )
    assert response.status_code == 500
