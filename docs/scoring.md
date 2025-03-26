# Quality Scoring

`QualityScorer` evaluates LLM responses across four dimensions, then combines them into an overall score.

## Score Components

### Length Score

Rewards responses that are substantively long enough. Uses a sigmoid-like curve against word count. Very short responses (≤ 5 words) score near zero; responses above ~100 words approach 1.0.

### Completeness Score

Checks whether the response ends cleanly:
- Trailing `...` or ellipsis → penalized
- Ends with proper punctuation or code block → 1.0
- Mid-sentence endings → 0.5

### Refusal Score

Detects unhelpful refusals by scanning for phrases like `"I cannot help"`, `"I'm not able to"`, `"I apologize"`, etc. A clean response scores 1.0. Any match → score drops.

### Alignment Score

Checks whether the response format matches the detected task type:
- `coding` task + code block present → high score
- `reasoning` task + structured explanation → bonus
- Mismatch between task and response format → reduced score

## Overall Score

```
overall = 0.30 × length
        + 0.25 × completeness
        + 0.25 × refusal
        + 0.20 × alignment
```

## Verdict Thresholds

| Score | Verdict |
|-------|---------|
| ≥ 0.85 | `excellent` |
| ≥ 0.70 | `good` |
| ≥ 0.55 | `acceptable` |
| ≥ 0.35 | `poor` |
| < 0.35 | `failed` |

## Passing Threshold

`QualityScore.passed()` returns `True` when `overall ≥ 0.50`.

## Usage

```python
from yua.scorer.quality_scorer import QualityScorer
from yua.providers.base import LLMResponse, ProviderName, TaskType

resp = LLMResponse(
    provider=ProviderName.GROK,
    model_id="grok-2",
    content="Here is a detailed explanation...",
    input_tokens=100,
    output_tokens=50,
    latency_ms=320.0,
    task_type=TaskType.CHAT,
)

score = QualityScorer().score(resp)
print(score.overall, score.verdict)  # 0.82  good
```

## Batch Scoring

```python
results = QualityScorer().score_batch([resp1, resp2, resp3])
best = QualityScorer().best_response([resp1, resp2, resp3])
```