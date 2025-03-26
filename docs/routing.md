# Routing Architecture

YuaLLM routes every prompt through a three-stage pipeline: task detection → complexity estimation → model scoring.

## Task Detection

The router classifies each prompt into one of seven task types:

| Task | Trigger keywords |
|------|-----------------|
| `coding` | `def`, `class`, `import`, `implement`, `debug`, `fix the` |
| `analysis` | `analyze`, `evaluate`, `compare`, `trade-off` |
| `reasoning` | `reason`, `step by step`, `explain why`, `deduce` |
| `summarization` | `summarize`, `tldr`, `brief`, `shorten` |
| `creative` | `write`, `story`, `poem`, `essay`, `blog` |
| `simple` | Prompt under 20 words |
| `chat` | Everything else |

## Complexity Estimation

Token count (words × 4/3) maps to a complexity tier:

- `simple` — ≤ 100 tokens
- `medium` — 101–500 tokens
- `complex` — > 500 tokens

## Model Scoring

Each available model receives a composite score:

```
score = primary_provider_bonus (10)
      + task_strength_match    (5)
      + cheap_preference       (0–3, if prefer_cheap)
      + speed_preference       (0–2, if prefer_fast)
      + complexity_match       (2, mini↔simple or full↔complex)
```

The highest-scoring model wins. If its estimated cost exceeds `max_cost_per_call`, the cheapest available model is used instead.

## Provider Priority

Default primary: **Grok**. Fallback order depends on task scoring, not a fixed list.

```
Grok grok-2          → reasoning, analysis, chat
Grok grok-2-mini     → simple, chat (cheapest Grok)
Anthropic Sonnet 4.6 → coding, analysis
Anthropic Haiku 4.5  → simple, chat, summarization
OpenAI gpt-4o        → coding, creative
OpenAI gpt-4o-mini   → simple, summarization (cheapest overall)
Groq llama-3.3-70b  → chat, reasoning, coding (open-weight)
```

## RouterConfig Reference

```python
RouterConfig(
    primary_provider=ProviderName.GROK,   # default primary
    max_cost_per_call=0.10,               # USD budget per call
    prefer_fast=False,                    # favor smaller/cheaper as proxy
    prefer_cheap=False,                   # minimize cost score
    disabled_providers=[ProviderName.OPENAI],
    force_model="anthropic/claude-haiku-4-5",  # bypass scoring entirely
)
```