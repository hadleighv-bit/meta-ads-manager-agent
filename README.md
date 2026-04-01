# Meta Ads Manager Agent

An AI-powered Meta (Facebook) Ads optimisation agent built with [Claude](https://www.anthropic.com/claude) and the Meta Marketing API. It analyses your ad account, surfaces performance issues, and can take automated corrective actions.

---

## Features

- **Three analysis modes** — report-only, semi-auto (confirm each action), full-auto
- **Claude-powered analysis** — uses `claude-opus-4-5` with tool use to drill into campaigns, ad sets, and ads
- **Threshold-based scoring** — flags ROAS, CPM, CPC, CTR, and frequency issues against configurable thresholds
- **Rich terminal output** — live campaign scorecard with `🔴 🟡 🟢` priority flags
- **Markdown reports** — saved to `reports/` with scorecard table, analysis, and next-review recommendation
- **Email delivery** — optionally sends reports via SMTP on completion
- **Scheduling** — runs every N hours/minutes unattended

---

## Setup

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd meta-ads-manager-agent
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and fill in:

| Variable | Description |
|----------|-------------|
| `META_APP_ID` | Your Meta App ID (from [developers.facebook.com](https://developers.facebook.com)) |
| `META_APP_SECRET` | Your Meta App Secret |
| `META_ACCESS_TOKEN` | Long-lived access token (see below) |
| `META_AD_ACCOUNT_ID` | Your ad account ID, e.g. `act_123456789` |
| `ANTHROPIC_API_KEY` | Anthropic API key from [console.anthropic.com](https://console.anthropic.com) |

#### Optional — email reporting

| Variable | Description |
|----------|-------------|
| `EMAIL_RECIPIENT` | Address to send reports to |
| `EMAIL_SENDER` | From address |
| `SMTP_HOST` | SMTP server (default: `smtp.gmail.com`) |
| `SMTP_PORT` | SMTP port (default: `587`) |
| `SMTP_USER` | SMTP login username |
| `SMTP_PASSWORD` | SMTP password or app password |

Leave email variables blank to disable email delivery.

### 3. Configure thresholds

Edit `config/thresholds.yaml` to match your performance targets:

```yaml
min_roas: 3.5            # minimum acceptable ROAS
max_cpm: 15.00           # maximum acceptable CPM ($)
max_cpc: 2.00            # maximum acceptable CPC ($)
min_ctr: 1.5             # minimum acceptable CTR (%)
frequency_cap: 4.0       # frequency above which creative fatigue is flagged
budget_burn_rate_warning: 0.85  # alert when 85%+ of budget is spent
```

---

## Meta Access Token

You need a **long-lived System User token** or a **long-lived User token** with the following permissions:

| Permission | Purpose |
|------------|---------|
| `ads_read` | Read campaigns, ad sets, ads, and insights |
| `ads_management` | Pause ad sets/ads and update budgets |
| `business_management` | Access Business Manager account data |

**To generate a token:**
1. Go to [developers.facebook.com](https://developers.facebook.com) → your app → **Tools** → **Graph API Explorer**
2. Select your app and add the three permissions above
3. Click **Generate Access Token**
4. Exchange for a long-lived token via the [token exchange endpoint](https://developers.facebook.com/docs/facebook-login/guides/access-tokens/get-long-lived)

For production use, create a **System User** in your Business Manager and generate a non-expiring token.

---

## Running the Agent

### Run once (report only — no changes made)

```bash
python main.py
```

### Analyse and confirm each action before execution

```bash
python main.py --mode semi_auto
```

You will be prompted for each write action:

```
╭─ Confirm Action ────────────────────────╮
│ Action    pause_adset                   │
│ Entity    "Summer Sale US" (12345)      │
│ Current   ACTIVE                        │
│ Proposed  PAUSED                        │
│ Reason    ROAS 1.2x below threshold 3.5x│
╰─────────────────────────────────────────╯
  [A]pprove  [S]kip  s[T]op all  →
```

All decisions are logged to `reports/action_log.csv`.

### Autonomous execution (no prompts)

```bash
python main.py --mode full_auto
```

### Run on a schedule

```bash
# Every 6 hours (default)
python main.py --schedule

# Every 2 hours in semi_auto mode
python main.py --schedule --interval 2h --mode semi_auto

# Every 30 minutes
python main.py --schedule --interval 30m

# Every day
python main.py --schedule --interval 1d
```

### Skip the Meta API connectivity check (useful for testing)

```bash
python main.py --skip-api-check --mode report_only
```

---

## Reports

Reports are saved to the `reports/` directory:

| File | Description |
|------|-------------|
| `reports/analysis_YYYY-MM-DD_HH-MM.md` | Full structured Markdown report |
| `reports/action_log.csv` | Log of all approved/skipped actions (semi_auto mode) |

### Report structure

```
# Meta Ads Analysis Report

## Campaign Scorecard
| Campaign | Spend | ROAS | CTR % | CPC | CPM | Freq | Status | Verdict |
...

## Detailed Analysis
(Claude's full analysis with Executive Summary, Issues Found, Root Cause Analysis,
Actions Taken/Recommended, Budget Reallocation Opportunities)

## Next Review Recommendation
```

---

## Project Structure

```
meta-ads-manager-agent/
├── main.py                  # CLI entry point
├── requirements.txt
├── .env.example
├── config/
│   ├── settings.py          # Loads .env + thresholds.yaml
│   └── thresholds.yaml      # Performance thresholds
├── agent/
│   ├── analyst.py           # Core Claude agent loop (claude-opus-4-5)
│   ├── reporter.py          # Report generation, terminal output, email
│   └── confirmation.py      # Semi-auto action confirmation handler
├── tools/
│   ├── account_tools.py     # Account-level summary
│   ├── campaign_tools.py    # Campaign CRUD + insights
│   ├── adset_tools.py       # Ad set CRUD + insights
│   └── ad_tools.py          # Ad CRUD + insights
└── reports/                 # Generated reports (git-ignored)
```

---

## Troubleshooting

**`Meta API validation failed`**
- Check that `META_ACCESS_TOKEN` is valid and not expired
- Verify `META_AD_ACCOUNT_ID` includes the `act_` prefix (e.g. `act_123456789`)
- Ensure the token has `ads_read` permission

**`Missing required environment variables`**
- Run `cp .env.example .env` and fill in all required fields

**`purchase_roas` shows `0` or `—`**
- This field requires the Meta Pixel to be installed and purchase conversion events configured
- Without pixel data, focus on CTR/CPC/CPM metrics

**Rate limit errors from Meta API**
- The agent makes many API calls in sequence; if you hit limits, use `--interval 2h` or longer
- Meta rate limit codes: 17 (app-level), 32 (page-level), 613 (custom)
