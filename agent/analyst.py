"""
AnalysisAgent — Claude-powered Meta Ads analysis loop.

Supports three modes:
  report_only  — analyse and report, take NO actions
  semi_auto    — analyse, propose actions, confirm each one via terminal prompt
  full_auto    — analyse and execute actions autonomously
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from config.settings import settings
from .reporter import Reporter
from tools.campaign_tools import (
    get_all_campaigns,
    get_campaign_insights,
    pause_campaign,
    resume_campaign,
    update_campaign_budget,
)
from tools.adset_tools import (
    get_adsets,
    get_adset_insights,
    pause_adset,
    update_adset_budget,
)
from tools.ad_tools import get_ads, get_ad_insights, pause_ad
from tools.account_tools import get_account_summary
from .confirmation import ActionConfirmationHandler, WRITE_TOOLS

console = Console()

_DEFAULT_MODEL = "claude-opus-4-6"  # overridable via CLAUDE_MODEL env var

AnalysisMode = Literal["report_only", "semi_auto", "full_auto"]

# ---------------------------------------------------------------------------
# Tool definitions for the analyst agent
# ---------------------------------------------------------------------------

ANALYST_TOOLS = [
    {
        "name": "get_account_summary",
        "description": (
            "Fetch high-level account KPIs (total spend, ROAS, active campaign count) "
            "for the last 7 days and last 30 days. Always call this first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_all_campaigns",
        "description": "Retrieve all campaigns with their IDs, names, status, objectives, and budgets.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_campaign_insights",
        "description": (
            "Get spend, ROAS, CPM, CPC, CTR, frequency, and purchase data for a specific campaign."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string", "description": "Campaign ID"},
                "date_preset": {
                    "type": "string",
                    "enum": ["last_7d", "last_14d", "last_30d", "today", "yesterday"],
                    "description": "Date range. Defaults to last_7d.",
                },
            },
            "required": ["campaign_id"],
        },
    },
    {
        "name": "get_adset_insights",
        "description": "Get performance metrics for a specific ad set.",
        "input_schema": {
            "type": "object",
            "properties": {
                "adset_id": {"type": "string", "description": "Ad set ID"},
                "date_preset": {
                    "type": "string",
                    "enum": ["last_7d", "last_14d", "last_30d", "today", "yesterday"],
                },
            },
            "required": ["adset_id"],
        },
    },
    {
        "name": "get_ad_insights",
        "description": "Get performance metrics for a specific ad.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ad_id": {"type": "string", "description": "Ad ID"},
                "date_preset": {
                    "type": "string",
                    "enum": ["last_7d", "last_14d", "last_30d", "today", "yesterday"],
                },
            },
            "required": ["ad_id"],
        },
    },
    {
        "name": "get_adsets",
        "description": "List all ad sets within a campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string", "description": "Campaign ID"},
            },
            "required": ["campaign_id"],
        },
    },
    {
        "name": "get_ads",
        "description": "List all ads within an ad set.",
        "input_schema": {
            "type": "object",
            "properties": {
                "adset_id": {"type": "string", "description": "Ad set ID"},
            },
            "required": ["adset_id"],
        },
    },
    {
        "name": "pause_campaign",
        "description": "Pause an active campaign to stop all spending.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string"},
                "reasoning": {"type": "string", "description": "Why this campaign should be paused."},
            },
            "required": ["campaign_id", "reasoning"],
        },
    },
    {
        "name": "pause_adset",
        "description": "Pause an active ad set.",
        "input_schema": {
            "type": "object",
            "properties": {
                "adset_id": {"type": "string"},
                "reasoning": {"type": "string", "description": "Why this ad set should be paused."},
            },
            "required": ["adset_id", "reasoning"],
        },
    },
    {
        "name": "pause_ad",
        "description": "Pause an individual ad.",
        "input_schema": {
            "type": "object",
            "properties": {
                "ad_id": {"type": "string"},
                "reasoning": {"type": "string", "description": "Why this ad should be paused."},
            },
            "required": ["ad_id", "reasoning"],
        },
    },
    {
        "name": "update_campaign_budget",
        "description": "Update the daily budget of a campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string"},
                "new_daily_budget": {
                    "type": "number",
                    "description": "New daily budget in dollars.",
                },
                "reasoning": {"type": "string", "description": "Why the budget is being changed."},
            },
            "required": ["campaign_id", "new_daily_budget", "reasoning"],
        },
    },
    {
        "name": "update_adset_budget",
        "description": "Update the daily budget of an ad set.",
        "input_schema": {
            "type": "object",
            "properties": {
                "adset_id": {"type": "string"},
                "new_budget": {
                    "type": "number",
                    "description": "New daily budget in dollars.",
                },
                "reasoning": {"type": "string", "description": "Why the budget is being changed."},
            },
            "required": ["adset_id", "new_budget", "reasoning"],
        },
    },
]

# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT_TEMPLATE = """You are a senior Meta (Facebook) Ads performance analyst and media buyer.

