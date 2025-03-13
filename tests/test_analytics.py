"""Tests — yua.analytics.leaderboard"""

import pytest
from yua.analytics.leaderboard import Leaderboard, ProviderStats, RoutingStats
from yua.scorer.quality_scorer import QualityScore
from yua.router.llm_router import LLMRouter, RouterConfig, RouteDecision
from yua.providers.base import ProviderName, TaskType


def make_score(model: str, overall: float, task: str = "chat") -> QualityScore:
    return QualityScore(model, task, overall, overall, overall, overall, overall, "good")


def make_decision(provider: ProviderName, model_id: str, task: TaskType, fallback: bool = False) -> RouteDecision:
    return RouteDecision(provider, model_id, task, "test", 0.001, fallback)


def lb() -> Leaderboard:
    return Leaderboard()


def test_provider_stats_empty():
    assert lb().provider_stats([]) == []


def test_provider_stats_ranks():
    scores = [
        make_score("grok/grok-2", 0.9),
        make_score("grok/grok-2", 0.8),
        make_score("anthropic/claude-haiku-4-5", 0.6),
    ]
    stats = lb().provider_stats(scores)
    assert stats[0].rank == 1
    assert stats[0].provider_model == "grok/grok-2"


def test_provider_stats_avg_quality():
    scores = [make_score("grok/grok-2", 0.8), make_score("grok/grok-2", 0.6)]
    stats = lb().provider_stats(scores)
    assert stats[0].avg_quality == pytest.approx(0.7)


def test_provider_stats_pass_rate():
    scores = [make_score("grok/grok-2", 0.7), make_score("grok/grok-2", 0.4)]
    stats = lb().provider_stats(scores)
    assert stats[0].pass_rate == pytest.approx(0.5)


def test_routing_stats_empty():
    s = lb().routing_stats([])
    assert s.total_routed == 0


def test_routing_stats_counts():
    decisions = [
        make_decision(ProviderName.GROK, "grok-2", TaskType.CHAT, fallback=False),
        make_decision(ProviderName.ANTHROPIC, "claude-haiku-4-5", TaskType.SIMPLE, fallback=True),
    ]
    s = lb().routing_stats(decisions)
    assert s.total_routed == 2
    assert s.primary_used == 1
    assert s.fallback_used == 1


def test_routing_stats_fallback_rate():
    decisions = [make_decision(ProviderName.GROK, "grok-2", TaskType.CHAT, fallback=True)] * 4
    s = lb().routing_stats(decisions)
    assert s.fallback_rate == pytest.approx(1.0)


def test_routing_stats_task_distribution():
    decisions = [
        make_decision(ProviderName.GROK, "grok-2", TaskType.CHAT),
        make_decision(ProviderName.GROK, "grok-2", TaskType.CODING),
        make_decision(ProviderName.GROK, "grok-2", TaskType.CHAT),
    ]
    s = lb().routing_stats(decisions)
    assert s.task_distribution["chat"] == 2
    assert s.task_distribution["coding"] == 1


def test_top_models_limit():
    scores = [make_score(f"grok/model-{i}", float(i) / 10) for i in range(1, 8)]
    stats = lb().provider_stats(scores)
    top = lb().top_models(stats, limit=3)
    assert len(top) == 3


def test_cheapest_models_no_cost():
    scores = [make_score("grok/grok-2", 0.8)]
    stats = lb().provider_stats(scores)
    cheapest = lb().cheapest_models(stats)
    assert isinstance(cheapest, list)
