"""
Mock Meta API data for local testing without real credentials.

Activate by setting MOCK_META=true in your .env or environment.
Covers all tool calls made by AnalysisAgent, with varied data to exercise
all three verdict paths (🔴 urgent, 🟡 watch, 🟢 healthy).

Usage:
    MOCK_META=true ANTHROPIC_API_KEY=sk-ant-... python main.py --mode report_only
"""
from __future__ import annotations

from typing import Any

# ---------------------------------------------------------------------------
# Static mock data
# ---------------------------------------------------------------------------

_CAMPAIGNS = [
    {
        "id": "mock_camp_001",
        "name": "Summer Sale — Conversions",
        "status": "ACTIVE",
        "objective": "OUTCOME_SALES",
        "daily_budget": "15000",     # $150/day
        "lifetime_budget": None,
    },
    {
        "id": "mock_camp_002",
        "name": "Brand Awareness — Prospecting",
        "status": "ACTIVE",
        "objective": "OUTCOME_AWARENESS",
        "daily_budget": "8000",      # $80/day
        "lifetime_budget": None,
    },
    {
        "id": "mock_camp_003",
        "name": "Retargeting — Cart Abandoners",
        "status": "ACTIVE",
        "objective": "OUTCOME_SALES",
        "daily_budget": "5000",      # $50/day
        "lifetime_budget": None,
    },
    {
        "id": "mock_camp_004",
        "name": "Loyalty — Repeat Buyers",
        "status": "PAUSED",
        "objective": "OUTCOME_SALES",
        "daily_budget": "3000",
        "lifetime_budget": None,
    },
]

# Campaign-level insights — last 7 days
# mock_camp_001: 🔴 ROAS 1.8x (below 3.5), high CPM, frequency over cap
# mock_camp_002: 🟡 CTR borderline, ROAS data absent (awareness campaign)
# mock_camp_003: 🟢 strong performer
# mock_camp_004: paused, no spend
_CAMPAIGN_INSIGHTS: dict[str, dict] = {
    "mock_camp_001": {
        "campaign_id": "mock_camp_001",
        "spend": 1050.00,
        "impressions": 87500,
        "clicks": 1050,
        "ctr": 1.20,
        "cpm": 12.00,
        "cpc": 1.00,
        "purchases": 30,
        "purchase_value": 1890.00,
        "roas": 1.80,
        "frequency": 5.2,
    },
    "mock_camp_002": {
        "campaign_id": "mock_camp_002",
        "spend": 560.00,
        "impressions": 112000,
        "clicks": 1120,
        "ctr": 1.00,
        "cpm": 5.00,
        "cpc": 0.50,
        "purchases": 0,
        "purchase_value": 0.00,
        "roas": 0.0,      # awareness — no purchase pixel
        "frequency": 2.1,
    },
    "mock_camp_003": {
        "campaign_id": "mock_camp_003",
        "spend": 348.00,
        "impressions": 29000,
        "clicks": 870,
        "ctr": 3.00,
        "cpm": 12.00,
        "cpc": 0.40,
        "purchases": 58,
        "purchase_value": 2088.00,
        "roas": 6.00,
        "frequency": 1.8,
    },
    "mock_camp_004": {
        "campaign_id": "mock_camp_004",
        "spend": 0.0,
        "impressions": 0,
        "clicks": 0,
        "ctr": 0.0,
        "cpm": 0.0,
        "cpc": 0.0,
        "purchases": 0,
        "purchase_value": 0.0,
        "roas": 0.0,
        "frequency": 0.0,
    },
}

# Ad sets (one set per campaign for brevity)
_ADSETS: dict[str, list[dict]] = {
    "mock_camp_001": [
        {"id": "mock_adset_001a", "name": "Broad — 25-54 US", "status": "ACTIVE", "targeting_summary": "age=25-54; countries=US", "bid_amount": None, "optimization_goal": "OFFSITE_CONVERSIONS", "daily_budget": "7500", "lifetime_budget": None},
        {"id": "mock_adset_001b", "name": "Interest — Fitness", "status": "ACTIVE", "targeting_summary": "age=18-44; countries=US", "bid_amount": None, "optimization_goal": "OFFSITE_CONVERSIONS", "daily_budget": "7500", "lifetime_budget": None},
    ],
    "mock_camp_002": [
        {"id": "mock_adset_002a", "name": "Lookalike 2% — US", "status": "ACTIVE", "targeting_summary": "age=18-65; countries=US", "bid_amount": None, "optimization_goal": "REACH", "daily_budget": "8000", "lifetime_budget": None},
    ],
    "mock_camp_003": [
        {"id": "mock_adset_003a", "name": "Cart — 3d", "status": "ACTIVE", "targeting_summary": "age=18-65; countries=US,CA", "bid_amount": None, "optimization_goal": "OFFSITE_CONVERSIONS", "daily_budget": "5000", "lifetime_budget": None},
    ],
}

_ADSET_INSIGHTS: dict[str, dict] = {
    "mock_adset_001a": {"adset_id": "mock_adset_001a", "spend": 525.00, "impressions": 43750, "clicks": 525, "ctr": 1.20, "cpm": 12.00, "cpc": 1.00, "purchases": 12, "purchase_value": 756.00, "roas": 1.44, "frequency": 5.8},
    "mock_adset_001b": {"adset_id": "mock_adset_001b", "spend": 525.00, "impressions": 43750, "clicks": 525, "ctr": 1.20, "cpm": 12.00, "cpc": 1.00, "purchases": 18, "purchase_value": 1134.00, "roas": 2.16, "frequency": 4.6},
    "mock_adset_002a": {"adset_id": "mock_adset_002a", "spend": 560.00, "impressions": 112000, "clicks": 1120, "ctr": 1.00, "cpm": 5.00, "cpc": 0.50, "purchases": 0, "purchase_value": 0.0, "roas": 0.0, "frequency": 2.1},
    "mock_adset_003a": {"adset_id": "mock_adset_003a", "spend": 348.00, "impressions": 29000, "clicks": 870, "ctr": 3.00, "cpm": 12.00, "cpc": 0.40, "purchases": 58, "purchase_value": 2088.00, "roas": 6.00, "frequency": 1.8},
}

