import os
from pathlib import Path
from dotenv import load_dotenv
import yaml

load_dotenv()

_CONFIG_DIR = Path(__file__).parent
_THRESHOLDS_PATH = _CONFIG_DIR / "thresholds.yaml"


def _load_thresholds() -> dict:
    with open(_THRESHOLDS_PATH) as f:
        return yaml.safe_load(f)


class Settings:
    def __init__(self):
        self.meta_app_id: str = os.environ["META_APP_ID"]
        self.meta_app_secret: str = os.environ["META_APP_SECRET"]
        self.meta_access_token: str = os.environ["META_ACCESS_TOKEN"]
        self.meta_ad_account_id: str = os.environ["META_AD_ACCOUNT_ID"]
        self.anthropic_api_key: str = os.environ["ANTHROPIC_API_KEY"]
        self.thresholds: dict = _load_thresholds()

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


settings = Settings()
