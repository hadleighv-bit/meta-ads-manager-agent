"""Account-level Meta Marketing API tool functions."""
from __future__ import annotations

from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign

from tools._shared import (
    DATE_PRESET_MAP,
    extract_purchase_value,
    extract_purchases,
    extract_roas,
    init_api,
)

_INSIGHT_FIELDS = [
    "spend", "impressions", "clicks", "ctr", "cpm", "cpc",
    "actions", "action_values", "purchase_roas", "frequency", "reach",
]


def _fetch_insights(account_id: str, date_preset: str) -> dict:
    params = {
        "level": "account",
        "date_preset": DATE_PRESET_MAP.get(date_preset, "last_7_d"),
    }
    insights = AdAccount(account_id).get_insights(fields=_INSIGHT_FIELDS, params=params)
    if not insights:
        return {}
    row = dict(insights[0])
    return {
        "spend": float(row.get("spend", 0)),
        "impressions": int(row.get("impressions", 0)),
        "clicks": int(row.get("clicks", 0)),
        "ctr": float(row.get("ctr", 0)),
        "cpm": float(row.get("cpm", 0)),
        "cpc": float(row.get("cpc", 0)),
        "purchases": extract_purchases(row.get("actions")),
        "purchase_value": extract_purchase_value(row.get("action_values")),
        "roas": extract_roas(row.get("purchase_roas")),
        "frequency": float(row.get("frequency", 0)),
        "reach": int(row.get("reach", 0)),
    }


def get_account_summary(account_id: str) -> dict:
    """Return total spend, overall ROAS, active campaign count for last 7d and 30d."""
    init_api()

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
