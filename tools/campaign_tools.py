"""Campaign-level Meta Marketing API tool functions."""
from __future__ import annotations

from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign

from config.settings import settings
from tools._shared import (
    DATE_PRESET_MAP,
    extract_purchase_value,
    extract_purchases,
    extract_roas,
    init_api,
)

_INSIGHT_FIELDS = [
    "spend", "impressions", "clicks", "ctr", "cpm", "cpc",
    "actions", "action_values", "purchase_roas", "frequency",
]

_CAMPAIGN_FIELDS = [
    Campaign.Field.id,
    Campaign.Field.name,
    Campaign.Field.status,
    Campaign.Field.objective,
    Campaign.Field.daily_budget,
    Campaign.Field.lifetime_budget,
]


def get_all_campaigns(account_id: str) -> list[dict]:
    """Return all campaigns for the given ad account."""
    init_api()
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


def get_campaign_insights(campaign_id: str, date_preset: str = "last_7d") -> dict:
    """Return aggregated performance metrics for a campaign."""
    init_api()
    params = {
        "level": "campaign",
        "date_preset": DATE_PRESET_MAP.get(date_preset, "last_7_d"),
    }
    try:
        insights = Campaign(campaign_id).get_insights(fields=_INSIGHT_FIELDS, params=params)
        if not insights:
            return {"campaign_id": campaign_id, "error": "no data"}
        row = dict(insights[0])
        return {
            "campaign_id": campaign_id,
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
        }
    except Exception as exc:
        return {"campaign_id": campaign_id, "error": str(exc)}


def pause_campaign(campaign_id: str) -> dict:
    """Pause a campaign."""
    init_api()
    try:
        Campaign(campaign_id).api_update(
            params={Campaign.Field.status: Campaign.Status.paused}
        )
        return {"campaign_id": campaign_id, "status": "PAUSED", "success": True}
    except Exception as exc:
        return {"campaign_id": campaign_id, "success": False, "error": str(exc)}


def resume_campaign(campaign_id: str) -> dict:
    """Resume a paused campaign."""
    init_api()
    try:
        Campaign(campaign_id).api_update(
            params={Campaign.Field.status: Campaign.Status.active}
        )
        return {"campaign_id": campaign_id, "status": "ACTIVE", "success": True}
    except Exception as exc:
        return {"campaign_id": campaign_id, "success": False, "error": str(exc)}


def update_campaign_budget(campaign_id: str, new_daily_budget: float) -> dict:
    """Set a new daily budget (dollars) on a campaign."""
    init_api()
    try:
        Campaign(campaign_id).api_update(
            params={Campaign.Field.daily_budget: int(new_daily_budget * 100)}
        )
        return {"campaign_id": campaign_id, "new_daily_budget": new_daily_budget, "success": True}
    except Exception as exc:
        return {"campaign_id": campaign_id, "success": False, "error": str(exc)}
