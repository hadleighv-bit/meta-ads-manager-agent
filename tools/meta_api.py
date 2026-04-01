"""
Meta Marketing API tool functions using the facebook-business SDK.
"""
from __future__ import annotations

import json
from typing import Any

from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad
from facebook_business.api import FacebookAdsApi

from config.settings import settings


def _init_api() -> None:
    FacebookAdsApi.init(
        app_id=settings.meta_app_id,
        app_secret=settings.meta_app_secret,
        access_token=settings.meta_access_token,
    )


def _account() -> AdAccount:
    return AdAccount(settings.meta_ad_account_id)


# ---------------------------------------------------------------------------
# Campaigns
# ---------------------------------------------------------------------------

def get_campaigns(status_filter: str = "ALL") -> list[dict]:
    """Return campaigns for the ad account."""
    _init_api()
    fields = [
        Campaign.Field.id,
        Campaign.Field.name,
        Campaign.Field.status,
        Campaign.Field.objective,
        Campaign.Field.daily_budget,
        Campaign.Field.lifetime_budget,
        Campaign.Field.start_time,
        Campaign.Field.stop_time,
    ]
    params: dict[str, Any] = {}
    if status_filter != "ALL":
        params["effective_status"] = [status_filter]

    campaigns = _account().get_campaigns(fields=fields, params=params)
    return [dict(c) for c in campaigns]


# ---------------------------------------------------------------------------
# Ad Sets
# ---------------------------------------------------------------------------

def get_adsets(
    campaign_id: str | None = None,
    status_filter: str = "ALL",
) -> list[dict]:
    """Return ad sets, optionally filtered by campaign."""
    _init_api()
    fields = [
        AdSet.Field.id,
        AdSet.Field.name,
        AdSet.Field.status,
        AdSet.Field.campaign_id,
        AdSet.Field.daily_budget,
        AdSet.Field.lifetime_budget,
        AdSet.Field.bid_strategy,
        AdSet.Field.bid_amount,
        AdSet.Field.targeting,
        AdSet.Field.start_time,
        AdSet.Field.end_time,
        AdSet.Field.optimization_goal,
    ]
    params: dict[str, Any] = {}
    if status_filter != "ALL":
        params["effective_status"] = [status_filter]

    if campaign_id:
        adsets = Campaign(campaign_id).get_ad_sets(fields=fields, params=params)
    else:
        adsets = _account().get_ad_sets(fields=fields, params=params)

    return [dict(a) for a in adsets]


# ---------------------------------------------------------------------------
# Ads
# ---------------------------------------------------------------------------

def get_ads(
    adset_id: str | None = None,
    campaign_id: str | None = None,
    status_filter: str = "ALL",
) -> list[dict]:
    """Return ads, optionally filtered by ad set or campaign."""
    _init_api()
    fields = [
        Ad.Field.id,
        Ad.Field.name,
        Ad.Field.status,
        Ad.Field.adset_id,
        Ad.Field.campaign_id,
        Ad.Field.creative,
        Ad.Field.created_time,
        Ad.Field.updated_time,
    ]
    params: dict[str, Any] = {}
    if status_filter != "ALL":
        params["effective_status"] = [status_filter]

    if adset_id:
        ads = AdSet(adset_id).get_ads(fields=fields, params=params)
    elif campaign_id:
        ads = Campaign(campaign_id).get_ads(fields=fields, params=params)
    else:
        ads = _account().get_ads(fields=fields, params=params)

    return [dict(a) for a in ads]


# ---------------------------------------------------------------------------
# Insights
# ---------------------------------------------------------------------------

_INSIGHT_FIELDS = [
    "campaign_id",
    "campaign_name",
    "adset_id",
    "adset_name",
    "ad_id",
    "ad_name",
    "impressions",
    "clicks",
    "spend",
    "cpm",
    "cpc",
    "ctr",
    "frequency",
    "reach",
    "actions",
    "action_values",
    "cost_per_action_type",
    "purchase_roas",
]

_LEVEL_MAP = {
    "account": "account",
    "campaign": "campaign",
    "adset": "adset",
    "ad": "ad",
}

_DATE_PRESET_MAP = {
    "today": "today",
    "yesterday": "yesterday",
    "last_7d": "last_7_d",
    "last_14d": "last_14_d",
    "last_30d": "last_30_d",
    "this_month": "this_month",
    "last_month": "last_month",
}


def get_insights(
    level: str,
    object_id: str | None = None,
    date_preset: str = "last_7d",
) -> list[dict]:
    """Return performance insights for the given level and object."""
    _init_api()
    params = {
        "level": _LEVEL_MAP.get(level, "campaign"),
        "date_preset": _DATE_PRESET_MAP.get(date_preset, "last_7_d"),
    }

    if object_id:
        if level == "campaign":
            source = Campaign(object_id)
        elif level == "adset":
            source = AdSet(object_id)
        elif level == "ad":
            source = Ad(object_id)
        else:
            source = _account()
    else:
        source = _account()

    insights = source.get_insights(fields=_INSIGHT_FIELDS, params=params)
    rows = []
    for insight in insights:
        row = dict(insight)
        # Flatten purchase_roas to a scalar
        roas_list = row.get("purchase_roas", [])
        if roas_list:
            row["roas"] = float(roas_list[0].get("value", 0))
        else:
            row["roas"] = 0.0
        row.pop("purchase_roas", None)
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# Mutations
# ---------------------------------------------------------------------------

def pause_adset(adset_id: str) -> dict:
    """Pause an active ad set."""
    _init_api()
    adset = AdSet(adset_id)
    adset.api_update(params={AdSet.Field.status: AdSet.Status.paused})
    return {"adset_id": adset_id, "status": "PAUSED", "success": True}


def adjust_budget(
    object_id: str,
    object_type: str,
    new_daily_budget: float,
) -> dict:
    """Set a new daily budget (in account currency) on a campaign or ad set."""
    _init_api()
    # Meta API expects budget in cents
    budget_cents = int(new_daily_budget * 100)

    if object_type == "campaign":
        obj = Campaign(object_id)
        obj.api_update(params={Campaign.Field.daily_budget: budget_cents})
    else:
        obj = AdSet(object_id)
        obj.api_update(params={AdSet.Field.daily_budget: budget_cents})

    return {
        "object_id": object_id,
        "object_type": object_type,
        "new_daily_budget": new_daily_budget,
        "success": True,
    }


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def dispatch_tool(tool_name: str, tool_input: dict) -> Any:
    """Route a tool call from the agent to the correct function."""
    handlers = {
        "get_campaigns": lambda i: get_campaigns(
            status_filter=i.get("status_filter", "ALL")
        ),
        "get_adsets": lambda i: get_adsets(
            campaign_id=i.get("campaign_id"),
            status_filter=i.get("status_filter", "ALL"),
        ),
        "get_ads": lambda i: get_ads(
            adset_id=i.get("adset_id"),
            campaign_id=i.get("campaign_id"),
            status_filter=i.get("status_filter", "ALL"),
        ),
        "get_insights": lambda i: get_insights(
            level=i["level"],
            object_id=i.get("object_id"),
            date_preset=i.get("date_preset", "last_7d"),
        ),
        "pause_adset": lambda i: pause_adset(adset_id=i["adset_id"]),
        "adjust_budget": lambda i: adjust_budget(
            object_id=i["object_id"],
            object_type=i["object_type"],
            new_daily_budget=i["new_daily_budget"],
        ),
    }

    handler = handlers.get(tool_name)
    if handler is None:
        raise ValueError(f"Unknown tool: {tool_name}")
    return handler(tool_input)
