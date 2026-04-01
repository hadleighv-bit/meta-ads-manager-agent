"""
Account-level Meta Marketing API tool functions.
"""
from __future__ import annotations

from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.api import FacebookAdsApi

from config.settings import settings

_INSIGHT_FIELDS = [
    "spend",
    "impressions",
    "clicks",
    "ctr",
    "cpm",
    "cpc",
    "actions",
    "action_values",
    "purchase_roas",
    "frequency",
    "reach",
]

_DATE_PRESET_MAP = {
    "last_7d": "last_7_d",
    "last_30d": "last_30_d",
}


def _init_api() -> None:
    FacebookAdsApi.init(
        app_id=settings.meta_app_id,
        app_secret=settings.meta_app_secret,
        access_token=settings.meta_access_token,
    )


def _extract_purchases(actions: list[dict]) -> int:
    for a in (actions or []):
        if a.get("action_type") == "purchase":
            return int(float(a.get("value", 0)))
    return 0


def _extract_purchase_value(action_values: list[dict]) -> float:
    for a in (action_values or []):
        if a.get("action_type") == "purchase":
            return float(a.get("value", 0))
    return 0.0


def _fetch_insights(account_id: str, date_preset: str) -> dict:
    from facebook_business.adobjects.campaign import Campaign
    params = {
        "level": "account",
        "date_preset": _DATE_PRESET_MAP.get(date_preset, "last_7_d"),
    }
    insights = AdAccount(account_id).get_insights(
        fields=_INSIGHT_FIELDS, params=params
    )
    if not insights:
        return {}
    row = dict(insights[0])
    roas_list = row.get("purchase_roas", [])
    roas = float(roas_list[0].get("value", 0)) if roas_list else 0.0
    return {
        "spend": float(row.get("spend", 0)),
        "impressions": int(row.get("impressions", 0)),
        "clicks": int(row.get("clicks", 0)),
        "ctr": float(row.get("ctr", 0)),
        "cpm": float(row.get("cpm", 0)),
        "cpc": float(row.get("cpc", 0)),
        "purchases": _extract_purchases(row.get("actions", [])),
        "purchase_value": _extract_purchase_value(row.get("action_values", [])),
        "roas": roas,
        "frequency": float(row.get("frequency", 0)),
        "reach": int(row.get("reach", 0)),
    }


def get_account_summary(account_id: str) -> dict:
    """Return total spend, overall ROAS, active campaign count for last 7d and 30d."""
    _init_api()
    from facebook_business.adobjects.campaign import Campaign

    # Active campaign count
    campaigns = AdAccount(account_id).get_campaigns(
        fields=[Campaign.Field.id, Campaign.Field.status],
        params={"effective_status": ["ACTIVE"]},
    )
    active_count = len(list(campaigns))

    try:
        last_7d = _fetch_insights(account_id, "last_7d")
    except Exception as exc:
        last_7d = {"error": str(exc)}

    try:
        last_30d = _fetch_insights(account_id, "last_30d")
    except Exception as exc:
        last_30d = {"error": str(exc)}

    return {
        "account_id": account_id,
        "active_campaigns": active_count,
        "last_7d": last_7d,
        "last_30d": last_30d,
    }
