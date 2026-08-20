from app.order_logic import calculate_commission, check_transition


def test_commission_is_ten_percent():
    assert calculate_commission(2000) == 200


def test_commission_rounds_to_nearest_cent():
    assert calculate_commission(999) == 100  # 99.9 rounds to 100


def test_seller_can_accept_a_request():
    assert check_transition("requested", "accepted", is_buyer=False, is_seller=True) is None


def test_buyer_cannot_accept_a_request():
    error = check_transition("requested", "accepted", is_buyer=True, is_seller=False)
    assert error is not None
    assert "seller" in error.lower()


def test_buyer_can_confirm_delivery():
    assert check_transition("delivered", "confirmed", is_buyer=True, is_seller=False) is None


def test_seller_cannot_confirm_delivery():
    error = check_transition("delivered", "confirmed", is_buyer=False, is_seller=True)
    assert error is not None
    assert "buyer" in error.lower()


def test_either_party_can_cancel_a_request():
    assert check_transition("requested", "cancelled", is_buyer=True, is_seller=False) is None
    assert check_transition("requested", "cancelled", is_buyer=False, is_seller=True) is None


def test_cannot_skip_straight_to_delivered():
    error = check_transition("requested", "delivered", is_buyer=False, is_seller=True)
    assert error is not None
    assert "requested" in error and "delivered" in error


def test_cannot_reopen_a_confirmed_order():
    error = check_transition("confirmed", "disputed", is_buyer=True, is_seller=False)
    assert error is not None
