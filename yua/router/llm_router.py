"""
YuaLLM · LLM Router
Routes prompts to the best provider/model based on task type,
complexity, cost budget, and provider availability.
Primary provider: Grok. Falls back to Anthropic, OpenAI, Groq.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from yua.providers.base import (
    KNOWN_MODELS,
    ProviderModel,
    ProviderName,
    TaskType,
    get_model,
    models_for_task,
)


@dataclass
class RouteDecision:
    provider: ProviderName
    model_id: str
    task_type: TaskType
    reason: str
    estimated_cost_usd: float
    fallback_used: bool = False

    def model_name(self) -> str:
        return f"{self.provider.value}/{self.model_id}"


@dataclass
class RouterConfig:
    primary_provider: ProviderName = ProviderName.GROK
    max_cost_per_call: float = 0.10        # USD
    prefer_fast: bool = False
    prefer_cheap: bool = False
    disabled_providers: list[ProviderName] = field(default_factory=list)
    force_model: Optional[str] = None      # "grok/grok-2" format


class LLMRouter:
    """
    Routes a prompt to the optimal LLM provider.
    Grok is the primary provider — used for reasoning and analysis.
    Falls back to other providers based on task type and config.
    """

    COMPLEXITY_THRESHOLDS = {
        "simple": 100,      # tokens
        "medium": 500,
        "complex": 2000,
    }

    def detect_task_type(self, prompt: str) -> TaskType:
        prompt_lower = prompt.lower()
        if any(k in prompt_lower for k in ["def ", "class ", "import ", "function", "code", "implement", "debug", "fix the"]):
            return TaskType.CODING
        if any(k in prompt_lower for k in ["analyze", "analysis", "evaluate", "assess", "compare", "versus", "trade-off"]):
            return TaskType.ANALYSIS
        if any(k in prompt_lower for k in ["reason", "think", "step by step", "explain why", "logic", "deduce"]):
            return TaskType.REASONING
        if any(k in prompt_lower for k in ["summarize", "summary", "tldr", "brief", "shorten"]):
            return TaskType.SUMMARIZATION
        if any(k in prompt_lower for k in ["write", "story", "creative", "poem", "essay", "blog"]):
            return TaskType.CREATIVE
        if len(prompt.split()) < 20:
            return TaskType.SIMPLE
        return TaskType.CHAT

    def estimate_tokens(self, text: str) -> int:
        return max(1, len(text.split()) * 4 // 3)

    def estimate_complexity(self, prompt: str) -> str:
        tokens = self.estimate_tokens(prompt)
        if tokens <= self.COMPLEXITY_THRESHOLDS["simple"]:
            return "simple"
        if tokens <= self.COMPLEXITY_THRESHOLDS["medium"]:
            return "medium"
        return "complex"

    def _available_models(self, config: RouterConfig) -> list[ProviderModel]:
        return [
            m for m in KNOWN_MODELS
            if m.provider not in config.disabled_providers
        ]

    def _score_model(
        self,
        model: ProviderModel,
        task: TaskType,
        complexity: str,
        config: RouterConfig,
    ) -> float:
        score = 0.0

        # Primary provider bonus
        if model.provider == config.primary_provider:
            score += 10.0

        # Task strength match
        if task in model.strengths:
            score += 5.0

        # Cost preference
        avg_cost = (model.cost_per_1k_input + model.cost_per_1k_output) / 2
        if config.prefer_cheap:
            score += max(0, 3.0 - avg_cost * 100)

        # Speed preference (use cheaper/smaller models as proxy)
        if config.prefer_fast:
            score += max(0, 2.0 - avg_cost * 50)

        # Complexity match
        if complexity == "simple" and "mini" in model.model_id:
            score += 2.0
        if complexity == "complex" and "mini" not in model.model_id:
            score += 2.0

        return score

    def route(self, prompt: str, config: Optional[RouterConfig] = None) -> RouteDecision:
        if config is None:
            config = RouterConfig()

        # Force model override
        if config.force_model:
            parts = config.force_model.split("/", 1)
            if len(parts) == 2:
                try:
                    provider = ProviderName(parts[0])
                    model = get_model(provider, parts[1])
                    if model:
                        task = self.detect_task_type(prompt)
                        est_tokens = self.estimate_tokens(prompt)
                        cost = model.cost_for(est_tokens, est_tokens * 2)
                        return RouteDecision(
                            provider=provider,
                            model_id=parts[1],
                            task_type=task,
                            reason=f"forced by config: {config.force_model}",
                            estimated_cost_usd=cost,
                        )
                except ValueError:
                    pass

        task = self.detect_task_type(prompt)
        complexity = self.estimate_complexity(prompt)
        available = self._available_models(config)

        if not available:
            raise ValueError("No available providers after applying disabled_providers filter")

        # Score and rank
        scored = sorted(
            available,
            key=lambda m: self._score_model(m, task, complexity, config),
            reverse=True,
        )

        best = scored[0]
        est_tokens = self.estimate_tokens(prompt)
        cost = best.cost_for(est_tokens, est_tokens * 2)

        # Check cost budget — find cheapest within budget if over
        if cost > config.max_cost_per_call:
            cheap = sorted(available, key=lambda m: m.cost_per_1k_output)
            best = cheap[0]
            cost = best.cost_for(est_tokens, est_tokens * 2)
            fallback = True
            reason = f"budget exceeded — switched to cheapest: {best.name()}"
        else:
            fallback = best.provider != config.primary_provider
            reason = (
                f"primary provider match: {best.name()}"
                if not fallback
                else f"fallback to {best.name()} — primary provider unavailable or lower score"
            )

        return RouteDecision(
            provider=best.provider,
            model_id=best.model_id,
            task_type=task,
            reason=reason,
            estimated_cost_usd=round(cost, 6),
            fallback_used=fallback,
        )

    def route_batch(self, prompts: list[str], config: Optional[RouterConfig] = None) -> list[RouteDecision]:
        return [self.route(p, config) for p in prompts]
