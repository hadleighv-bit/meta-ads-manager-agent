"""
Ad-set-level Meta Marketing API tool functions.
"""
from __future__ import annotations

from facebook_business.adobjects.adset import AdSet
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


def _targeting_summary(targeting: dict | None) -> str:
    if not targeting:
        return ""
    parts = []
    genders = targeting.get("genders")
    if genders:
        parts.append("genders=" + ",".join(str(g) for g in genders))
    age_min = targeting.get("age_min")
    age_max = targeting.get("age_max")
    if age_min or age_max:
        parts.append(f"age={age_min}-{age_max}")
    geo = targeting.get("geo_locations", {})
    countries = geo.get("countries", [])
    if countries:
        parts.append("countries=" + ",".join(countries))
    return "; ".join(parts)


def get_adsets(campaign_id: str) -> list[dict]:
    """Return ad sets for a campaign."""
    _init_api()
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
    _init_api()
    params = {
        "level": "adset",
        "date_preset": _DATE_PRESET_MAP.get(date_preset, "last_7_d"),
    }
    try:
        insights = AdSet(adset_id).get_insights(
            fields=_INSIGHT_FIELDS, params=params
        )
        if not insights:
            return {"adset_id": adset_id, "error": "no data"}
        row = dict(insights[0])
        roas_list = row.get("purchase_roas", [])
        roas = float(roas_list[0].get("value", 0)) if roas_list else 0.0
        return {
            "adset_id": adset_id,
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
        return {"adset_id": adset_id, "error": str(exc)}


def pause_adset(adset_id: str) -> dict:
    """Pause an ad set."""
    _init_api()
    try:
        AdSet(adset_id).api_update(
            params={AdSet.Field.status: AdSet.Status.paused}
        )
        return {"adset_id": adset_id, "status": "PAUSED", "success": True}
    except Exception as exc:
        return {"adset_id": adset_id, "success": False, "error": str(exc)}


def update_adset_budget(adset_id: str, new_budget: float) -> dict:
    """Set a new daily budget (dollars) on an ad set."""
    _init_api()
    try:
        AdSet(adset_id).api_update(
            params={AdSet.Field.daily_budget: int(new_budget * 100)}
        )
        return {"adset_id": adset_id, "new_daily_budget": new_budget, "success": True}
    except Exception as exc:
        return {"adset_id": adset_id, "success": False, "error": str(exc)}


def duplicate_adset(adset_id: str, new_name: str) -> dict:
    """Duplicate an ad set with a new name."""
    _init_api()
    try:
        adset = AdSet(adset_id)
        result = adset.create_copy(
            params={
                "rename_options": {
                    "rename_prefix": "",
                    "rename_suffix": "",
                },
                "campaign_id": adset.get("campaign_id"),
            }
        )
        new_id = result.get("ad_object_ids", [{}])[0].get("id") if result else None
        if new_id:
            AdSet(new_id).api_update(params={AdSet.Field.name: new_name})
        return {
            "original_adset_id": adset_id,
            "new_adset_id": new_id,
            "new_name": new_name,
            "success": True,
        }
    except Exception as exc:
        return {"adset_id": adset_id, "success": False, "error": str(exc)}
