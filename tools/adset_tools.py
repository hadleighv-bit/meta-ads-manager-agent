"""Ad-set-level Meta Marketing API tool functions."""
from __future__ import annotations

from facebook_business.adobjects.adset import AdSet
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

_ADSET_FIELDS = [
    AdSet.Field.id,
    AdSet.Field.name,
    AdSet.Field.status,
    AdSet.Field.targeting,
    AdSet.Field.bid_amount,
    AdSet.Field.optimization_goal,
    AdSet.Field.daily_budget,
    AdSet.Field.lifetime_budget,
    AdSet.Field.campaign_id,
]


def _targeting_summary(targeting: dict | None) -> str:
    if not targeting:
        return ""
    parts = []
    if targeting.get("genders"):
        parts.append("genders=" + ",".join(str(g) for g in targeting["genders"]))
    age_min, age_max = targeting.get("age_min"), targeting.get("age_max")
    if age_min or age_max:
        parts.append(f"age={age_min}-{age_max}")
    countries = targeting.get("geo_locations", {}).get("countries", [])
    if countries:
        parts.append("countries=" + ",".join(countries))
    return "; ".join(parts)


def get_adsets(campaign_id: str) -> list[dict]:
    """Return ad sets for a campaign."""
    init_api()
    adsets = Campaign(campaign_id).get_ad_sets(fields=_ADSET_FIELDS)
    return [
        {
            "id": a.get("id"),
            "name": a.get("name"),
            "status": a.get("status"),
            "targeting_summary": _targeting_summary(a.get("targeting")),
            "bid_amount": a.get("bid_amount"),
            "optimization_goal": a.get("optimization_goal"),
            "daily_budget": a.get("daily_budget"),
            "lifetime_budget": a.get("lifetime_budget"),
        }
        for a in adsets
    ]


def get_adset_insights(adset_id: str, date_preset: str = "last_7d") -> dict:
    """Return aggregated performance metrics for an ad set."""
    init_api()
    params = {
        "level": "adset",
        "date_preset": DATE_PRESET_MAP.get(date_preset, "last_7_d"),
    }
    try:
        insights = AdSet(adset_id).get_insights(fields=_INSIGHT_FIELDS, params=params)
        if not insights:
            return {"adset_id": adset_id, "error": "no data"}
        row = dict(insights[0])
        return {
            "adset_id": adset_id,
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
        return {"adset_id": adset_id, "error": str(exc)}


def pause_adset(adset_id: str) -> dict:
    """Pause an ad set."""
    init_api()
    try:
        AdSet(adset_id).api_update(params={AdSet.Field.status: AdSet.Status.paused})
        return {"adset_id": adset_id, "status": "PAUSED", "success": True}
    except Exception as exc:
        return {"adset_id": adset_id, "success": False, "error": str(exc)}


def update_adset_budget(adset_id: str, new_budget: float) -> dict:
    """Set a new daily budget (dollars) on an ad set."""
    init_api()
    try:
        AdSet(adset_id).api_update(
            params={AdSet.Field.daily_budget: int(new_budget * 100)}
        )
        return {"adset_id": adset_id, "new_daily_budget": new_budget, "success": True}
    except Exception as exc:
        return {"adset_id": adset_id, "success": False, "error": str(exc)}


def duplicate_adset(adset_id: str, new_name: str) -> dict:
    """Duplicate an ad set with a new name."""
    init_api()
    try:
        adset = AdSet(adset_id)
        result = adset.create_copy(
            params={
                "rename_options": {"rename_prefix": "", "rename_suffix": ""},
                "campaign_id": adset.get("campaign_id"),
            }
        )
        new_id = (result.get("ad_object_ids", [{}])[0].get("id") if result else None)
        if new_id:
            AdSet(new_id).api_update(params={AdSet.Field.name: new_name})
        return {"original_adset_id": adset_id, "new_adset_id": new_id, "new_name": new_name, "success": True}
    except Exception as exc:
        return {"adset_id": adset_id, "success": False, "error": str(exc)}
