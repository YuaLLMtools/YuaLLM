"""Tests — yua.alerts.notifier"""

import pytest
from yua.alerts.notifier import AlertLevel, YuaAlert, YuaNotifier


def test_format_terminal_info():
    a = YuaAlert(AlertLevel.INFO, "Test", "message")
    assert "[INFO]" in a.format_terminal()


def test_format_terminal_warning():
    a = YuaAlert(AlertLevel.WARNING, "Warn", "msg")
    assert "[WARN]" in a.format_terminal()


def test_format_terminal_critical():
    a = YuaAlert(AlertLevel.CRITICAL, "Crit", "msg")
    assert "[CRIT]" in a.format_terminal()


def test_timestamp_auto_set():
    a = YuaAlert(AlertLevel.INFO, "T", "m")
    assert a.timestamp != ""


def test_send_records_history():
    n = YuaNotifier()
    n.send(YuaAlert(AlertLevel.INFO, "T", "m"), silent=True)
    assert len(n.history()) == 1


def test_clear_history():
    n = YuaNotifier()
    n.send(YuaAlert(AlertLevel.INFO, "T", "m"), silent=True)
    n.clear_history()
    assert len(n.history()) == 0


def test_cost_overrun_alert():
    n = YuaNotifier()
    a = n.alert_cost_overrun("grok/grok-2", 0.05, 0.01, silent=True)
    assert a.level == AlertLevel.WARNING
    assert "grok/grok-2" in a.provider_model


def test_quality_failure_alert():
    n = YuaNotifier()
    a = n.alert_quality_failure("grok/grok-2", 0.35, silent=True)
    assert a.level == AlertLevel.WARNING
    assert "35%" in a.message


def test_fallback_alert():
    n = YuaNotifier()
    a = n.alert_fallback("grok/grok-2", "anthropic/claude-haiku-4-5", "timeout", silent=True)
    assert a.level == AlertLevel.INFO
    assert "fallback" in a.title.lower() or "Fallback" in a.title


def test_provider_error_alert():
    n = YuaNotifier()
    a = n.alert_provider_error("grok/grok-2", "connection refused", silent=True)
    assert a.level == AlertLevel.CRITICAL


def test_history_accumulates():
    n = YuaNotifier()
    n.send(YuaAlert(AlertLevel.INFO, "A", "1"), silent=True)
    n.send(YuaAlert(AlertLevel.WARNING, "B", "2"), silent=True)
    assert len(n.history()) == 2


def test_telegram_format_has_title():
    a = YuaAlert(AlertLevel.WARNING, "My Title", "body", provider_model="grok/grok-2")
    assert "My Title" in a.format_telegram()
