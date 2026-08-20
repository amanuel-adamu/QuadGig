import os

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_fake")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_fake")

import pytest
from pydantic import ValidationError

from fastapi.testclient import TestClient
from app.main import app
from app.listings import ListingCreate

client = TestClient(app)


def test_create_listing_requires_auth():
    response = client.post("/listings", json={
        "title": "Calc tutoring",
        "price_cents": 2000,
        "category": "tutoring",
    })
    assert response.status_code == 401


def test_create_listing_rejects_malformed_auth_header():
    response = client.post(
        "/listings",
        json={"title": "Calc tutoring", "price_cents": 2000, "category": "tutoring"},
        headers={"Authorization": "not-a-bearer-token"},
    )
    assert response.status_code == 401


def test_listing_create_model_rejects_zero_price():
    with pytest.raises(ValidationError):
        ListingCreate(title="Calc tutoring", price_cents=0, category="tutoring")


def test_listing_create_model_accepts_valid_input():
    listing = ListingCreate(title="Calc tutoring", price_cents=2000, category="tutoring")
    assert listing.price_cents == 2000


def test_browse_listings_does_not_require_auth():
    response = client.get("/listings")
    assert response.status_code == 502


def test_create_order_requires_auth():
    response = client.post("/orders", json={"listing_id": "some-id"})
    assert response.status_code == 401


def test_update_order_status_requires_auth():
    response = client.patch("/orders/some-id", json={"status": "accepted"})
    assert response.status_code == 401
