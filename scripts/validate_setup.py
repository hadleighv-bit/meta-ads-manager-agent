"""
Pre-flight validation script.

Checks every prerequisite before running the agent so you get a clear,
actionable error message instead of a cryptic traceback.

Usage:
    python scripts/validate_setup.py
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Allow running from the repo root without installing the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

console = Console()

_ROOT = Path(__file__).parent.parent
_REQUIRED_VARS = [
    "META_APP_ID",
    "META_APP_SECRET",
    "META_ACCESS_TOKEN",
    "META_AD_ACCOUNT_ID",
    "ANTHROPIC_API_KEY",
]


def _ok(msg: str) -> None:
    console.print(f"  [bold green]✅[/bold green]  {msg}")


def _fail(msg: str, hint: str = "") -> None:
    console.print(f"  [bold red]❌[/bold red]  {msg}")
    if hint:
        console.print(f"     [dim]{hint}[/dim]")


def check_env_file() -> bool:
    env_path = _ROOT / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)
        _ok(f".env file found at {env_path}")
        return True
    _fail(
        ".env file not found",
        hint="Run: cp .env.example .env  — then fill in your credentials",
    )
    return False


def check_required_vars() -> bool:
    missing = [k for k in _REQUIRED_VARS if not os.getenv(k)]
    if not missing:
        _ok("All required environment variables are set")
        return True
    for var in missing:
        _fail(f"{var} is not set", hint=f"Add {var}=<value> to your .env file")
    return False


def check_thresholds() -> bool:
    import yaml
    path = _ROOT / "config" / "thresholds.yaml"
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
        required_keys = {"min_roas", "max_cpm", "max_cpc", "min_ctr", "frequency_cap", "budget_burn_rate_warning"}
        missing = required_keys - set(data.keys())
        if missing:
            _fail(f"thresholds.yaml is missing keys: {', '.join(missing)}")
            return False
        _ok("config/thresholds.yaml is valid")
        return True
    except Exception as exc:
        _fail(f"Could not read thresholds.yaml: {exc}")
        return False


def check_reports_dir() -> bool:
    reports = _ROOT / "reports"
    reports.mkdir(exist_ok=True)
    test_file = reports / ".write_test"
    try:
        test_file.write_text("ok")
        test_file.unlink()
        _ok("reports/ directory is writable")
        return True
    except Exception as exc:
        _fail(f"reports/ directory is not writable: {exc}")
        return False


def check_meta_api() -> bool:
    try:
        # Import here so earlier checks can still run if facebook-business isn't installed
        from config.settings import settings
        from tools.account_tools import get_account_summary

        result = get_account_summary(settings.meta_ad_account_id)
        if "error" in result and result["error"]:
            raise RuntimeError(result["error"])
        active = result.get("active_campaigns", "?")
        _ok(f"Meta API connection OK  ({settings.meta_ad_account_id}, {active} active campaigns)")
        return True
    except ImportError as exc:
        _fail(f"facebook-business SDK not installed: {exc}", hint="Run: pip install -r requirements.txt")
        return False
    except Exception as exc:
        _fail(
            f"Meta API connection failed: {exc}",
            hint="Check META_ACCESS_TOKEN and META_AD_ACCOUNT_ID\n"
                 "     Token needs: ads_read, ads_management, business_management",
        )
        return False


def check_anthropic_api() -> bool:
    try:
        import anthropic
        from config.settings import settings

        model = settings.claude_model
        client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        # Minimal ping — 1 token response
        response = client.messages.create(
            model=model,
            max_tokens=5,
            messages=[{"role": "user", "content": "ping"}],
        )
        _ok(f"Anthropic API connection OK  (model: {model})")
        return True
    except ImportError as exc:
        _fail(f"anthropic SDK not installed: {exc}", hint="Run: pip install -r requirements.txt")
        return False
    except Exception as exc:
        _fail(
            f"Anthropic API connection failed: {exc}",
            hint="Check ANTHROPIC_API_KEY in your .env file",
        )
        return False


def main() -> None:
    console.print(Panel.fit("[bold cyan]Meta Ads Agent — Setup Validation[/bold cyan]", border_style="cyan"))
    console.print()

    steps = [
        ("Environment file",         check_env_file),
        ("Required variables",       check_required_vars),
        ("Thresholds config",        check_thresholds),
        ("Reports directory",        check_reports_dir),
        ("Meta API connectivity",    check_meta_api),
        ("Anthropic API connectivity", check_anthropic_api),
    ]

    passed = 0
    failed_at: str | None = None

    for label, fn in steps:
        console.print(f"[bold white]{label}[/bold white]")
        ok = fn()
        console.print()
        if ok:
            passed += 1
        else:
            failed_at = label
            break   # stop on first failure — later checks may depend on earlier ones

    if failed_at is None:
        console.print(
            Panel(
                f"[bold green]All {passed} checks passed — you're ready to run![/bold green]\n\n"
                "  [dim]python main.py                    # report only\n"
                "  python main.py --mode semi_auto    # confirm each action\n"
                "  python main.py --schedule          # run every 6h[/dim]",
                border_style="green",
            )
        )
        sys.exit(0)
    else:
        console.print(
            Panel(
                f"[bold red]Setup incomplete — failed at: {failed_at}[/bold red]\n\n"
                "Fix the issue above and re-run:  [bold]python scripts/validate_setup.py[/bold]",
                border_style="red",
            )
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
