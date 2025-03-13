"""Tests — yua.router.llm_router"""

import pytest
from yua.router.llm_router import LLMRouter, RouterConfig, RouteDecision
from yua.providers.base import ProviderName, TaskType


def router() -> LLMRouter:
    return LLMRouter()


def test_route_returns_decision():
    r = router().route("Hello, how are you?")
    assert isinstance(r, RouteDecision)


def test_route_default_primary_grok():
    r = router().route("Analyze the macroeconomic impact of interest rate changes")
    assert r.provider == ProviderName.GROK


def test_detect_coding_task():
    task = router().detect_task_type("def fibonacci(n): implement this function")
    assert task == TaskType.CODING


def test_detect_reasoning_task():
    task = router().detect_task_type("explain why the sky is blue step by step")
    assert task == TaskType.REASONING


def test_detect_summarization_task():
    task = router().detect_task_type("summarize this article in 3 bullet points")
    assert task == TaskType.SUMMARIZATION


def test_detect_simple_task():
    task = router().detect_task_type("hi")
    assert task == TaskType.SIMPLE


def test_detect_analysis_task():
    task = router().detect_task_type("analyze and compare these two approaches")
    assert task == TaskType.ANALYSIS


def test_detect_creative_task():
    task = router().detect_task_type("write a short story about a robot")
    assert task == TaskType.CREATIVE


def test_estimate_tokens():
    r = router()
    tokens = r.estimate_tokens("hello world this is a test")
    assert tokens > 0


def test_estimate_complexity_simple():
    r = router()
    assert r.estimate_complexity("hi") == "simple"


def test_estimate_complexity_complex():
    long_prompt = " ".join(["word"] * 600)
    assert router().estimate_complexity(long_prompt) == "complex"


def test_route_with_cheap_config():
    config = RouterConfig(prefer_cheap=True)
    r = router().route("What is 2+2?", config)
    assert isinstance(r, RouteDecision)
    assert r.estimated_cost_usd >= 0


def test_route_with_fast_config():
    config = RouterConfig(prefer_fast=True)
    r = router().route("Quick question about Python", config)
    assert isinstance(r, RouteDecision)


def test_route_batch():
    prompts = ["Hello", "Write some code", "Analyze this data"]
    decisions = router().route_batch(prompts)
    assert len(decisions) == 3


def test_route_with_disabled_provider():
    config = RouterConfig(disabled_providers=[ProviderName.GROK])
    r = router().route("Tell me about Grok AI", config)
    assert r.provider != ProviderName.GROK


def test_route_all_disabled_raises():
    config = RouterConfig(
        disabled_providers=[
            ProviderName.GROK, ProviderName.ANTHROPIC,
            ProviderName.OPENAI, ProviderName.GROQ,
        ]
    )
    with pytest.raises(ValueError):
        router().route("hello", config)


def test_route_force_model():
    config = RouterConfig(force_model="anthropic/claude-haiku-4-5")
    r = router().route("quick question", config)
    assert r.provider == ProviderName.ANTHROPIC
    assert r.model_id == "claude-haiku-4-5"


def test_route_cost_budget():
    config = RouterConfig(max_cost_per_call=0.00001)
    r = router().route("hi", config)
    assert r.estimated_cost_usd >= 0


def test_decision_model_name():
    r = router().route("hello")
    assert "/" in r.decision_model_name() if hasattr(r, "decision_model_name") else "/" in r.model_name()


def test_route_reason_not_empty():
    r = router().route("hello world")
    assert len(r.reason) > 0


def test_estimated_cost_non_negative():
    r = router().route("analyze this market trend in depth please")
    assert r.estimated_cost_usd >= 0
