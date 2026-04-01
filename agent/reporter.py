"""
Reporter — formats and distributes the final analysis output.

Responsibilities:
  1. Save a structured Markdown report to reports/analysis_YYYY-MM-DD_HH-MM.md
  2. Print a campaign scorecard table to the terminal via rich
  3. Optionally send the report by email if EMAIL_RECIPIENT is set in .env
"""
from __future__ import annotations

import os
import smtplib
import textwrap
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config.settings import settings

console = Console()

_FLAG_URGENT = "🔴"
_FLAG_WATCH = "🟡"
_FLAG_HEALTHY = "🟢"


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def _verdict(row: dict) -> tuple[str, str]:
    """
    Return (flag_emoji, label) based on campaign metrics vs thresholds.
    row keys: spend, roas, ctr, cpc, cpm, frequency
    """
    spend = float(row.get("spend", 0) or 0)
    roas = float(row.get("roas", 0) or 0)
    ctr = float(row.get("ctr", 0) or 0)
    cpc = float(row.get("cpc", 0) or 0)
    cpm = float(row.get("cpm", 0) or 0)
    frequency = float(row.get("frequency", 0) or 0)

    # Urgent: spending but zero conversions, or ROAS well below threshold
    if spend > 0 and roas == 0:
        return _FLAG_URGENT, "No conversions"
    if roas > 0 and roas < settings.min_roas:
        return _FLAG_URGENT, f"ROAS {roas:.2f}x < {settings.min_roas}x"
    if cpm > settings.max_cpm * 1.5:
        return _FLAG_URGENT, f"CPM ${cpm:.2f} very high"
    if frequency > settings.frequency_cap:
        return _FLAG_URGENT, f"Frequency {frequency:.1f} > cap"

    # Watch: borderline on any metric
    if roas > 0 and roas < settings.min_roas * 1.2:
        return _FLAG_WATCH, f"ROAS {roas:.2f}x borderline"
    if ctr < settings.min_ctr and spend > 0:
        return _FLAG_WATCH, f"CTR {ctr:.2f}% < {settings.min_ctr}%"
    if cpc > settings.max_cpc:
        return _FLAG_WATCH, f"CPC ${cpc:.2f} > ${settings.max_cpc}"
    if cpm > settings.max_cpm:
        return _FLAG_WATCH, f"CPM ${cpm:.2f} > ${settings.max_cpm}"

    # No spend yet — neutral
    if spend == 0:
        return _FLAG_WATCH, "No spend"

    return _FLAG_HEALTHY, "Healthy"


def _next_review(campaign_metrics: list[dict]) -> str:
    verdicts = [_verdict(r)[0] for r in campaign_metrics]
    if _FLAG_URGENT in verdicts:
        return "**Review immediately** — urgent issues detected."
    if _FLAG_WATCH in verdicts:
        return "**Review within 24 hours** — metrics need monitoring."
    return "**Review in 7 days** — all campaigns healthy."


# ---------------------------------------------------------------------------
# Reporter
# ---------------------------------------------------------------------------

