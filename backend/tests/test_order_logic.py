from app.order_logic import calculate_commission, calculate_seller_payout, check_transition, should_refund


def test_commission_is_ten_percent():
    assert calculate_commission(2000) == 200


def test_commission_rounds_to_nearest_cent():
    assert calculate_commission(999) == 100


def test_seller_payout_is_price_minus_commission():
    assert calculate_seller_payout(2000, 200) == 1800


def test_seller_payout_plus_commission_equals_price():
    price = 4999
    commission = calculate_commission(price)
    payout = calculate_seller_payout(price, commission)
    assert payout + commission == price


def test_should_refund_paid_order():
    assert should_refund("paid") is True


def test_should_not_refund_pending_order():
    assert should_refund("pending") is False


def test_should_not_refund_already_refunded_order():
    assert should_refund("refunded") is False


def test_should_not_refund_failed_payment():
    assert should_refund("failed") is False


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
