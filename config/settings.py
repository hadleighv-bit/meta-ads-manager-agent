from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from dotenv import load_dotenv
import yaml

load_dotenv()

_CONFIG_DIR = Path(__file__).parent
_THRESHOLDS_PATH = _CONFIG_DIR / "thresholds.yaml"


def _load_thresholds() -> dict:
    with open(_THRESHOLDS_PATH) as f:
        return yaml.safe_load(f)


class Settings:
    def __init__(self) -> None:
        missing = [
            k for k in (
                "META_APP_ID", "META_APP_SECRET", "META_ACCESS_TOKEN",
                "META_AD_ACCOUNT_ID", "ANTHROPIC_API_KEY",
            )
            if not os.getenv(k)
        ]
        if missing:
            raise EnvironmentError(
                f"Missing required environment variables: {', '.join(missing)}\n"
                "Copy .env.example to .env and fill in all values."
            )

        self.meta_app_id: str = os.environ["META_APP_ID"]
        self.meta_app_secret: str = os.environ["META_APP_SECRET"]
        self.meta_access_token: str = os.environ["META_ACCESS_TOKEN"]
        # Normalise act_ prefix
        _account_id = os.environ["META_AD_ACCOUNT_ID"]
        self.meta_ad_account_id: str = (
            _account_id if _account_id.startswith("act_") else f"act_{_account_id}"
        )
        self.anthropic_api_key: str = os.environ["ANTHROPIC_API_KEY"]
        self.thresholds: dict = _load_thresholds()

        # Optional — mock mode and model override
        self.mock_meta: bool = os.getenv("MOCK_META", "false").lower() == "true"
        self.claude_model: str = os.getenv("CLAUDE_MODEL", "claude-opus-4-6")

        # Optional — email settings
        self.email_recipient: str = os.getenv("EMAIL_RECIPIENT", "")
        self.smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user: str = os.getenv("SMTP_USER", "")
        self.smtp_password: str = os.getenv("SMTP_PASSWORD", "")
        self.email_sender: str = os.getenv("EMAIL_SENDER", os.getenv("SMTP_USER", ""))

    # Threshold convenience properties
    @property
    def min_roas(self) -> float:
        return self.thresholds["min_roas"]

    @property
    def max_cpm(self) -> float:
        return self.thresholds["max_cpm"]

    @property
    def max_cpc(self) -> float:
        return self.thresholds["max_cpc"]

    @property
    def min_ctr(self) -> float:
        return self.thresholds["min_ctr"]

    @property
    def frequency_cap(self) -> float:
        return self.thresholds["frequency_cap"]

    @property
    def budget_burn_rate_warning(self) -> float:
        return self.thresholds["budget_burn_rate_warning"]


class _LazySettings:
    """
    Proxy that defers Settings() construction until the first attribute access.

    This means importing `from config.settings import settings` never raises
    EnvironmentError — the error is deferred to the moment the code actually
    *uses* a settings value, which is after main.py has had a chance to load
    the .env file and validate the environment.
    """

    _instance: Settings | None = None

    def __getattr__(self, name: str):
        if self._instance is None:
            self._instance = Settings()
        return getattr(self._instance, name)

    def reload(self) -> None:
        """Force re-initialisation (useful in tests or after .env changes)."""
        self._instance = None


settings = _LazySettings()
