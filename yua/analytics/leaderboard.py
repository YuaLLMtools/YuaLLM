"""
YuaLLM · Provider Leaderboard
Aggregates quality scores and routing stats across providers.
"""

from __future__ import annotations

from dataclasses import dataclass

from yua.scorer.quality_scorer import QualityScore
from yua.router.llm_router import RouteDecision
from yua.providers.base import ProviderName


@dataclass
class ProviderStats:
    provider_model: str
    total_calls: int
    avg_quality: float
    avg_latency_ms: float
    total_cost_usd: float
    pass_rate: float       # % responses scoring >= 0.6
    rank: int


@dataclass
class RoutingStats:
    total_routed: int
    primary_used: int
    fallback_used: int
    fallback_rate: float
    task_distribution: dict[str, int]
    most_routed_model: str


class Leaderboard:
    def provider_stats(
        self,
        scores: list[QualityScore],
        latencies: dict[str, float] | None = None,
        costs: dict[str, float] | None = None,
    ) -> list[ProviderStats]:
        if not scores:
            return []

        grouped: dict[str, list[QualityScore]] = {}
        for s in scores:
            grouped.setdefault(s.provider_model, []).append(s)

        result = []
        for model, model_scores in grouped.items():
            avg_q = sum(s.overall for s in model_scores) / len(model_scores)
            pass_r = sum(1 for s in model_scores if s.passed()) / len(model_scores)
            result.append(ProviderStats(
                provider_model=model,
                total_calls=len(model_scores),
                avg_quality=round(avg_q, 4),
                avg_latency_ms=round(latencies.get(model, 0.0) if latencies else 0.0, 1),
                total_cost_usd=round(costs.get(model, 0.0) if costs else 0.0, 6),
                pass_rate=round(pass_r, 4),
                rank=0,
            ))

        result.sort(key=lambda s: (s.avg_quality, s.pass_rate), reverse=True)
        for i, s in enumerate(result):
            s.rank = i + 1
        return result

    def routing_stats(self, decisions: list[RouteDecision]) -> RoutingStats:
        if not decisions:
            return RoutingStats(0, 0, 0, 0.0, {}, "")

        primary = sum(1 for d in decisions if not d.fallback_used)
        fallback = sum(1 for d in decisions if d.fallback_used)

        task_dist: dict[str, int] = {}
        for d in decisions:
            k = d.task_type.value
            task_dist[k] = task_dist.get(k, 0) + 1

        model_counts: dict[str, int] = {}
        for d in decisions:
            k = d.model_name()
            model_counts[k] = model_counts.get(k, 0) + 1

        most_routed = max(model_counts, key=model_counts.get) if model_counts else ""

        return RoutingStats(
            total_routed=len(decisions),
            primary_used=primary,
            fallback_used=fallback,
            fallback_rate=round(fallback / len(decisions), 4),
            task_distribution=task_dist,
            most_routed_model=most_routed,
        )

    def top_models(self, stats: list[ProviderStats], limit: int = 5) -> list[ProviderStats]:
        return sorted(stats, key=lambda s: s.avg_quality, reverse=True)[:limit]

    def cheapest_models(self, stats: list[ProviderStats], limit: int = 5) -> list[ProviderStats]:
        return sorted(
            [s for s in stats if s.total_cost_usd > 0],
            key=lambda s: s.total_cost_usd,
        )[:limit]
