"""
YuaLLM · Cost Calculator
Tracks token usage and calculates costs per provider/model.
All arithmetic is pure — no external calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from yua.providers.base import KNOWN_MODELS, ProviderModel, ProviderName, get_model


@dataclass
class UsageRecord:
    provider: str
    model_id: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    session_id: str = ""

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


@dataclass
class BudgetSummary:
    total_cost_usd: float
    total_input_tokens: int
    total_output_tokens: int
    total_calls: int
    by_provider: dict[str, float]
    most_expensive_model: str
    cheapest_model: str


class CostCalculator:
    def __init__(self) -> None:
        self._records: list[UsageRecord] = []

    def estimate(
        self,
        provider: ProviderName,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        model = get_model(provider, model_id)
        if model is None:
            return 0.0
        return round(model.cost_for(input_tokens, output_tokens), 6)

    def estimate_from_text(
        self,
        provider: ProviderName,
        model_id: str,
        input_text: str,
        output_text: str,
    ) -> float:
        input_tokens = max(1, len(input_text.split()) * 4 // 3)
        output_tokens = max(1, len(output_text.split()) * 4 // 3)
        return self.estimate(provider, model_id, input_tokens, output_tokens)

    def record(
        self,
        provider: ProviderName,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        session_id: str = "",
    ) -> UsageRecord:
        cost = self.estimate(provider, model_id, input_tokens, output_tokens)
        record = UsageRecord(
            provider=provider.value,
            model_id=model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost_usd=cost,
            session_id=session_id,
        )
        self._records.append(record)
        return record

    def total_cost(self) -> float:
        return round(sum(r.cost_usd for r in self._records), 6)

    def cost_by_provider(self) -> dict[str, float]:
        result: dict[str, float] = {}
        for r in self._records:
            result[r.provider] = round(result.get(r.provider, 0.0) + r.cost_usd, 6)
        return result

    def cost_by_model(self) -> dict[str, float]:
        result: dict[str, float] = {}
        key = lambda r: f"{r.provider}/{r.model_id}"
        for r in self._records:
            k = key(r)
            result[k] = round(result.get(k, 0.0) + r.cost_usd, 6)
        return result

    def summary(self) -> BudgetSummary:
        if not self._records:
            return BudgetSummary(0.0, 0, 0, 0, {}, "", "")

        by_model = self.cost_by_model()
        most_exp = max(by_model, key=by_model.get) if by_model else ""
        cheapest = min(by_model, key=by_model.get) if by_model else ""

        return BudgetSummary(
            total_cost_usd=self.total_cost(),
            total_input_tokens=sum(r.input_tokens for r in self._records),
            total_output_tokens=sum(r.output_tokens for r in self._records),
            total_calls=len(self._records),
            by_provider=self.cost_by_provider(),
            most_expensive_model=most_exp,
            cheapest_model=cheapest,
        )

    def compare_models(self, input_tokens: int, output_tokens: int) -> list[tuple[str, float]]:
        results = []
        for model in KNOWN_MODELS:
            cost = model.cost_for(input_tokens, output_tokens)
            results.append((model.name(), round(cost, 6)))
        return sorted(results, key=lambda x: x[1])

    def reset(self) -> None:
        self._records.clear()
