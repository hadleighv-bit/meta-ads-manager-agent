"""
Meta Marketing API tool functions (generic / legacy interface).

The newer, split modules (campaign_tools, adset_tools, ad_tools, account_tools)
are preferred for new code. This module is kept for backwards compatibility
with agent/agent.py and the original TOOL_DEFINITIONS schema.
"""
from __future__ import annotations

from typing import Any

from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.ad import Ad

from config.settings import settings
from tools._shared import DATE_PRESET_MAP, extract_roas, init_api

_INSIGHT_FIELDS = [
    "campaign_id", "campaign_name",
    "adset_id", "adset_name",
    "ad_id", "ad_name",
    "impressions", "clicks", "spend",
    "cpm", "cpc", "ctr",
    "frequency", "reach",
    "actions", "action_values",
    "cost_per_action_type", "purchase_roas",
]

_LEVEL_MAP = {"account": "account", "campaign": "campaign", "adset": "adset", "ad": "ad"}


def _account() -> AdAccount:
    return AdAccount(settings.meta_ad_account_id)


# ---------------------------------------------------------------------------
# Public functions (used by agent/agent.py via TOOL_DEFINITIONS)
# ---------------------------------------------------------------------------

def get_campaigns(status_filter: str = "ALL") -> list[dict]:
    init_api()
    fields = [
        Campaign.Field.id, Campaign.Field.name, Campaign.Field.status,
        Campaign.Field.objective, Campaign.Field.daily_budget,
        Campaign.Field.lifetime_budget, Campaign.Field.start_time, Campaign.Field.stop_time,
    ]
    params: dict[str, Any] = {}
    if status_filter != "ALL":
        params["effective_status"] = [status_filter]
    return [dict(c) for c in _account().get_campaigns(fields=fields, params=params)]


def get_adsets(campaign_id: str | None = None, status_filter: str = "ALL") -> list[dict]:
    init_api()
    fields = [
        AdSet.Field.id, AdSet.Field.name, AdSet.Field.status, AdSet.Field.campaign_id,
        AdSet.Field.daily_budget, AdSet.Field.lifetime_budget, AdSet.Field.bid_strategy,
        AdSet.Field.bid_amount, AdSet.Field.targeting, AdSet.Field.optimization_goal,
    ]
    params: dict[str, Any] = {}
    if status_filter != "ALL":
        params["effective_status"] = [status_filter]
    source = Campaign(campaign_id) if campaign_id else _account()
    return [dict(a) for a in source.get_ad_sets(fields=fields, params=params)]


def get_ads(adset_id: str | None = None, campaign_id: str | None = None, status_filter: str = "ALL") -> list[dict]:
    init_api()
    fields = [
        Ad.Field.id, Ad.Field.name, Ad.Field.status, Ad.Field.adset_id,
        Ad.Field.campaign_id, Ad.Field.creative,
    ]
    params: dict[str, Any] = {}
    if status_filter != "ALL":
        params["effective_status"] = [status_filter]
    if adset_id:
        source = AdSet(adset_id)
    elif campaign_id:
        source = Campaign(campaign_id)
    else:
        source = _account()
    return [dict(a) for a in source.get_ads(fields=fields, params=params)]


def get_insights(level: str, object_id: str | None = None, date_preset: str = "last_7d") -> list[dict]:
    init_api()
    params = {
        "level": _LEVEL_MAP.get(level, "campaign"),
        "date_preset": DATE_PRESET_MAP.get(date_preset, "last_7_d"),
    }
    if object_id:
        sources = {"campaign": Campaign, "adset": AdSet, "ad": Ad}
        source = sources.get(level, AdAccount)(object_id) if level in sources else _account()
    else:
        source = _account()
    rows = []
    for insight in source.get_insights(fields=_INSIGHT_FIELDS, params=params):
        row = dict(insight)
        row["roas"] = extract_roas(row.pop("purchase_roas", None))
        rows.append(row)
    return rows


def pause_adset(adset_id: str) -> dict:
    init_api()
    AdSet(adset_id).api_update(params={AdSet.Field.status: AdSet.Status.paused})
    return {"adset_id": adset_id, "status": "PAUSED", "success": True}


def adjust_budget(object_id: str, object_type: str, new_daily_budget: float) -> dict:
    init_api()
    budget_cents = int(new_daily_budget * 100)
    if object_type == "campaign":
        Campaign(object_id).api_update(params={Campaign.Field.daily_budget: budget_cents})
    else:
        AdSet(object_id).api_update(params={AdSet.Field.daily_budget: budget_cents})
    return {"object_id": object_id, "object_type": object_type, "new_daily_budget": new_daily_budget, "success": True}


# ---------------------------------------------------------------------------
# Dispatcher — used by agent/agent.py
# ---------------------------------------------------------------------------

class MetaAPITools:
    """Namespace wrapper (kept for backwards compat)."""
    get_campaigns = staticmethod(get_campaigns)
    get_adsets = staticmethod(get_adsets)
    get_ads = staticmethod(get_ads)
    get_insights = staticmethod(get_insights)
    pause_adset = staticmethod(pause_adset)
    adjust_budget = staticmethod(adjust_budget)


def dispatch_tool(tool_name: str, tool_input: dict) -> Any:
    """Route a tool call from the agent to the correct function."""
    handlers: dict[str, Any] = {
        "get_campaigns": lambda i: get_campaigns(status_filter=i.get("status_filter", "ALL")),
        "get_adsets": lambda i: get_adsets(campaign_id=i.get("campaign_id"), status_filter=i.get("status_filter", "ALL")),
        "get_ads": lambda i: get_ads(adset_id=i.get("adset_id"), campaign_id=i.get("campaign_id"), status_filter=i.get("status_filter", "ALL")),
        "get_insights": lambda i: get_insights(level=i["level"], object_id=i.get("object_id"), date_preset=i.get("date_preset", "last_7d")),
        "pause_adset": lambda i: pause_adset(adset_id=i["adset_id"]),
        "adjust_budget": lambda i: adjust_budget(object_id=i["object_id"], object_type=i["object_type"], new_daily_budget=i["new_daily_budget"]),
    }
    handler = handlers.get(tool_name)
    if handler is None:
        raise ValueError(f"Unknown tool: {tool_name}")
    return handler(tool_input)
