"""
Shared utilities used by all Meta API tool modules.
Centralises the API init call, date-preset mapping, and insight field helpers.
"""
from __future__ import annotations

from facebook_business.api import FacebookAdsApi

from config.settings import settings

# ---------------------------------------------------------------------------
# Date preset mapping  (our keys → Meta API values)
# ---------------------------------------------------------------------------

DATE_PRESET_MAP: dict[str, str] = {
    "today": "today",
    "yesterday": "yesterday",
    "last_7d": "last_7_d",
    "last_14d": "last_14_d",
    "last_30d": "last_30_d",
    "this_month": "this_month",
    "last_month": "last_month",
}


# ---------------------------------------------------------------------------
# API initialisation
# ---------------------------------------------------------------------------

def init_api() -> None:
    """Initialise the facebook-business SDK with credentials from settings."""
    FacebookAdsApi.init(
        app_id=settings.meta_app_id,
        app_secret=settings.meta_app_secret,
        access_token=settings.meta_access_token,
    )


# ---------------------------------------------------------------------------
# Insight field helpers
# ---------------------------------------------------------------------------

def extract_purchases(actions: list[dict] | None) -> int:
    """Return the purchase count from a Meta API `actions` list."""
    for a in (actions or []):
        if a.get("action_type") == "purchase":
            return int(float(a.get("value", 0)))
    return 0


def extract_purchase_value(action_values: list[dict] | None) -> float:
    """Return the total purchase value from a Meta API `action_values` list."""
    for a in (action_values or []):
        if a.get("action_type") == "purchase":
            return float(a.get("value", 0))
    return 0.0


def extract_roas(purchase_roas: list[dict] | None) -> float:
    """Return ROAS scalar from a Meta API `purchase_roas` list."""
    if purchase_roas:
        return float(purchase_roas[0].get("value", 0))
    return 0.0