class Reporter:
    def __init__(
        self,
        analysis_text: str,
        campaign_metrics: list[dict] | None = None,
        mode: str = "report_only",
    ) -> None:
        self.analysis_text = analysis_text
        self.campaign_metrics = campaign_metrics or []
        self.mode = mode
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        self._report_path: Path | None = None

    def generate(self) -> Path:
        """Build the report, print to terminal, optionally email. Returns report path."""
        self._print_scorecard()
        self._report_path = self._save_markdown()
        self._maybe_send_email()
        console.print(f"\n[dim]Report saved → {self._report_path}[/dim]")
        return self._report_path

    # ------------------------------------------------------------------
    # Terminal scorecard
    # ------------------------------------------------------------------

    def _print_scorecard(self) -> None:
        if not self.campaign_metrics:
            return

        table = Table(
            title="Campaign Scorecard",
            show_header=True,
            header_style="bold white on dark_blue",
            show_lines=True,
            border_style="blue",
        )
        table.add_column("Campaign", style="bold", overflow="fold", max_width=30)
        table.add_column("Spend", justify="right")
        table.add_column("ROAS", justify="right")
        table.add_column("CTR %", justify="right")
        table.add_column("CPC", justify="right")
        table.add_column("CPM", justify="right")
        table.add_column("Freq", justify="right")
        table.add_column("Status")
        table.add_column("Verdict")

        for row in self.campaign_metrics:
            flag, label = _verdict(row)
            flag_color = {
                _FLAG_URGENT: "red",
                _FLAG_WATCH: "yellow",
                _FLAG_HEALTHY: "green",
            }.get(flag, "white")

            roas = float(row.get("roas", 0) or 0)
            roas_str = f"{roas:.2f}x" if roas else "—"
            spend = float(row.get("spend", 0) or 0)

            table.add_row(
                row.get("name", row.get("campaign_id", "?")),
                f"${spend:,.2f}",
                roas_str,
                f"{float(row.get('ctr', 0) or 0):.2f}",
                f"${float(row.get('cpc', 0) or 0):.2f}",
                f"${float(row.get('cpm', 0) or 0):.2f}",
                f"{float(row.get('frequency', 0) or 0):.1f}",
                row.get("status", "—"),
                f"[{flag_color}]{flag} {label}[/{flag_color}]",
            )

        console.print()
        console.print(table)
        console.print()

    # ------------------------------------------------------------------
    # Markdown report
    # ------------------------------------------------------------------

    def _build_markdown(self) -> str:
        ts = datetime.now()
        lines: list[str] = [
            f"# Meta Ads Analysis Report",
            f"",
            f"**Generated:** {ts.strftime('%Y-%m-%d %H:%M')}  |  **Mode:** {self.mode}",
            f"",
        ]

        # Scorecard table
        if self.campaign_metrics:
            lines += [
                "## Campaign Scorecard",
                "",
                "| Campaign | Spend | ROAS | CTR % | CPC | CPM | Freq | Status | Verdict |",
                "|----------|------:|-----:|------:|----:|----:|-----:|--------|---------|",
            ]
            for row in self.campaign_metrics:
                flag, label = _verdict(row)
                roas = float(row.get("roas", 0) or 0)
                lines.append(
                    "| {name} | ${spend:,.2f} | {roas} | {ctr:.2f} | ${cpc:.2f} | ${cpm:.2f}"
                    " | {freq:.1f} | {status} | {flag} {label} |".format(
                        name=row.get("name", row.get("campaign_id", "?")),
                        spend=float(row.get("spend", 0) or 0),
                        roas=f"{roas:.2f}x" if roas else "—",
                        ctr=float(row.get("ctr", 0) or 0),
                        cpc=float(row.get("cpc", 0) or 0),
                        cpm=float(row.get("cpm", 0) or 0),
                        freq=float(row.get("frequency", 0) or 0),
                        status=row.get("status", "—"),
                        flag=flag,
                        label=label,
                    )
                )
            lines.append("")

        # Priority legend
        lines += [
            "### Priority Flags",
            f"- {_FLAG_URGENT} **Urgent** — immediate action required",
            f"- {_FLAG_WATCH} **Watch** — monitor closely",
            f"- {_FLAG_HEALTHY} **Healthy** — performing above thresholds",
            "",
        ]

        # Claude's analysis
        lines += [
            "---",
            "",
            "## Detailed Analysis",
            "",
            self.analysis_text,
            "",
        ]

        # Next review
        lines += [
            "---",
            "",
            "## Next Review Recommendation",
            "",
            _next_review(self.campaign_metrics) if self.campaign_metrics
            else "Review schedule not determined — no campaign metrics collected.",
            "",
        ]

        return "\n".join(lines)

    def _save_markdown(self) -> Path:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M")
        path = self.reports_dir / f"analysis_{ts}.md"
        path.write_text(self._build_markdown(), encoding="utf-8")
        return path

    # ------------------------------------------------------------------
    # Email
    # ------------------------------------------------------------------

    def _maybe_send_email(self) -> None:
        recipient = os.getenv("EMAIL_RECIPIENT", "").strip()
        if not recipient or self._report_path is None:
            return

        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        sender = os.getenv("EMAIL_SENDER", smtp_user)

        if not smtp_user or not smtp_password:
            console.print(
                "[yellow]EMAIL_RECIPIENT set but SMTP_USER/SMTP_PASSWORD missing — skipping email.[/yellow]"
            )
            return

        subject = f"Meta Ads Report — {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        msg = MIMEMultipart("mixed")
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = recipient

        # Plain-text body (truncated executive summary)
        body_text = textwrap.shorten(self.analysis_text, width=2000, placeholder="…")
        msg.attach(MIMEText(body_text, "plain"))

        # Markdown attachment
        attachment = MIMEBase("text", "markdown")
        attachment.set_payload(self._report_path.read_bytes())
        encoders.encode_base64(attachment)
        attachment.add_header(
            "Content-Disposition",
            "attachment",
            filename=self._report_path.name,
        )
        msg.attach(attachment)

        try:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.sendmail(sender, [recipient], msg.as_string())
            console.print(f"[green]Email sent → {recipient}[/green]")
        except Exception as exc:
            console.print(f"[yellow]Email failed: {exc}[/yellow]")
