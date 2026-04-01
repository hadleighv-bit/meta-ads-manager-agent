"""
ActionConfirmationHandler — used in semi_auto mode.

Intercepts write tool calls, shows a rich summary to the terminal,
prompts the user for approval, and logs the outcome to reports/action_log.csv.
"""
from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

_LOG_PATH = Path("reports/action_log.csv")
_LOG_HEADERS = [
    "timestamp",
    "tool",
    "entity_id",
    "entity_name",
    "current_value",
    "proposed_value",
    "reasoning",
    "decision",
]

# Tools that mutate state and require confirmation
WRITE_TOOLS = {
    "pause_campaign",
    "pause_adset",
    "pause_ad",
    "update_campaign_budget",
    "update_adset_budget",
}


def _ensure_log() -> None:
    _LOG_PATH.parent.mkdir(exist_ok=True)
    if not _LOG_PATH.exists():
        with open(_LOG_PATH, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=_LOG_HEADERS).writeheader()


def _log_action(
    tool: str,
    entity_id: str,
    entity_name: str,
    current_value: str,
    proposed_value: str,
    reasoning: str,
    decision: str,
) -> None:
    _ensure_log()
    with open(_LOG_PATH, "a", newline="") as f:
        csv.DictWriter(f, fieldnames=_LOG_HEADERS).writerow(
            {
                "timestamp": datetime.now().isoformat(),
                "tool": tool,
                "entity_id": entity_id,
                "entity_name": entity_name,
                "current_value": current_value,
                "proposed_value": proposed_value,
                "reasoning": reasoning,
                "decision": decision,
            }
        )


class ActionConfirmationHandler:
    """
    Wraps a tool-dispatch callable to intercept write tools in semi_auto mode.

    Usage:
        handler = ActionConfirmationHandler(dispatch_fn)
        result = handler.confirm_and_execute(tool_name, tool_input, reasoning)
        # result is (execute: bool, stop_all: bool)
    """

    def __init__(self, dispatch_fn: Any) -> None:
        self._dispatch = dispatch_fn
        self._stop_all = False

    @property
    def stop_all(self) -> bool:
        return self._stop_all

    def confirm_and_execute(
        self,
        tool_name: str,
        tool_input: dict,
        reasoning: str = "",
        entity_name: str = "",
    ) -> tuple[bool, Any]:
        """
        Show confirmation prompt and execute (or skip) the action.

        Returns (approved: bool, result: Any).
        If stop_all was triggered, approved=False and result=None.
        """
        if self._stop_all:
            return False, None

        if tool_name not in WRITE_TOOLS:
            # Read-only tool — execute without confirmation
            result = self._dispatch(tool_name, tool_input)
            return True, result

        # Build display values
        entity_id, current_value, proposed_value = self._parse_values(
            tool_name, tool_input
        )

        self._print_summary(
            tool_name=tool_name,
            entity_id=entity_id,
            entity_name=entity_name,
            current_value=current_value,
            proposed_value=proposed_value,
            reasoning=reasoning,
        )

        decision = self._prompt_user()

        if decision == "stop":
            self._stop_all = True
            _log_action(tool_name, entity_id, entity_name, current_value, proposed_value, reasoning, "STOP_ALL")
            console.print("[bold red]Stopping all further actions.[/bold red]")
            return False, None

        if decision == "skip":
            _log_action(tool_name, entity_id, entity_name, current_value, proposed_value, reasoning, "SKIPPED")
            console.print("[yellow]  Skipped.[/yellow]")
            return False, {"skipped": True, "tool": tool_name}

        # Approved
        try:
            result = self._dispatch(tool_name, tool_input)
            _log_action(tool_name, entity_id, entity_name, current_value, proposed_value, reasoning, "APPROVED")
            console.print("[green]  Approved and executed.[/green]")
            return True, result
        except Exception as exc:
            _log_action(tool_name, entity_id, entity_name, current_value, proposed_value, reasoning, f"ERROR: {exc}")
            console.print(f"[red]  Execution error: {exc}[/red]")
            return False, {"error": str(exc)}

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_values(tool_name: str, tool_input: dict) -> tuple[str, str, str]:
        """Extract (entity_id, current_value, proposed_value) for display."""
        if tool_name in ("pause_campaign", "resume_campaign"):
            eid = tool_input.get("campaign_id", "")
            current = "ACTIVE" if tool_name == "pause_campaign" else "PAUSED"
            proposed = "PAUSED" if tool_name == "pause_campaign" else "ACTIVE"
        elif tool_name == "pause_adset":
            eid = tool_input.get("adset_id", "")
            current, proposed = "ACTIVE", "PAUSED"
        elif tool_name == "pause_ad":
            eid = tool_input.get("ad_id", "")
            current, proposed = "ACTIVE", "PAUSED"
        elif tool_name == "update_campaign_budget":
            eid = tool_input.get("campaign_id", "")
            current = "current budget"
            proposed = f"${tool_input.get('new_daily_budget', '?')}/day"
        elif tool_name == "update_adset_budget":
            eid = tool_input.get("adset_id", "")
            current = "current budget"
            proposed = f"${tool_input.get('new_budget', '?')}/day"
        else:
            eid = json.dumps(tool_input)
            current, proposed = "", ""
        return eid, current, proposed

    @staticmethod
    def _print_summary(
        tool_name: str,
        entity_id: str,
        entity_name: str,
        current_value: str,
        proposed_value: str,
        reasoning: str,
    ) -> None:
        table = Table(show_header=False, box=None, padding=(0, 1))
        table.add_column("key", style="bold cyan", no_wrap=True)
        table.add_column("value")
        table.add_row("Action", tool_name)
        table.add_row("Entity", f"{entity_name} ({entity_id})" if entity_name else entity_id)
        if current_value:
            table.add_row("Current", current_value)
        if proposed_value:
            table.add_row("Proposed", proposed_value)
        if reasoning:
            table.add_row("Reason", reasoning)

        console.print(
            Panel(
                table,
                title="[bold yellow]Confirm Action[/bold yellow]",
                border_style="yellow",
            )
        )

    @staticmethod
    def _prompt_user() -> str:
        """Return 'approve', 'skip', or 'stop'."""
        while True:
            try:
                choice = console.input(
                    "  [[bold green]A[/bold green]]pprove  "
                    "[[bold yellow]S[/bold yellow]]kip  "
                    "s[[bold red]T[/bold red]]op all  → "
                ).strip().lower()
            except (EOFError, KeyboardInterrupt):
                return "stop"

            if choice in ("a", "approve", ""):
                return "approve"
            if choice in ("s", "skip"):
                return "skip"
            if choice in ("t", "stop", "st"):
                return "stop"
            console.print("[dim]  Please enter A, S, or T.[/dim]")
