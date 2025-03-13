"""Tests — yua.budget.cost_calculator"""

import pytest
from yua.budget.cost_calculator import CostCalculator, UsageRecord
from yua.providers.base import ProviderName


def calc() -> CostCalculator:
    return CostCalculator()


def test_estimate_grok():
    cost = calc().estimate(ProviderName.GROK, "grok-2", 1000, 1000)
    assert cost > 0.0


def test_estimate_unknown_model():
    cost = calc().estimate(ProviderName.GROK, "nonexistent", 1000, 1000)
    assert cost == 0.0


def test_estimate_zero_tokens():
    cost = calc().estimate(ProviderName.ANTHROPIC, "claude-haiku-4-5", 0, 0)
    assert cost == 0.0


def test_estimate_scales_linearly():
    c = calc()
    cost_1k = c.estimate(ProviderName.GROK, "grok-2", 1000, 0)
    cost_2k = c.estimate(ProviderName.GROK, "grok-2", 2000, 0)
    assert abs(cost_2k - cost_1k * 2) < 0.000001


def test_record_adds_to_history():
    c = calc()
    c.record(ProviderName.GROK, "grok-2", 500, 800)
    assert len(c._records) == 1


def test_total_cost_empty():
    assert calc().total_cost() == 0.0


def test_total_cost_accumulates():
    c = calc()
    c.record(ProviderName.GROK, "grok-2", 500, 800)
    c.record(ProviderName.ANTHROPIC, "claude-haiku-4-5", 200, 300)
    assert c.total_cost() > 0.0


def test_cost_by_provider():
    c = calc()
    c.record(ProviderName.GROK, "grok-2", 500, 800)
    c.record(ProviderName.ANTHROPIC, "claude-haiku-4-5", 200, 300)
    by_prov = c.cost_by_provider()
    assert "grok" in by_prov
    assert "anthropic" in by_prov


def test_cost_by_model():
    c = calc()
    c.record(ProviderName.GROK, "grok-2", 500, 800)
    by_model = c.cost_by_model()
    assert "grok/grok-2" in by_model


def test_summary_empty():
    s = calc().summary()
    assert s.total_calls == 0 and s.total_cost_usd == 0.0


def test_summary_with_records():
    c = calc()
    c.record(ProviderName.GROK, "grok-2", 500, 800)
    s = c.summary()
    assert s.total_calls == 1
    assert s.total_input_tokens == 500
    assert s.total_output_tokens == 800


def test_compare_models_sorted():
    comparisons = calc().compare_models(1000, 1000)
    costs = [c for _, c in comparisons]
    assert costs == sorted(costs)


def test_compare_models_all_providers():
    comparisons = calc().compare_models(500, 500)
    providers = {name.split("/")[0] for name, _ in comparisons}
    assert "grok" in providers


def test_reset_clears_records():
    c = calc()
    c.record(ProviderName.GROK, "grok-2", 100, 200)
    c.reset()
    assert len(c._records) == 0 and c.total_cost() == 0.0


def test_usage_record_total_tokens():
    r = UsageRecord("grok", "grok-2", 300, 700, 0.005)
    assert r.total_tokens == 1000


def test_estimate_from_text():
    cost = calc().estimate_from_text(ProviderName.GROK, "grok-2", "hello world", "this is a response")
    assert cost >= 0.0
