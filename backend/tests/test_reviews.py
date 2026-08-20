import os

os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_fake")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_fake")

import pytest
from pydantic import ValidationError

from fastapi.testclient import TestClient
from app.main import app
from app.review_logic import calculate_average_rating
from app.reviews import ReviewCreate

client = TestClient(app)


def test_average_of_no_ratings_is_none():
    assert calculate_average_rating([]) is None


def test_average_of_one_rating():
    assert calculate_average_rating([5]) == 5.0


def test_average_rounds_to_two_decimals():
    assert calculate_average_rating([5, 4, 4]) == 4.33


def test_average_of_perfect_ratings():
    assert calculate_average_rating([5, 5, 5, 5]) == 5.0


def test_review_create_rejects_rating_above_five():
    with pytest.raises(ValidationError):
        ReviewCreate(order_id="some-id", rating=6)


def test_review_create_rejects_rating_below_one():
    with pytest.raises(ValidationError):
        ReviewCreate(order_id="some-id", rating=0)


def test_review_create_accepts_valid_rating():
    review = ReviewCreate(order_id="some-id", rating=5, comment="Great work!")
    assert review.rating == 5


def test_create_review_requires_auth():
    response = client.post("/reviews", json={"order_id": "some-id", "rating": 5})
    assert response.status_code == 401


def test_get_user_reviews_does_not_require_auth():
    response = client.get("/users/some-id/reviews")
    assert response.status_code == 502
