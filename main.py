"""
Entry point for the Meta Ads Manager Agent.

Usage:
    # Run once
    python main.py

    # Run once in dry-run mode (no mutations)
    python main.py --dry-run

    # Run on a schedule (every hour by default)
    python main.py --schedule

    # Run on a custom interval (minutes)
    python main.py --schedule --interval 30
"""
import argparse
import sys
import time

import schedule
from rich.console import Console

from agent import MetaAdsAgent

console = Console()


def _run_agent(dry_run: bool) -> None:
    try:
        agent = MetaAdsAgent(dry_run=dry_run)
        agent.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user.[/yellow]")
        raise
    except Exception as exc:
        console.print(f"[bold red]Agent run failed:[/bold red] {exc}")
        raise


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Meta Ads Manager Agent — AI-powered ad account optimiser"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Do not apply any changes; only report recommendations (default: True)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply automated actions (pause ad sets, adjust budgets). Overrides --dry-run.",
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

    dry_run = not args.apply

    if args.schedule:
        console.print(
            f"[bold green]Scheduling agent every {args.interval} minute(s).[/bold green] "
            f"Press Ctrl+C to stop."
        )

        # Run immediately on start, then on schedule
        _run_agent(dry_run=dry_run)

        schedule.every(args.interval).minutes.do(_run_agent, dry_run=dry_run)

        try:
            while True:
                schedule.run_pending()
                time.sleep(30)
        except KeyboardInterrupt:
            console.print("\n[yellow]Scheduler stopped.[/yellow]")
            sys.exit(0)
    else:
        _run_agent(dry_run=dry_run)


if __name__ == "__main__":
    main()
