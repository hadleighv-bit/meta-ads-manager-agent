"""
Ad-level Meta Marketing API tool functions.
"""
from __future__ import annotations

from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adset import AdSet
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

_AD_FIELDS = [
    Ad.Field.id,
    Ad.Field.name,
    Ad.Field.status,
    Ad.Field.adset_id,
    Ad.Field.campaign_id,
    Ad.Field.creative,
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


def get_ads(adset_id: str) -> list[dict]:
    """Return ads for an ad set."""
    _init_api()
    ads = AdSet(adset_id).get_ads(fields=_AD_FIELDS)
    return [
        {
            "id": a.get("id"),
            "name": a.get("name"),
            "status": a.get("status"),
            "creative_id": (a.get("creative") or {}).get("id"),
            "creative_name": (a.get("creative") or {}).get("name"),
        }
        for a in ads
    ]


def get_ad_insights(ad_id: str, date_preset: str = "last_7d") -> dict:
    """Return aggregated performance metrics for an ad."""
    _init_api()
    params = {
        "level": "ad",
        "date_preset": _DATE_PRESET_MAP.get(date_preset, "last_7_d"),
    }
    try:
        insights = Ad(ad_id).get_insights(fields=_INSIGHT_FIELDS, params=params)
        if not insights:
            return {"ad_id": ad_id, "error": "no data"}
        row = dict(insights[0])
        roas_list = row.get("purchase_roas", [])
        roas = float(roas_list[0].get("value", 0)) if roas_list else 0.0
        return {
            "ad_id": ad_id,
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
        return {"ad_id": ad_id, "error": str(exc)}


def pause_ad(ad_id: str) -> dict:
    """Pause an ad."""
    _init_api()
    try:
        Ad(ad_id).api_update(params={Ad.Field.status: Ad.Status.paused})
        return {"ad_id": ad_id, "status": "PAUSED", "success": True}
    except Exception as exc:
        return {"ad_id": ad_id, "success": False, "error": str(exc)}
