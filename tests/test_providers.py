"""Tests — yua.providers.base"""

import pytest
from yua.providers.base import (
    KNOWN_MODELS, ProviderName, TaskType, ProviderModel,
    get_model, models_for_task,
)


def test_known_models_not_empty():
    assert len(KNOWN_MODELS) >= 4


def test_grok_model_exists():
    model = get_model(ProviderName.GROK, "grok-2")
    assert model is not None
    assert model.provider == ProviderName.GROK


def test_anthropic_model_exists():
    model = get_model(ProviderName.ANTHROPIC, "claude-sonnet-4-6")
    assert model is not None


def test_get_model_not_found():
    assert get_model(ProviderName.GROK, "nonexistent-model") is None


def test_cost_for_zero_tokens():
    model = get_model(ProviderName.GROK, "grok-2")
    assert model.cost_for(0, 0) == 0.0


def test_cost_for_positive_tokens():
    model = get_model(ProviderName.GROK, "grok-2")
    cost = model.cost_for(1000, 1000)
    assert cost > 0.0


def test_cost_scales_with_tokens():
    model = get_model(ProviderName.ANTHROPIC, "claude-sonnet-4-6")
    cost_small = model.cost_for(100, 100)
    cost_large = model.cost_for(1000, 1000)
    assert cost_large > cost_small


def test_model_name_format():
    model = get_model(ProviderName.GROK, "grok-2")
    assert model.name() == "grok/grok-2"


def test_models_for_task_reasoning():
    models = models_for_task(TaskType.REASONING)
    assert len(models) >= 1
    assert any(m.provider == ProviderName.GROK for m in models)


def test_models_for_task_coding():
    models = models_for_task(TaskType.CODING)
    assert len(models) >= 1


def test_models_for_task_simple():
    models = models_for_task(TaskType.SIMPLE)
    assert any("mini" in m.model_id for m in models)


def test_grok_context_window():
    model = get_model(ProviderName.GROK, "grok-2")
    assert model.context_window >= 100_000


def test_all_models_have_costs():
    for model in KNOWN_MODELS:
        assert model.cost_per_1k_input >= 0
        assert model.cost_per_1k_output >= 0


def test_provider_name_values():
    assert ProviderName.GROK.value == "grok"
    assert ProviderName.ANTHROPIC.value == "anthropic"
