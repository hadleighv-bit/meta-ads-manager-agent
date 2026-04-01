"""
Campaign-level Meta Marketing API tool functions.
"""
from __future__ import annotations

from facebook_business.adobjects.campaign import Campaign
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
]

_CAMPAIGN_FIELDS = [
    Campaign.Field.id,
    Campaign.Field.name,
    Campaign.Field.status,
    Campaign.Field.objective,
    Campaign.Field.daily_budget,
    Campaign.Field.lifetime_budget,
]

_DATE_PRESET_MAP = {
    "today": "today",
    "yesterday": "yesterday",
    "last_7d": "last_7_d",
    "last_14d": "last_14_d",
    "last_30d": "last_30_d",
    "this_month": "this_month",
    "last_month": "last_month",
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


def get_all_campaigns(account_id: str) -> list[dict]:
    """Return all campaigns for the given ad account."""
    _init_api()
    from facebook_business.adobjects.adaccount import AdAccount
    campaigns = AdAccount(account_id).get_campaigns(fields=_CAMPAIGN_FIELDS)
    return [
        {
            "id": c.get("id"),
            "name": c.get("name"),
            "status": c.get("status"),
            "objective": c.get("objective"),
            "daily_budget": c.get("daily_budget"),
            "lifetime_budget": c.get("lifetime_budget"),
        }
        for c in campaigns
    ]


def get_campaign_insights(
    campaign_id: str, date_preset: str = "last_7d"
) -> dict:
    """Return aggregated performance metrics for a campaign."""
    _init_api()
    params = {
        "level": "campaign",
        "date_preset": _DATE_PRESET_MAP.get(date_preset, "last_7_d"),
    }
    try:
        insights = Campaign(campaign_id).get_insights(
            fields=_INSIGHT_FIELDS, params=params
        )
        if not insights:
            return {"campaign_id": campaign_id, "error": "no data"}
        row = dict(insights[0])
        roas_list = row.get("purchase_roas", [])
        roas = float(roas_list[0].get("value", 0)) if roas_list else 0.0
        return {
            "campaign_id": campaign_id,
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
        }
    except Exception as exc:
        return {"campaign_id": campaign_id, "error": str(exc)}


def pause_campaign(campaign_id: str) -> dict:
    """Pause a campaign."""
    _init_api()
    try:
        Campaign(campaign_id).api_update(
            params={Campaign.Field.status: Campaign.Status.paused}
        )
        return {"campaign_id": campaign_id, "status": "PAUSED", "success": True}
    except Exception as exc:
        return {"campaign_id": campaign_id, "success": False, "error": str(exc)}


def resume_campaign(campaign_id: str) -> dict:
    """Resume a paused campaign."""
    _init_api()
    try:
        Campaign(campaign_id).api_update(
            params={Campaign.Field.status: Campaign.Status.active}
        )
        return {"campaign_id": campaign_id, "status": "ACTIVE", "success": True}
    except Exception as exc:
        return {"campaign_id": campaign_id, "success": False, "error": str(exc)}


def update_campaign_budget(campaign_id: str, new_daily_budget: float) -> dict:
    """Set a new daily budget (dollars) on a campaign."""
    _init_api()
    try:
        Campaign(campaign_id).api_update(
            params={Campaign.Field.daily_budget: int(new_daily_budget * 100)}
        )
        return {
            "campaign_id": campaign_id,
            "new_daily_budget": new_daily_budget,
            "success": True,
        }
    except Exception as exc:
        return {"campaign_id": campaign_id, "success": False, "error": str(exc)}