## Your Mission
Thoroughly analyse the ad account, identify performance issues, diagnose root causes, and take or recommend corrective actions.

## Analysis Workflow
1. **Start with `get_account_summary`** — understand the overall health of the account.
2. **Fetch all campaigns with `get_all_campaigns`** — identify active ones.
3. **Drill into each active campaign** using `get_campaign_insights` (last 7 days).
4. For any campaign with **ROAS below {min_roas}x**, high CPM/CPC, or spend anomalies:
   - Fetch ad sets with `get_adsets` and their insights with `get_adset_insights`.
   - For problematic ad sets, fetch ads with `get_ads` and `get_ad_insights`.
5. **Diagnose root causes**: creative fatigue (high frequency), audience exhaustion, bid issues, poor targeting.
6. **Take or propose corrective actions**:
   - Pause campaigns/ad sets/ads that are irredeemably underperforming.
   - Adjust budgets: scale up winners (ROAS > {min_roas}x), reduce spend on losers.
   - Flag creative fatigue (frequency > {frequency_cap}).

## Performance Thresholds
| Metric | Threshold |
|--------|-----------|
| Min ROAS | {min_roas}x |
| Max CPM | ${max_cpm} |
| Max CPC | ${max_cpc} |
| Min CTR | {min_ctr}% |
| Frequency cap | {frequency_cap} |
| Budget burn rate warning | {burn_rate:.0%} |

## Mode
{mode_instruction}

## Final Report Format
Structure your final response as Markdown with these sections:
1. **Executive Summary** — 3-5 bullet KPIs
2. **Issues Found** — table with: Entity | Metric | Value | Threshold | Severity (HIGH/MEDIUM/LOW)
3. **Root Cause Analysis** — concise explanation per issue
4. **Actions Taken / Recommended** — numbered priority list
5. **Budget Reallocation Opportunities** — where to move spend

