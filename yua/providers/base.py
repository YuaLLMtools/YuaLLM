"""
YuaLLM · Provider Base
Abstract interface for all LLM provider adapters.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class TaskType(Enum):
    CHAT = "chat"
    REASONING = "reasoning"
    CODING = "coding"
    SUMMARIZATION = "summarization"
    CREATIVE = "creative"
    ANALYSIS = "analysis"
    SIMPLE = "simple"


class ProviderName(Enum):
    GROK = "grok"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GROQ = "groq"


@dataclass
class ProviderModel:
    provider: ProviderName
    model_id: str
    context_window: int
    cost_per_1k_input: float   # USD
    cost_per_1k_output: float  # USD
    strengths: list[TaskType] = field(default_factory=list)
    supports_streaming: bool = True

    def cost_for(self, input_tokens: int, output_tokens: int) -> float:
        return (
            input_tokens / 1000 * self.cost_per_1k_input
            + output_tokens / 1000 * self.cost_per_1k_output
        )

    def name(self) -> str:
        return f"{self.provider.value}/{self.model_id}"


@dataclass
class LLMResponse:
    provider: ProviderName
    model_id: str
    content: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    task_type: TaskType
    cost_usd: float = 0.0

    def __post_init__(self) -> None:
        if self.cost_usd == 0.0 and self.input_tokens > 0:
            pass  # cost is set externally after response

    def summary(self) -> str:
        return (
            f"{self.provider.value}/{self.model_id} "
            f"| {self.latency_ms:.0f}ms "
            f"| {self.input_tokens + self.output_tokens} tokens "
            f"| ${self.cost_usd:.5f}"
        )


# Registry of known models
KNOWN_MODELS: list[ProviderModel] = [
    ProviderModel(
        provider=ProviderName.GROK,
        model_id="grok-2",
        context_window=131_072,
        cost_per_1k_input=0.002,
        cost_per_1k_output=0.010,
        strengths=[TaskType.REASONING, TaskType.ANALYSIS, TaskType.CHAT],
    ),
    ProviderModel(
        provider=ProviderName.GROK,
        model_id="grok-2-mini",
        context_window=131_072,
        cost_per_1k_input=0.0002,
        cost_per_1k_output=0.0005,
        strengths=[TaskType.SIMPLE, TaskType.CHAT],
    ),
    ProviderModel(
        provider=ProviderName.ANTHROPIC,
        model_id="claude-sonnet-4-6",
        context_window=200_000,
        cost_per_1k_input=0.003,
        cost_per_1k_output=0.015,
        strengths=[TaskType.CODING, TaskType.ANALYSIS, TaskType.REASONING],
    ),
    ProviderModel(
        provider=ProviderName.ANTHROPIC,
        model_id="claude-haiku-4-5",
        context_window=200_000,
        cost_per_1k_input=0.0008,
        cost_per_1k_output=0.004,
        strengths=[TaskType.SIMPLE, TaskType.CHAT, TaskType.SUMMARIZATION],
    ),
    ProviderModel(
        provider=ProviderName.OPENAI,
        model_id="gpt-4o",
        context_window=128_000,
        cost_per_1k_input=0.0025,
        cost_per_1k_output=0.010,
        strengths=[TaskType.CODING, TaskType.CREATIVE, TaskType.CHAT],
    ),
    ProviderModel(
        provider=ProviderName.OPENAI,
        model_id="gpt-4o-mini",
        context_window=128_000,
        cost_per_1k_input=0.00015,
        cost_per_1k_output=0.0006,
        strengths=[TaskType.SIMPLE, TaskType.SUMMARIZATION],
    ),
    ProviderModel(
        provider=ProviderName.GROQ,
        model_id="llama-3.3-70b",
        context_window=128_000,
        cost_per_1k_input=0.00059,
        cost_per_1k_output=0.00079,
        strengths=[TaskType.CHAT, TaskType.REASONING, TaskType.CODING],
    ),
]


def get_model(provider: ProviderName, model_id: str) -> Optional[ProviderModel]:
    for m in KNOWN_MODELS:
        if m.provider == provider and m.model_id == model_id:
            return m
    return None


def models_for_task(task: TaskType) -> list[ProviderModel]:
    return [m for m in KNOWN_MODELS if task in m.strengths]
