"""
YuaLLM · Alert Notifier
Alerts for cost overruns, quality failures, and provider fallbacks.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class AlertLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class YuaAlert:
    level: AlertLevel
    title: str
    message: str
    provider_model: str = ""
    timestamp: str = ""

    def __post_init__(self) -> None:
        if not self.timestamp:
            self.timestamp = datetime.now(tz=timezone.utc).isoformat()

    def format_terminal(self) -> str:
        prefix = {"INFO": "[INFO]", "WARNING": "[WARN]", "CRITICAL": "[CRIT]"}[self.level.value]
        return f"{prefix} {self.title} — {self.message}"

    def format_telegram(self) -> str:
        emoji = {"INFO": "ℹ️", "WARNING": "⚠️", "CRITICAL": "🚨"}[self.level.value]
        lines = [f"{emoji} *{self.title}*", self.message]
        if self.provider_model:
            lines.append(f"model: `{self.provider_model}`")
        return "\n".join(lines)


class YuaNotifier:
    def __init__(self, telegram_token: str | None = None, telegram_chat_id: str | None = None) -> None:
        self._tg_token = telegram_token or os.getenv("TELEGRAM_TOKEN", "")
        self._tg_chat = telegram_chat_id or os.getenv("TELEGRAM_CHAT_ID", "")
        self._history: list[YuaAlert] = []

    def send(self, alert: YuaAlert, silent: bool = False) -> None:
        self._history.append(alert)
        if not silent:
            print(alert.format_terminal())

    def alert_cost_overrun(self, model: str, actual: float, budget: float, silent: bool = False) -> YuaAlert:
        alert = YuaAlert(
            level=AlertLevel.WARNING,
            title="Cost Overrun",
            message=f"${actual:.5f} exceeds budget ${budget:.5f}",
            provider_model=model,
        )
        self.send(alert, silent=silent)
        return alert

    def alert_quality_failure(self, model: str, score: float, silent: bool = False) -> YuaAlert:
        alert = YuaAlert(
            level=AlertLevel.WARNING,
            title="Quality Failure",
            message=f"response scored {score:.0%} — below threshold",
            provider_model=model,
        )
        self.send(alert, silent=silent)
        return alert

    def alert_fallback(self, from_model: str, to_model: str, reason: str, silent: bool = False) -> YuaAlert:
        alert = YuaAlert(
            level=AlertLevel.INFO,
            title="Provider Fallback",
            message=f"{from_model} → {to_model} | {reason}",
        )
        self.send(alert, silent=silent)
        return alert

    def alert_provider_error(self, model: str, error: str, silent: bool = False) -> YuaAlert:
        alert = YuaAlert(
            level=AlertLevel.CRITICAL,
            title="Provider Error",
            message=error,
            provider_model=model,
        )
        self.send(alert, silent=silent)
        return alert

    def history(self) -> list[YuaAlert]:
        return list(self._history)

    def clear_history(self) -> None:
        self._history.clear()