Be specific: always cite actual metric values. Do not speculate without data.
"""

_MODE_INSTRUCTIONS = {
    "report_only": (
        "You are in REPORT ONLY mode. Do NOT call any write tools (pause_*, update_*). "
        "Only gather data and produce a recommendations report."
    ),
    "semi_auto": (
        "You are in SEMI-AUTO mode. You MAY call write tools (pause_*, update_*). "
        "Each write action will be intercepted and presented to the human for approval before execution."
    ),
    "full_auto": (
        "You are in FULL AUTO mode. You MAY call write tools (pause_*, update_*) and they will "
        "execute immediately. Use your best judgement. Prefer pausing over deleting. "
        "Do not change budgets by more than 30% in a single step."
    ),
}


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

def _dispatch(tool_name: str, tool_input: dict) -> Any:
    if settings.mock_meta:
        from tools.mock_meta_api import dispatch_mock
        return dispatch_mock(tool_name, tool_input)

    handlers: dict[str, Any] = {
        "get_account_summary": lambda i: get_account_summary(settings.meta_ad_account_id),
        "get_all_campaigns": lambda i: get_all_campaigns(settings.meta_ad_account_id),
        "get_campaign_insights": lambda i: get_campaign_insights(
            i["campaign_id"], i.get("date_preset", "last_7d")
        ),
        "get_adset_insights": lambda i: get_adset_insights(
            i["adset_id"], i.get("date_preset", "last_7d")
        ),
        "get_ad_insights": lambda i: get_ad_insights(
            i["ad_id"], i.get("date_preset", "last_7d")
        ),
        "get_adsets": lambda i: get_adsets(i["campaign_id"]),
        "get_ads": lambda i: get_ads(i["adset_id"]),
        "pause_campaign": lambda i: pause_campaign(i["campaign_id"]),
        "pause_adset": lambda i: pause_adset(i["adset_id"]),
        "pause_ad": lambda i: pause_ad(i["ad_id"]),
        "update_campaign_budget": lambda i: update_campaign_budget(
            i["campaign_id"], i["new_daily_budget"]
        ),
        "update_adset_budget": lambda i: update_adset_budget(
            i["adset_id"], i["new_budget"]
        ),
    }
    handler = handlers.get(tool_name)
    if handler is None:
        raise ValueError(f"Unknown tool: {tool_name}")
    return handler(tool_input)


# ---------------------------------------------------------------------------
# AnalysisAgent
# ---------------------------------------------------------------------------

class AnalysisAgent:
    def __init__(self) -> None:
        self.model: str = settings.claude_model  # resolved at instantiation time (after .env load)
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        # Accumulated during a run for the reporter scorecard
        self._campaigns: dict[str, dict] = {}       # campaign_id -> campaign row
        self._campaign_insights: dict[str, dict] = {}  # campaign_id -> insights row

    def run_analysis(self, mode: AnalysisMode = "report_only") -> str:
        """Run a full analysis cycle in the given mode."""
        self._campaigns = {}
        self._campaign_insights = {}
        console.print(
            Panel.fit(
                f"[bold cyan]Meta Ads Analyst[/bold cyan]  [dim]mode={mode}[/dim]\n"
                f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
                border_style="cyan",
            )
        )

        system = _SYSTEM_PROMPT_TEMPLATE.format(
            min_roas=settings.min_roas,
            max_cpm=settings.max_cpm,
            max_cpc=settings.max_cpc,
            min_ctr=settings.min_ctr,
            frequency_cap=settings.frequency_cap,
            burn_rate=settings.budget_burn_rate_warning,
            mode_instruction=_MODE_INSTRUCTIONS[mode],
        )

        messages: list[dict] = [
            {
                "role": "user",
                "content": (
                    "Please analyse the Meta ad account now. "
                    "Start with the account summary, then drill down as needed. "
                    "Produce a full structured report at the end."
                ),
            }
        ]

        confirmation_handler = (
            ActionConfirmationHandler(_dispatch) if mode == "semi_auto" else None
        )

        final_text = self._loop(
            system=system,
            messages=messages,
            mode=mode,
            confirmation_handler=confirmation_handler,
        )

        campaign_metrics = self._build_campaign_metrics()
        Reporter(
            analysis_text=final_text,
            campaign_metrics=campaign_metrics,
            mode=mode,
        ).generate()
        return final_text

    # ------------------------------------------------------------------
    # Agentic loop
    # ------------------------------------------------------------------

    def _loop(
        self,
        system: str,
        messages: list[dict],
        mode: AnalysisMode,
        confirmation_handler: ActionConfirmationHandler | None,
    ) -> str:
        turn = 0
        while True:
            turn += 1

            with Progress(
                SpinnerColumn(),
                TextColumn(f"[cyan]Claude thinking (turn {turn})…"),
                transient=True,
                console=console,
            ) as progress:
                progress.add_task("")
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=8096,
                    system=system,
                    tools=ANALYST_TOOLS,
                    messages=messages,
                )

            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                final_text = "\n\n".join(
                    b.text for b in response.content if hasattr(b, "text")
                )
                console.print(
                    Panel(Markdown(final_text), title="Analysis Report", border_style="green")
                )
                return final_text

            if response.stop_reason == "tool_use":
                tool_results = self._handle_tools(
                    response.content, mode, confirmation_handler
                )
                messages.append({"role": "user", "content": tool_results})
                continue

            console.print(f"[yellow]Unexpected stop_reason: {response.stop_reason}[/yellow]")
            break

        return ""

    # ------------------------------------------------------------------
    # Tool dispatch
    # ------------------------------------------------------------------

    def _handle_tools(
        self,
        content_blocks: list[Any],
        mode: AnalysisMode,
        confirmation_handler: ActionConfirmationHandler | None,
    ) -> list[dict]:
        results = []

        for block in content_blocks:
            if block.type != "tool_use":
                continue

            tool_name: str = block.name
            tool_input: dict = block.input
            tool_use_id: str = block.id
            reasoning: str = tool_input.pop("reasoning", "")

            is_write = tool_name in WRITE_TOOLS

            console.print(
                f"  [bold yellow]→[/bold yellow] [white]{tool_name}[/white] "
                + (f"[dim]{json.dumps(tool_input, default=str)}[/dim]" if not is_write else "")
            )

            # report_only: block write tools
            if mode == "report_only" and is_write:
                result = {"blocked": True, "reason": "report_only mode — no actions taken"}
                console.print("  [dim](blocked — report_only)[/dim]")

            # semi_auto: route through confirmation handler
            elif mode == "semi_auto" and is_write and confirmation_handler:
                if confirmation_handler.stop_all:
                    result = {"skipped": True, "reason": "stop_all triggered"}
                else:
                    _approved, result = confirmation_handler.confirm_and_execute(
                        tool_name=tool_name,
                        tool_input=tool_input,
                        reasoning=reasoning,
                    )
                    if result is None:
                        result = {"skipped": True, "reason": "stop_all triggered"}

            # full_auto or read-only tools: execute directly
            else:
                try:
                    result = _dispatch(tool_name, tool_input)
                    self._capture_metrics(tool_name, tool_input, result)
                except Exception as exc:
                    result = {"error": str(exc)}
                    console.print(f"  [red]Error: {exc}[/red]")

            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": json.dumps(result, default=str),
                }
            )

        return results

    # ------------------------------------------------------------------
    # Metric collection
    # ------------------------------------------------------------------

    def _capture_metrics(self, tool_name: str, tool_input: dict, result: Any) -> None:
        """Store campaign list and insights as they arrive for the reporter scorecard."""
        if tool_name == "get_all_campaigns" and isinstance(result, list):
            for c in result:
                cid = c.get("id")
                if cid:
                    self._campaigns[cid] = c
        elif tool_name == "get_campaign_insights" and isinstance(result, dict) and "error" not in result:
            cid = tool_input.get("campaign_id") or result.get("campaign_id")
            if cid:
                self._campaign_insights[cid] = result

    def _build_campaign_metrics(self) -> list[dict]:
        """Merge campaign list + insights into rows for the reporter."""
        rows: list[dict] = []
        for cid, campaign in self._campaigns.items():
            insights = self._campaign_insights.get(cid, {})
            rows.append({
                "campaign_id": cid,
                "name": campaign.get("name", cid),
                "status": campaign.get("status", "—"),
                "spend": insights.get("spend", 0),
                "roas": insights.get("roas", 0),
                "ctr": insights.get("ctr", 0),
                "cpc": insights.get("cpc", 0),
                "cpm": insights.get("cpm", 0),
                "frequency": insights.get("frequency", 0),
            })
        # Also include any insights for campaigns not yet in the list
        for cid, insights in self._campaign_insights.items():
            if cid not in self._campaigns:
                rows.append({
                    "campaign_id": cid,
                    "name": cid,
                    "status": "—",
                    **{k: insights.get(k, 0) for k in ("spend", "roas", "ctr", "cpc", "cpm", "frequency")},
                })
        return rows