# Ads (one per ad set)
_ADS: dict[str, list[dict]] = {
    "mock_adset_001a": [{"id": "mock_ad_001a1", "name": "Static — Product Hero", "status": "ACTIVE", "creative_id": "mock_cr_001"}],
    "mock_adset_001b": [{"id": "mock_ad_001b1", "name": "Video — 15s Testimonial", "status": "ACTIVE", "creative_id": "mock_cr_002"}],
    "mock_adset_002a": [{"id": "mock_ad_002a1", "name": "Carousel — Brand Story", "status": "ACTIVE", "creative_id": "mock_cr_003"}],
    "mock_adset_003a": [{"id": "mock_ad_003a1", "name": "Dynamic — Cart Retarget", "status": "ACTIVE", "creative_id": "mock_cr_004"}],
}

_AD_INSIGHTS: dict[str, dict] = {
    "mock_ad_001a1": {"ad_id": "mock_ad_001a1", "spend": 525.00, "impressions": 43750, "clicks": 525, "ctr": 1.20, "cpm": 12.00, "cpc": 1.00, "purchases": 12, "purchase_value": 756.00, "roas": 1.44, "frequency": 5.8},
    "mock_ad_001b1": {"ad_id": "mock_ad_001b1", "spend": 525.00, "impressions": 43750, "clicks": 525, "ctr": 1.20, "cpm": 12.00, "cpc": 1.00, "purchases": 18, "purchase_value": 1134.00, "roas": 2.16, "frequency": 4.6},
    "mock_ad_002a1": {"ad_id": "mock_ad_002a1", "spend": 560.00, "impressions": 112000, "clicks": 1120, "ctr": 1.00, "cpm": 5.00, "cpc": 0.50, "purchases": 0, "purchase_value": 0.0, "roas": 0.0, "frequency": 2.1},
    "mock_ad_003a1": {"ad_id": "mock_ad_003a1", "spend": 348.00, "impressions": 29000, "clicks": 870, "ctr": 3.00, "cpm": 12.00, "cpc": 0.40, "purchases": 58, "purchase_value": 2088.00, "roas": 6.00, "frequency": 1.8},
}

# Account-level rollup
_ACCOUNT_SUMMARY = {
    "account_id": "act_mock_account",
    "active_campaigns": 3,
    "last_7d": {
        "spend": 1958.00,
        "impressions": 228500,
        "clicks": 3040,
        "ctr": 1.33,
        "cpm": 8.57,
        "cpc": 0.64,
        "purchases": 88,
        "purchase_value": 3978.00,
        "roas": 2.03,
        "frequency": 3.1,
        "reach": 73710,
    },
    "last_30d": {
        "spend": 7830.00,
        "impressions": 915000,
        "clicks": 12175,
        "ctr": 1.33,
        "cpm": 8.56,
        "cpc": 0.64,
        "purchases": 352,
        "purchase_value": 15930.00,
        "roas": 2.03,
        "frequency": 3.4,
        "reach": 269000,
    },
}


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def dispatch_mock(tool_name: str, tool_input: dict) -> Any:
    """Return mock data for any tool call, simulating the Meta Marketing API."""

    if tool_name == "get_account_summary":
        return _ACCOUNT_SUMMARY

    if tool_name == "get_all_campaigns":
        return list(_CAMPAIGNS)

    if tool_name == "get_campaign_insights":
        cid = tool_input.get("campaign_id", "")
        return _CAMPAIGN_INSIGHTS.get(cid, {"campaign_id": cid, "error": "no mock data for this campaign"})

    if tool_name == "get_adsets":
        cid = tool_input.get("campaign_id", "")
        return _ADSETS.get(cid, [])

    if tool_name == "get_adset_insights":
        aid = tool_input.get("adset_id", "")
        return _ADSET_INSIGHTS.get(aid, {"adset_id": aid, "error": "no mock data"})

    if tool_name == "get_ads":
        aid = tool_input.get("adset_id", "")
        return _ADS.get(aid, [])

    if tool_name == "get_ad_insights":
        ad_id = tool_input.get("ad_id", "")
        return _AD_INSIGHTS.get(ad_id, {"ad_id": ad_id, "error": "no mock data"})

    # Write tools — simulate success in mock mode
    if tool_name == "pause_campaign":
        return {"campaign_id": tool_input.get("campaign_id"), "status": "PAUSED", "success": True, "mock": True}

    if tool_name == "pause_adset":
        return {"adset_id": tool_input.get("adset_id"), "status": "PAUSED", "success": True, "mock": True}

    if tool_name == "pause_ad":
        return {"ad_id": tool_input.get("ad_id"), "status": "PAUSED", "success": True, "mock": True}

    if tool_name == "update_campaign_budget":
        return {"campaign_id": tool_input.get("campaign_id"), "new_daily_budget": tool_input.get("new_daily_budget"), "success": True, "mock": True}

    if tool_name == "update_adset_budget":
        return {"adset_id": tool_input.get("adset_id"), "new_daily_budget": tool_input.get("new_budget"), "success": True, "mock": True}

    return {"error": f"No mock handler for tool: {tool_name}", "tool": tool_name, "input": tool_input}
