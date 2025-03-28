<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=200&section=header&text=YuaLLM&fontSize=72&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=LLM%20Router%20%26%20Orchestrator&descAlignY=58&descAlign=50" />
</p>

<p align="center">
  <a href="https://github.com/yuallm-dev/YuaLLM/actions/workflows/ci.yml"><img src="https://github.com/yuallm-dev/YuaLLM/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://pypi.org/project/yuallm/"><img src="https://img.shields.io/pypi/v/yuallm.svg" alt="PyPI" /></a>
  <img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/license-MIT-green" alt="MIT" />
</p>

<p align="center">
  Route prompts to the right LLM automatically — Grok, Anthropic, OpenAI, or Groq —<br/>
  based on task type, budget, and quality scoring. No manual model selection needed.
</p>

---

## Why YuaLLM

Most LLM applications hardcode a single model and call it a day. That works fine until you hit a rate limit, a cost spike, or a task that your default model handles poorly. YuaLLM solves this by sitting between your code and the providers.

The router detects what kind of task you're sending — coding, reasoning, summarization, creative writing — and picks the best-fit model automatically. Grok is the primary provider because it's fast and cost-efficient for most analytical work, but the system falls back to Anthropic, OpenAI, or Groq when the task or budget calls for it.

The quality scorer evaluates responses along four dimensions: length adequacy, completeness, refusal-free delivery, and task alignment. The budget tracker records every call and gives you cost breakdowns by provider and model. The alert system tells you when something goes wrong — cost overruns, quality failures, provider errors.

The whole thing is pure Python with no mandatory API keys at install time. You bring your own keys.

---

## Install

```bash
pip install yuallm
```

## Quick Start

```bash
yua setup          # configure API keys (~/.yuallm/.env)
yua route "Explain how transformers work step by step"
yua cost --input-tokens 500 --output-tokens 1000
yua score "Here is a detailed explanation of transformers..."
```

---

## Python API

### Routing

```python
from yua.router.llm_router import LLMRouter, RouterConfig
from yua.providers.base import ProviderName

router = LLMRouter()

# Auto-route based on task detection
decision = router.route("Implement a binary search tree in Python")
print(decision.provider.value)       # anthropic
print(decision.model_id)             # claude-sonnet-4-6
print(decision.task_type.value)      # coding
print(f"${decision.estimated_cost_usd:.6f}")

# With preferences
config = RouterConfig(prefer_cheap=True, max_cost_per_call=0.001)
decision = router.route("Summarize this article", config)

# Disable a provider
config = RouterConfig(disabled_providers=[ProviderName.OPENAI])

# Force a specific model
config = RouterConfig(force_model="grok/grok-2-mini")

# Batch routing
decisions = router.route_batch(["Hello", "Write a poem", "Debug this code"])
```

### Quality Scoring

```python
from yua.scorer.quality_scorer import QualityScorer
from yua.providers.base import LLMResponse, ProviderName, TaskType

resp = LLMResponse(
    provider=ProviderName.GROK,
    model_id="grok-2",
    content="Here is a comprehensive explanation...",
    input_tokens=100,
    output_tokens=200,
    latency_ms=450.0,
    task_type=TaskType.REASONING,
)

score = QualityScorer().score(resp)
print(score.overall, score.verdict)    # 0.84  good
print(score.passed())                  # True

# Pick best from multiple responses
best = QualityScorer().best_response([resp_a, resp_b, resp_c])
```

### Budget Tracking

```python
from yua.budget.cost_calculator import CostCalculator
from yua.providers.base import ProviderName

calc = CostCalculator()
calc.record(ProviderName.GROK, "grok-2", input_tokens=500, output_tokens=1200)
calc.record(ProviderName.ANTHROPIC, "claude-haiku-4-5", input_tokens=300, output_tokens=800)

summary = calc.summary()
print(f"Total: ${summary.total_cost_usd:.4f} across {summary.total_calls} calls")

by_provider = calc.cost_by_provider()   # {"grok": 0.0130, "anthropic": 0.0056}
by_model = calc.cost_by_model()

# Compare models before committing
comparisons = calc.compare_models(input_tokens=500, output_tokens=1000)
# Returns: [("openai/gpt-4o-mini", 0.000675), ..., ("anthropic/claude-sonnet-4-6", 0.0165)]
```

### Alerts

```python
from yua.alerts.notifier import YuaNotifier

notifier = YuaNotifier()
notifier.alert_cost_overrun("grok/grok-2", actual=0.05, budget=0.01)
notifier.alert_quality_failure("grok/grok-2-mini", score=0.34)
notifier.alert_fallback("grok/grok-2", "anthropic/claude-haiku-4-5", reason="timeout")
notifier.alert_provider_error("openai/gpt-4o", error="rate limit exceeded")
```

### Analytics

```python
from yua.analytics.leaderboard import Leaderboard

lb = Leaderboard()
stats = lb.provider_stats(quality_scores)      # ranked ProviderStats list
top3 = lb.top_models(stats, limit=3)
cheapest = lb.cheapest_models(stats)

routing = lb.routing_stats(route_decisions)
print(routing.fallback_rate)                   # 0.12
print(routing.task_distribution)               # {"chat": 45, "coding": 22, ...}
```

---

## Architecture

```
yua/
  providers/    ← model registry, ProviderName, TaskType, LLMResponse
  router/       ← LLMRouter — task detection, scoring, fallback logic
  scorer/       ← QualityScorer — 4-dimension response evaluation
  budget/       ← CostCalculator — per-call cost tracking
  analytics/    ← Leaderboard — provider and routing statistics
  alerts/       ← YuaNotifier — cost, quality, and error alerts
  cli.py        ← yua CLI entry point
```

Routing is a pure scoring function — no HTTP calls, no async, no side effects. You plug in your own provider SDK on top and pass the responses back through the scorer and budget tracker.

---

## Provider Coverage

| Provider | Models | Primary use |
|----------|--------|------------|
| **Grok** (xAI) | `grok-2`, `grok-2-mini` | Default — reasoning, analysis |
| **Anthropic** | `claude-sonnet-4-6`, `claude-haiku-4-5` | Coding, long-context |
| **OpenAI** | `gpt-4o`, `gpt-4o-mini` | Creative, general |
| **Groq** | `llama-3.3-70b` | Open-weight, fast |

---

## Configuration

After `yua setup`, keys are stored in `~/.yuallm/.env`:

```
GROK_API_KEY=xai-...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
```

---

## Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=yua --cov-report=term-missing
```

93 tests, pure logic — no API calls.

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs go to `develop`, not `main`.

---

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=20,11,6&height=120&section=footer" />
</p>