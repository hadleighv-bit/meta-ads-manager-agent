"""
Core Claude-powered Meta Ads Manager agent.

Runs an agentic loop that:
1. Asks Claude to analyse the Meta ad account
2. Claude calls Meta API tools to gather data
3. Claude evaluates metrics against thresholds
4. Claude surfaces prioritised recommendations
5. Optionally applies automated actions (pause / budget changes)
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import anthropic
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from config.settings import settings
from tools.meta_api import dispatch_tool
from tools.tool_definitions import TOOL_DEFINITIONS

console = Console()

MODEL = "claude-sonnet-4-6"

SYSTEM_PROMPT = """You are an expert Meta (Facebook) Ads performance analyst and media buyer.

Your job is to analyse an ad account's performance, identify issues, and make data-driven recommendations.

## Workflow
1. Start by fetching campaigns and their insights for the last 7 days.
2. Drill down into ad sets and ads that need attention.
3. Flag any metrics that breach the performance thresholds below.
4. Provide a prioritised list of recommended actions.
5. Where appropriate, take automated actions (pause underperforming ad sets, adjust budgets).

## Performance Thresholds
- Minimum ROAS: {min_roas}x
- Maximum CPM: ${max_cpm}
- Maximum CPC: ${max_cpc}
- Minimum CTR: {min_ctr}%
- Frequency cap: {frequency_cap}
- Budget burn rate warning: {burn_rate:.0%}

## Output Format
Structure your final response as:
1. **Account Summary** – top-level KPIs
2. **Issues Found** – breaches of thresholds with severity (HIGH / MEDIUM / LOW)
3. **Recommendations** – prioritised action list
4. **Actions Taken** – any automated changes made (pauses, budget adjustments)

Be concise, specific, and data-driven. Always cite metric values when raising an issue.
"""


class MetaAdsAgent:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def run(self) -> str:
        """Run one full analysis cycle. Returns the final report text."""
        console.print(
            Panel.fit(
                f"[bold cyan]Meta Ads Manager Agent[/bold cyan]\n"
                f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  |  "
                f"dry_run={self.dry_run}[/dim]",
                border_style="cyan",
            )
        )

        system = SYSTEM_PROMPT.format(
            min_roas=settings.min_roas,
            max_cpm=settings.max_cpm,
            max_cpc=settings.max_cpc,
            min_ctr=settings.min_ctr,
            frequency_cap=settings.frequency_cap,
            burn_rate=settings.budget_burn_rate_warning,
        )

        messages: list[dict] = [
            {
                "role": "user",
                "content": (
                    "Please analyse the Meta ad account now. "
                    "Fetch the data you need, identify performance issues, "
                    "and provide a full report with recommendations."
                    + (" Do NOT take any mutating actions (dry run mode)." if self.dry_run else "")
                ),
            }
        ]

        final_text = self._agentic_loop(system=system, messages=messages)
        self._save_report(final_text)
        return final_text

    # ------------------------------------------------------------------
    # Agentic loop
    # ------------------------------------------------------------------

    def _agentic_loop(self, system: str, messages: list[dict]) -> str:
        """Drive the Claude tool-use loop until a final text response."""
        iteration = 0

        while True:
            iteration += 1

            with Progress(
                SpinnerColumn(),
                TextColumn(f"[cyan]Calling Claude (turn {iteration})…"),
                transient=True,
                console=console,
            ) as progress:
                progress.add_task("")
                response = self.client.messages.create(
                    model=MODEL,
                    max_tokens=4096,
                    system=system,
                    tools=TOOL_DEFINITIONS,
                    messages=messages,
                )

            # Append assistant turn
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                # Extract the final text
                final_text = "\n\n".join(
                    block.text
                    for block in response.content
                    if hasattr(block, "text")
                )
                console.print(Panel(Markdown(final_text), title="Agent Report", border_style="green"))
                return final_text

            if response.stop_reason == "tool_use":
                tool_results = self._handle_tool_calls(response.content)
                messages.append({"role": "user", "content": tool_results})
                continue

            # Unexpected stop reason
            console.print(f"[yellow]Unexpected stop_reason: {response.stop_reason}[/yellow]")
            break

        return ""

    # ------------------------------------------------------------------
    # Tool call handling
    # ------------------------------------------------------------------

    def _handle_tool_calls(
        self, content_blocks: list[Any]
    ) -> list[dict]:
        """Execute all tool_use blocks and return tool_result content."""
        results = []

        for block in content_blocks:
            if block.type != "tool_use":
                continue

            tool_name = block.name
            tool_input = block.input
            tool_use_id = block.id

            console.print(
                f"  [bold yellow]→ Tool:[/bold yellow] [white]{tool_name}[/white] "
                f"[dim]{json.dumps(tool_input, default=str)}[/dim]"
            )

            # Gate mutating tools in dry-run mode
            if self.dry_run and tool_name in ("pause_adset", "adjust_budget"):
                result_content = {
                    "dry_run": True,
                    "message": f"Dry run: would have called {tool_name} with {tool_input}",
                }
                console.print(f"  [dim]  (skipped – dry run)[/dim]")
            else:
                try:
                    result_content = dispatch_tool(tool_name, tool_input)
                    self._print_tool_result(tool_name, result_content)
                except Exception as exc:
                    result_content = {"error": str(exc)}
                    console.print(f"  [red]  Error: {exc}[/red]")

            results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use_id,
                    "content": json.dumps(result_content, default=str),
                }
            )

        return results

    # ------------------------------------------------------------------
    # Pretty-print tool results
    # ------------------------------------------------------------------

    def _print_tool_result(self, tool_name: str, result: Any) -> None:
        if not isinstance(result, list) or not result:
            return

        if tool_name in ("get_campaigns", "get_adsets", "get_ads"):
            table = Table(show_header=True, header_style="bold magenta", show_lines=False)
            first = result[0]
            for key in list(first.keys())[:6]:  # cap columns for readability
                table.add_column(key, overflow="fold")
            for row in result[:10]:
                table.add_row(*[str(row.get(k, "")) for k in list(first.keys())[:6]])
            console.print(table)

        elif tool_name == "get_insights":
            table = Table(show_header=True, header_style="bold blue", show_lines=False)
            metric_keys = ["campaign_name", "adset_name", "spend", "impressions", "cpm", "cpc", "ctr", "frequency", "roas"]
            for key in metric_keys:
                table.add_column(key, overflow="fold")
            for row in result[:15]:
                table.add_row(*[str(row.get(k, "")) for k in metric_keys])
            console.print(table)

    # ------------------------------------------------------------------
    # Report persistence
    # ------------------------------------------------------------------

    def _save_report(self, text: str) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"report_{timestamp}.md"
        report_path.write_text(text)
        console.print(f"\n[dim]Report saved to {report_path}[/dim]")
