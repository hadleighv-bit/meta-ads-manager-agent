"""
Entry point for the Meta Ads Manager Agent.

Usage:
    # Report only (no actions taken) — default
    python main.py

    # Semi-auto: Claude proposes, you confirm each action
    python main.py --mode semi_auto

    # Full auto: Claude acts autonomously
    python main.py --mode full_auto

    # Run on a schedule (every 60 minutes by default)
    python main.py --schedule

    # Custom interval
    python main.py --schedule --interval 30 --mode semi_auto
"""
import argparse
import sys
import time

import schedule
from rich.console import Console

from agent import AnalysisAgent

console = Console()

VALID_MODES = ("report_only", "semi_auto", "full_auto")


def _run_agent(mode: str) -> None:
    try:
        agent = AnalysisAgent()
        agent.run_analysis(mode=mode)  # type: ignore[arg-type]
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        raise
    except Exception as exc:
        console.print(f"[bold red]Agent run failed:[/bold red] {exc}")
        raise


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Meta Ads Manager Agent — AI-powered ad account optimiser"
    )
    parser.add_argument(
        "--mode",
        choices=VALID_MODES,
        default="report_only",
        help=(
            "Analysis mode: "
            "'report_only' (default) — analyse only, no actions; "
            "'semi_auto' — propose actions with terminal confirmation; "
            "'full_auto' — execute actions autonomously."
        ),
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run the agent on a recurring schedule instead of once.",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Schedule interval in minutes (default: 60). Only used with --schedule.",
    )
    args = parser.parse_args()

    if args.schedule:
        console.print(
            f"[bold green]Scheduling agent every {args.interval} minute(s)  "
            f"(mode={args.mode}).[/bold green]  Press Ctrl+C to stop."
        )
        _run_agent(mode=args.mode)
        schedule.every(args.interval).minutes.do(_run_agent, mode=args.mode)
        try:
            while True:
                schedule.run_pending()
                time.sleep(30)
        except KeyboardInterrupt:
            console.print("\n[yellow]Scheduler stopped.[/yellow]")
            sys.exit(0)
    else:
        _run_agent(mode=args.mode)


if __name__ == "__main__":
    main()
