"""Tests — yua.scorer.quality_scorer"""

import pytest
from yua.scorer.quality_scorer import QualityScorer, QualityScore
from yua.providers.base import LLMResponse, ProviderName, TaskType


def make_response(content: str, task: TaskType = TaskType.CHAT) -> LLMResponse:
    return LLMResponse(
        provider=ProviderName.GROK,
        model_id="grok-2",
        content=content,
        input_tokens=100,
        output_tokens=len(content.split()),
        latency_ms=500.0,
        task_type=task,
    )


def scorer() -> QualityScorer:
    return QualityScorer()


def test_score_returns_quality_score():
    s = scorer().score(make_response("This is a decent response about things."))
    assert isinstance(s, QualityScore)


def test_overall_bounded():
    s = scorer().score(make_response("hello"))
    assert 0.0 <= s.overall <= 1.0


def test_empty_content_low_score():
    s = scorer().score(make_response(""))
    assert s.overall < 0.5


def test_refusal_detected():
    s = scorer().score(make_response("I cannot help with that request."))
    assert s.refusal_score < 1.0


def test_no_refusal_full_score():
    s = scorer().score(make_response("Here is a detailed explanation of the topic you asked about."))
    assert s.refusal_score == 1.0


def test_long_response_higher_length_score():
    short = scorer().score(make_response("ok"))
    long = scorer().score(make_response("This is a much longer response. " * 20))
    assert long.length_score > short.length_score


def test_coding_alignment_with_code():
    resp = make_response("```python\ndef hello():\n    return 'world'\n```", TaskType.CODING)
    s = scorer().score(resp)
    assert s.alignment_score > 0.5


def test_verdict_excellent():
    s = scorer()
    assert s._verdict(0.90) == "excellent"


def test_verdict_good():
    s = scorer()
    assert s._verdict(0.75) == "good"


def test_verdict_acceptable():
    s = scorer()
    assert s._verdict(0.60) == "acceptable"


def test_verdict_poor():
    s = scorer()
    assert s._verdict(0.40) == "poor"


def test_verdict_failed():
    s = scorer()
    assert s._verdict(0.20) == "failed"


def test_passed_above_threshold():
    s = scorer().score(make_response("Here is a detailed and comprehensive response. " * 5))
    assert isinstance(s.passed(), bool)


def test_batch_score():
    responses = [make_response("Response one."), make_response("Response two. " * 10)]
    results = scorer().score_batch(responses)
    assert len(results) == 2


def test_best_response_returns_better():
    r1 = make_response("ok")
    r2 = make_response("This is a very detailed and complete response to your question. " * 5)
    best = scorer().best_response([r1, r2])
    assert best.content == r2.content


def test_best_response_single():
    r = make_response("Only one response here.")
    assert scorer().best_response([r]).content == r.content


def test_best_response_empty_raises():
    with pytest.raises(ValueError):
        scorer().best_response([])


def test_provider_model_in_score():
    s = scorer().score(make_response("test content"))
    assert "grok" in s.provider_model


def test_completeness_truncated():
    s = scorer()
    score = s._completeness_score("This response ends with ...")
    assert score < 1.0


def test_completeness_clean_ending():
    s = scorer()
    score = s._completeness_score("This response ends cleanly.")
    assert score == 1.0
