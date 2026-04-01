TOOL_DEFINITIONS = [
    {
        "name": "get_campaigns",
        "description": (
            "Retrieve all ad campaigns for the Meta ad account. "
            "Returns campaign IDs, names, status, objectives, and daily/lifetime budgets."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "status_filter": {
                    "type": "string",
                    "enum": ["ACTIVE", "PAUSED", "ALL"],
                    "description": "Filter campaigns by status. Defaults to ALL.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "get_adsets",
        "description": (
            "Retrieve ad sets for a given campaign or all ad sets in the account. "
            "Returns ad set IDs, names, status, targeting, budgets, and bid strategies."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {
                    "type": "string",
                    "description": "Campaign ID to filter ad sets. If omitted, returns all ad sets.",
                },
                "status_filter": {
                    "type": "string",
                    "enum": ["ACTIVE", "PAUSED", "ALL"],
                    "description": "Filter ad sets by status. Defaults to ALL.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_ads",
        "description": (
            "Retrieve individual ads for a given ad set or campaign. "
            "Returns ad IDs, names, creative details, and status."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "adset_id": {
                    "type": "string",
                    "description": "Ad set ID to filter ads. If omitted, returns all ads.",
                },
                "campaign_id": {
                    "type": "string",
                    "description": "Campaign ID to filter ads.",
                },
                "status_filter": {
                    "type": "string",
                    "enum": ["ACTIVE", "PAUSED", "ALL"],
                    "description": "Filter ads by status. Defaults to ALL.",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_insights",
        "description": (
            "Retrieve performance insights (metrics) for campaigns, ad sets, or ads. "
            "Returns ROAS, CPM, CPC, CTR, frequency, impressions, clicks, spend, and conversions "
            "for the specified date range and level of aggregation."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "object_id": {
                    "type": "string",
                    "description": "ID of the campaign, ad set, or ad to get insights for. If omitted, returns account-level insights.",
                },
                "level": {
                    "type": "string",
                    "enum": ["account", "campaign", "adset", "ad"],
                    "description": "Aggregation level for insights.",
                },
                "date_preset": {
                    "type": "string",
                    "enum": [
                        "today",
                        "yesterday",
                        "last_7d",
                        "last_14d",
                        "last_30d",
                        "this_month",
                        "last_month",
                    ],
                    "description": "Date range preset. Defaults to last_7d.",
                },
            },
            "required": ["level"],
        },
    },
    {
        "name": "pause_adset",
        "description": (
            "Pause an active ad set to stop it from spending. "
            "Use this when an ad set is underperforming based on key metrics."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "adset_id": {
                    "type": "string",
                    "description": "The ID of the ad set to pause.",
                }
            },
            "required": ["adset_id"],
        },
    },
    {
        "name": "adjust_budget",
        "description": (
            "Adjust the daily budget of a campaign or ad set. "
            "Use this to scale up strong performers or reduce spend on underperformers."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "object_id": {
                    "type": "string",
                    "description": "ID of the campaign or ad set to adjust.",
                },
                "object_type": {
                    "type": "string",
                    "enum": ["campaign", "adset"],
                    "description": "Whether the object is a campaign or ad set.",
                },
                "new_daily_budget": {
                    "type": "number",
                    "description": "New daily budget in account currency (e.g., 50.00 for $50/day).",
                },
            },
            "required": ["object_id", "object_type", "new_daily_budget"],
        },
    },
]
