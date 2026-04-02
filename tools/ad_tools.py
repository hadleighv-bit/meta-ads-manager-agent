"""Ad-level Meta Marketing API tool functions."""
from __future__ import annotations

from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adset import AdSet

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

_AD_FIELDS = [
    Ad.Field.id,
    Ad.Field.name,
    Ad.Field.status,
    Ad.Field.adset_id,
    Ad.Field.campaign_id,
    Ad.Field.creative,
]


def get_ads(adset_id: str) -> list[dict]:
    """Return ads for an ad set."""
    init_api()
    ads = AdSet(adset_id).get_ads(fields=_AD_FIELDS)
    return [
        {
            "id": a.get("id"),
            "name": a.get("name"),
            "status": a.get("status"),
            "creative_id": (a.get("creative") or {}).get("id"),
        }
        for a in ads
    ]


def get_ad_insights(ad_id: str, date_preset: str = "last_7d") -> dict:
    """Return aggregated performance metrics for an ad."""
    init_api()
    params = {
        "level": "ad",
        "date_preset": DATE_PRESET_MAP.get(date_preset, "last_7_d"),
    }
    try:
        insights = Ad(ad_id).get_insights(fields=_INSIGHT_FIELDS, params=params)
        if not insights:
            return {"ad_id": ad_id, "error": "no data"}
        row = dict(insights[0])
        return {
            "ad_id": ad_id,
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
        return {"ad_id": ad_id, "error": str(exc)}


def pause_ad(ad_id: str) -> dict:
    """Pause an ad."""
    init_api()
    try:
        Ad(ad_id).api_update(params={Ad.Field.status: Ad.Status.paused})
        return {"ad_id": ad_id, "status": "PAUSED", "success": True}
    except Exception as exc:
        return {"ad_id": ad_id, "success": False, "error": str(exc)}
