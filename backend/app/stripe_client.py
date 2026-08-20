from stripe import StripeClient

from app.config import settings


def get_stripe() -> StripeClient:
    """
    Uses the StripeClient + .v1 namespace pattern deliberately --
    the older global stripe.api_key = "..." style is deprecated in
    all current Stripe SDKs (confirmed directly against the installed
    library, not just docs, since docs and blog posts disagreed on
    whether the .v1 prefix is required -- it is).
    """
    return StripeClient(settings.stripe_secret_key)
