"""
Entry point for the Meta Ads Manager Agent.

Usage:
    python main.py                              # report only, run once
    python main.py --mode semi_auto             # confirm each action
    python main.py --mode full_auto             # autonomous execution
    python main.py --schedule                   # run every 6h (default)
    python main.py --schedule --interval 2h     # every 2 hours
    python main.py --schedule --interval 30m    # every 30 minutes
    python main.py --schedule --interval 1d --mode report_only
"""
import argparse
import os
import sys
import time

import schedule
from dotenv import load_dotenv
from rich.console import Console

console = Console()

VALID_MODES = ("report_only", "semi_auto", "full_auto")

_REQUIRED_ENV_VARS = [
    "META_APP_ID",
    "META_APP_SECRET",
    "META_ACCESS_TOKEN",
    "META_AD_ACCOUNT_ID",
    "ANTHROPIC_API_KEY",
]


# ---------------------------------------------------------------------------
# Interval parsing  e.g. "6h" → 360, "30m" → 30, "1d" → 1440
# ---------------------------------------------------------------------------

def _parse_interval(raw: str) -> int:
    """Return interval in minutes. Accepts Nh / Nm / Nd or plain integer (minutes)."""
    raw = raw.strip().lower()
    try:
        if raw.endswith("h"):
            return int(raw[:-1]) * 60
        if raw.endswith("m"):
            return int(raw[:-1])
        if raw.endswith("d"):
            return int(raw[:-1]) * 60 * 24
        return int(raw)
    except ValueError:
        console.print(f"[bold red]Invalid interval '{raw}'. Use formats like 6h, 30m, 1d, or 90 (minutes).[/bold red]")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Startup validation
# ---------------------------------------------------------------------------

def _validate_env() -> None:
    """Check all required env vars are present. Exits with error if any are missing."""
    load_dotenv()
    missing = [k for k in _REQUIRED_ENV_VARS if not os.getenv(k)]
    if missing:
        console.print("[bold red]Missing required environment variables:[/bold red]")
        for var in missing:
            console.print(f"  [red]✗[/red] {var}")
        console.print("\n[dim]Copy .env.example to .env and fill in all values.[/dim]")
        sys.exit(1)
    console.print("[dim]Environment variables … [green]OK[/green][/dim]")


def _validate_meta_api() -> None:
    """Make a lightweight test call to Meta API to verify the token and account ID."""
    try:
        from tools.account_tools import get_account_summary
        from config.settings import settings

        # Normalise act_ prefix
        account_id = settings.meta_ad_account_id
        if not account_id.startswith("act_"):
            account_id = f"act_{account_id}"

        result = get_account_summary(account_id)
        if "error" in result and result["error"]:
            raise RuntimeError(result["error"])
        console.print("[dim]Meta API connection … [green]OK[/green][/dim]")
    except Exception as exc:
        console.print(f"[bold red]Meta API validation failed:[/bold red] {exc}")
        console.print(
            "[dim]Check META_ACCESS_TOKEN and META_AD_ACCOUNT_ID in your .env\n"
            "The token needs: ads_read, ads_management, business_management[/dim]"
        )
        sys.exit(1)


def validate_startup(skip_api_check: bool = False) -> None:
    """Run all startup checks. Exits on failure."""
    console.print("[bold cyan]Validating configuration…[/bold cyan]")
    _validate_env()
    if not skip_api_check:
        _validate_meta_api()
    console.print("[bold green]All checks passed.[/bold green]\n")


# ---------------------------------------------------------------------------
# Agent runner
# ---------------------------------------------------------------------------

def _run_agent(mode: str) -> None:
    try:
        from agent import AnalysisAgent
        agent = AnalysisAgent()
        agent.run_analysis(mode=mode)  # type: ignore[arg-type]
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted.[/yellow]")
        raise
    except Exception as exc:
        console.print(f"[bold red]Agent run failed:[/bold red] {exc}")
        raise


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Meta Ads Manager Agent — AI-powered ad account optimiser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py
  python main.py --mode semi_auto
  python main.py --mode full_auto
  python main.py --schedule --interval 6h
  python main.py --schedule --interval 30m --mode semi_auto
  python main.py --skip-api-check --mode report_only
""",
    )
    parser.add_argument(
        "--mode",
        choices=VALID_MODES,
        default="report_only",
        help=(
            "report_only (default): analyse, no mutations | "
            "semi_auto: confirm each action | "
            "full_auto: autonomous execution"
        ),
    )
    parser.add_argument(
        "--schedule",
        action="store_true",
        help="Run repeatedly on an interval instead of once.",
    )
    parser.add_argument(
        "--interval",
        default="6h",
        metavar="INTERVAL",
        help="Schedule interval. Accepts 6h, 30m, 1d, or plain minutes (default: 6h).",
    )
    parser.add_argument(
        "--skip-api-check",
        action="store_true",
        help="Skip the Meta API connectivity check on startup (useful for offline testing).",
    )
    args = parser.parse_args()

    validate_startup(skip_api_check=args.skip_api_check)

    if args.schedule:
        interval_minutes = _parse_interval(args.interval)
        interval_label = args.interval if not args.interval.isdigit() else f"{args.interval}m"
        console.print(
            f"[bold green]Scheduling agent every {interval_label} "
            f"(mode={args.mode}).[/bold green]  Press Ctrl+C to stop.\n"
        )
        _run_agent(mode=args.mode)
        schedule.every(interval_minutes).minutes.do(_run_agent, mode=args.mode)
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
