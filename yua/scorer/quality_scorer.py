"""
YuaLLM · Quality Scorer
Scores LLM response quality based on observable signals:
length, completeness, refusal detection, and task alignment.
No external models required — pure heuristics.
"""

from __future__ import annotations

from dataclasses import dataclass

from yua.providers.base import LLMResponse, TaskType


@dataclass
class QualityScore:
    provider_model: str
    task_type: str
    length_score: float       # 0.0 – 1.0
    completeness_score: float
    refusal_score: float      # 1.0 = no refusal
    alignment_score: float
    overall: float
    verdict: str

    def passed(self, threshold: float = 0.6) -> bool:
        return self.overall >= threshold


REFUSAL_PHRASES = [
    "i cannot", "i can't", "i'm unable", "as an ai",
    "i don't have the ability", "i'm not able to",
    "i won't", "i apologize", "i'm sorry, but i",
]

TRUNCATION_SIGNALS = [
    "...", "[continues]", "[truncated]", "to be continued",
]


class QualityScorer:
    MIN_USEFUL_CHARS = 50
    IDEAL_CHARS = {
        TaskType.SIMPLE: 200,
        TaskType.CHAT: 400,
        TaskType.SUMMARIZATION: 600,
        TaskType.REASONING: 1000,
        TaskType.ANALYSIS: 1200,
        TaskType.CODING: 800,
        TaskType.CREATIVE: 600,
    }

    def _length_score(self, content: str, task: TaskType) -> float:
        n = len(content)
        if n < self.MIN_USEFUL_CHARS:
            return 0.1
        ideal = self.IDEAL_CHARS.get(task, 500)
        if n >= ideal:
            return 1.0
        return min(1.0, n / ideal)

    def _completeness_score(self, content: str) -> float:
        content_stripped = content.strip()
        if not content_stripped:
            return 0.0
        # Penalize if ends mid-sentence
        ends_cleanly = content_stripped[-1] in ".!?\"'`)"
        truncated = any(sig in content_stripped[-50:] for sig in TRUNCATION_SIGNALS)
        score = 1.0
        if not ends_cleanly:
            score -= 0.2
        if truncated:
            score -= 0.4
        return max(0.0, score)

    def _refusal_score(self, content: str) -> float:
        content_lower = content.lower()
        hits = sum(1 for p in REFUSAL_PHRASES if p in content_lower)
        if hits == 0:
            return 1.0
        if hits == 1:
            return 0.5
        return 0.1

    def _alignment_score(self, content: str, task: TaskType) -> float:
        content_lower = content.lower()
        task_signals = {
            TaskType.CODING: ["def ", "class ", "```", "function", "return", "import"],
            TaskType.REASONING: ["because", "therefore", "thus", "step", "first", "second"],
            TaskType.SUMMARIZATION: ["summary", "key point", "in brief", "main", "overall"],
            TaskType.ANALYSIS: ["however", "on the other hand", "consider", "factor", "impact"],
            TaskType.CREATIVE: ["once", "the", "her", "his", "they", "story"],
        }
        signals = task_signals.get(task, [])
        if not signals:
            return 0.8
        matches = sum(1 for s in signals if s in content_lower)
        return min(1.0, 0.4 + matches * 0.15)

    def _verdict(self, score: float) -> str:
        if score >= 0.85:
            return "excellent"
        if score >= 0.70:
            return "good"
        if score >= 0.55:
            return "acceptable"
        if score >= 0.35:
            return "poor"
        return "failed"

    def score(self, response: LLMResponse) -> QualityScore:
        task = response.task_type
        ls = self._length_score(response.content, task)
        cs = self._completeness_score(response.content)
        rs = self._refusal_score(response.content)
        als = self._alignment_score(response.content, task)

        overall = round(ls * 0.25 + cs * 0.25 + rs * 0.30 + als * 0.20, 4)

        return QualityScore(
            provider_model=f"{response.provider.value}/{response.model_id}",
            task_type=task.value,
            length_score=round(ls, 4),
            completeness_score=round(cs, 4),
            refusal_score=round(rs, 4),
            alignment_score=round(als, 4),
            overall=overall,
            verdict=self._verdict(overall),
        )

    def score_batch(self, responses: list[LLMResponse]) -> list[QualityScore]:
        return [self.score(r) for r in responses]

    def best_response(self, responses: list[LLMResponse]) -> LLMResponse:
        if not responses:
            raise ValueError("No responses to evaluate")
        scores = self.score_batch(responses)
        best_idx = max(range(len(scores)), key=lambda i: scores[i].overall)
        return responses[best_idx]
