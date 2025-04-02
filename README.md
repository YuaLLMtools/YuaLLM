<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=220&section=header&text=YuaLLM&fontSize=80&fontColor=ffffff&animation=fadeIn&fontAlignY=38&desc=LLM%20Router%20%26%20Orchestrator&descAlignY=58&descAlign=50&descSize=22" />
</p>

<p align="center">
  <a href="https://readme-typing-svg.demolab.com">
    <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&pause=1000&color=6EBBFF&center=true&vCenter=true&width=520&lines=Route+prompts+to+the+right+LLM+automatically.;Grok+%7C+Anthropic+%7C+OpenAI+%7C+Groq.;Task-aware+routing+with+quality+scoring.;Built+for+Solana+AI+agents+and+crypto+tools." alt="Typing SVG" />
  </a>
</p>

<p align="center">
  <a href="https://github.com/YuaLLMtools/YuaLLM/actions/workflows/ci.yml">
    <img src="https://github.com/YuaLLMtools/YuaLLM/actions/workflows/ci.yml/badge.svg" alt="CI" />
  </a>
  <img src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white" alt="Python 3.10+" />
  <img src="https://img.shields.io/badge/license-MIT-22c55e" alt="MIT" />
  <img src="https://img.shields.io/badge/tests-93%20passing-22c55e" alt="93 tests" />
  <img src="https://img.shields.io/badge/providers-Grok%20%7C%20Anthropic%20%7C%20OpenAI%20%7C%20Groq-6366f1" alt="Providers" />
</p>

<p align="center">
  <a href="https://pump.fun/coin/o1u4V1yZaKR85qwghmBvyBPqHs6EHjCUVVE8HEbpump">
    <img src="https://img.shields.io/badge/%24YLLM-o1u4V1yZ...HEbpump-9945FF?style=for-the-badge&logo=solana&logoColor=white" alt="$YLLM CA" />
  </a>
</p>

<p align="center">
  <code>$YLLM &nbsp;|&nbsp; o1u4V1yZaKR85qwghmBvyBPqHs6EHjCUVVE8HEbpump</code>
</p>

<br/>

<p align="center">
  <img src="https://skillicons.dev/icons?i=py,rust,go,ts&perline=4" />
</p>

<br/>

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=3" />

## The Problem

Every AI agent makes the same mistake at some point: it picks one model and uses it for everything. That one model gets rate-limited on a Thursday afternoon when traffic spikes. It costs 20x more than necessary for a task that needed two sentences. It refuses a request that a different provider would have handled perfectly. When you are running a trading bot on Solana at 3am and your signal generation pipeline starts failing because one upstream LLM is saturated, you need the system to reroute itself without human intervention.

YuaLLM was built to solve exactly that. It sits between your application code and the LLM providers, acting as an intelligent dispatch layer. You send a prompt. YuaLLM classifies the task, estimates complexity and cost, scores every available model, and routes the call to the best fit. If that provider fails or blows the budget, it falls back automatically. Your application code never needs to know which provider handled the request.

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=3" />

## Built for Crypto and Solana AI Agents

The crypto AI agent space has a specific set of constraints that most LLM orchestration libraries ignore. Latency matters at the block level. Cost matters when you are processing thousands of on-chain events per hour. Quality matters when a poorly scored response triggers a trade or sends a Telegram alert that spooks a community.

YuaLLM was designed with these constraints in mind. When a Solana wallet tracker fires and needs to narrate a whale movement, that is a `chat` task and it routes to `grok-2-mini` at $0.0002 per 1k tokens. When a signal engine needs to reason through a complex DeFi position across three protocols, that is a `reasoning` task and it routes to `grok-2` which handles multi-step analytical work better. When a code generation agent is writing a new strategy module, it routes to Anthropic Sonnet because coding is where it consistently outperforms.

The result is a system where each component of your Solana AI stack gets the right model for its job, without any of them needing to know about the others.

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=3" />

## Install

```bash
pip install yuallm
```

```bash
yua setup          # configure API keys, saved to ~/.yuallm/.env
yua route "Explain the recent SPL token volume spike on Raydium"
yua cost --input-tokens 500 --output-tokens 1000
yua score "Here is the on-chain analysis you requested..."
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=3" />

## How Routing Works

When a prompt arrives, the router runs three stages in sequence before selecting a model.

**Stage 1 — Task Classification**

The router scans the prompt for semantic signals and classifies it into one of seven task types. A prompt containing `def`, `class`, or `implement` becomes a `coding` task. One with `analyze`, `compare`, or `evaluate` becomes an `analysis` task. `step by step` or `explain why` maps to `reasoning`. `summarize` or `tldr` maps to `summarization`. Anything under 20 words is `simple`. Everything else defaults to `chat`. This classification drives the model selection logic downstream.

**Stage 2 — Complexity Estimation**

Token count is approximated from word count using a 4/3 multiplier. Under 100 tokens is `simple`, 100 to 500 is `medium`, above 500 is `complex`. Complexity affects model selection: mini models get a bonus for simple tasks, full-size models get a bonus for complex ones.

**Stage 3 — Model Scoring**

Every available model receives a composite score based on four factors: primary provider bonus (Grok gets +10 by default), task strength match (+5 if the model is optimized for the detected task), cost preference bonus (scaled by pricing when `prefer_cheap=True`), and complexity tier bonus. The highest-scoring model wins. If its estimated cost exceeds `max_cost_per_call`, the router switches to the cheapest available model instead of raising an error.

```python
from yua.router.llm_router import LLMRouter, RouterConfig
from yua.providers.base import ProviderName

router = LLMRouter()

# Basic routing — task detection is automatic
decision = router.route("Implement a Solana SPL token transfer function in Rust")
print(decision.provider.value)          # anthropic
print(decision.model_id)               # claude-sonnet-4-6
print(decision.task_type.value)        # coding
print(f"${decision.estimated_cost_usd:.6f}")

# Budget-constrained routing
config = RouterConfig(prefer_cheap=True, max_cost_per_call=0.001)
decision = router.route("Summarize today's Solana DEX volume", config)

# Disable a provider entirely
config = RouterConfig(disabled_providers=[ProviderName.OPENAI])

# Override to a specific model, bypassing scoring
config = RouterConfig(force_model="grok/grok-2-mini")

# Batch routing for pipelines that process multiple prompts
decisions = router.route_batch([
    "Narrate this whale wallet movement",
    "Write a Python function to fetch Raydium pool data",
    "Analyze the RSI divergence on SOL/USDC",
])
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=3" />

## Quality Scoring

Routing a prompt to the right model is only half the problem. You also need to know whether the response you got back is actually usable. YuaLLM includes a quality scorer that evaluates every response across four independent dimensions.

**Length score** measures whether the response is substantively long enough for the task. A two-word reply to a complex analytical question scores near zero. A well-developed paragraph approaches 1.0.

**Completeness score** checks whether the response ended cleanly or got cut off. Responses that trail off with ellipsis or stop mid-sentence take a penalty. Responses that end with proper punctuation or a closing code block score full marks.

**Refusal score** scans for phrases that indicate the model declined the request rather than answering it. Phrases like "I cannot help with that" or "I'm not able to" drop the score. A clean, on-topic response scores 1.0.

**Alignment score** checks whether the response format matches the task type. A coding task that returns a code block scores higher than one that returns plain prose. A reasoning task that walks through steps scores higher than one that skips to a conclusion.

The overall score is a weighted average: 30% length, 25% completeness, 25% refusal, 20% alignment. Scores above 0.70 are `good`, above 0.85 are `excellent`. Anything below 0.50 fails.

```python
from yua.scorer.quality_scorer import QualityScorer
from yua.providers.base import LLMResponse, ProviderName, TaskType

resp = LLMResponse(
    provider=ProviderName.GROK,
    model_id="grok-2",
    content="Here is a comprehensive breakdown of the on-chain activity...",
    input_tokens=100,
    output_tokens=200,
    latency_ms=450.0,
    task_type=TaskType.ANALYSIS,
)

score = QualityScorer().score(resp)
print(score.overall, score.verdict)    # 0.84  good
print(score.passed())                  # True

# Score a batch of responses
results = QualityScorer().score_batch([resp_a, resp_b, resp_c])

# Pick the best one automatically
best = QualityScorer().best_response([resp_a, resp_b, resp_c])
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=3" />

## Budget Tracking

When you are running an AI agent at scale, cost tracking is not optional. YuaLLM records every call with full token detail and lets you query costs any way you need: by provider, by model, by call, or as a total summary.

```python
from yua.budget.cost_calculator import CostCalculator
from yua.providers.base import ProviderName

calc = CostCalculator()
calc.record(ProviderName.GROK, "grok-2", input_tokens=500, output_tokens=1200)
calc.record(ProviderName.ANTHROPIC, "claude-haiku-4-5", input_tokens=300, output_tokens=800)

summary = calc.summary()
print(f"Total: ${summary.total_cost_usd:.4f} across {summary.total_calls} calls")
print(f"Tokens: {summary.total_input_tokens} in / {summary.total_output_tokens} out")

# Break down by provider or model
by_provider = calc.cost_by_provider()   # {"grok": 0.0130, "anthropic": 0.0056}
by_model    = calc.cost_by_model()      # {"grok/grok-2": 0.0130, ...}

# Compare all models before choosing one for a new use case
comparisons = calc.compare_models(input_tokens=500, output_tokens=1000)
# Returns sorted list: [("openai/gpt-4o-mini", 0.000675), ..., ("anthropic/claude-sonnet-4-6", 0.0165)]

# Estimate from raw text without counting tokens manually
cost = calc.estimate_from_text(ProviderName.GROK, "grok-2", prompt_text, response_text)
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=3" />

## Alerts

When something goes wrong in a live agent pipeline, you want to know about it before the user does. YuaLLM includes an alert system with four built-in alert types covering the most common failure modes.

```python
from yua.alerts.notifier import YuaNotifier

notifier = YuaNotifier()

# Cost overrun: actual spend exceeded the expected budget
notifier.alert_cost_overrun("grok/grok-2", actual=0.05, budget=0.01)

# Quality failure: response scored below acceptable threshold
notifier.alert_quality_failure("grok/grok-2-mini", score=0.34)

# Fallback triggered: primary provider was replaced
notifier.alert_fallback("grok/grok-2", "anthropic/claude-haiku-4-5", reason="timeout")

# Provider error: hard failure from upstream
notifier.alert_provider_error("openai/gpt-4o", error="rate limit exceeded")

# All alerts are stored in history
print(notifier.history())   # list of YuaAlert objects
```

Alerts format to both terminal and Telegram out of the box. Plug `format_telegram()` directly into your bot dispatcher.

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=3" />

## Analytics and Leaderboard

After running an agent for a while, you want to know which providers are actually performing. The leaderboard module aggregates quality scores and routing decisions into ranked statistics.

```python
from yua.analytics.leaderboard import Leaderboard

lb = Leaderboard()

# Rank providers by average quality across all recorded scores
stats = lb.provider_stats(quality_scores)
for s in stats:
    print(s.rank, s.provider_model, f"{s.avg_quality:.0%}", f"pass rate: {s.pass_rate:.0%}")

# Filter to top performers or cheapest options
top3     = lb.top_models(stats, limit=3)
cheapest = lb.cheapest_models(stats)

# Routing analytics: how is the system distributing calls?
routing = lb.routing_stats(route_decisions)
print(f"Total routed: {routing.total_routed}")
print(f"Primary used: {routing.primary_used}")
print(f"Fallback rate: {routing.fallback_rate:.0%}")
print(f"Task breakdown: {routing.task_distribution}")
# {"chat": 45, "coding": 22, "analysis": 18, "reasoning": 8}
```

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=3" />

## Architecture

```
yua/
  providers/    model registry, ProviderName, TaskType, LLMResponse dataclasses
  router/       LLMRouter: task classification, complexity, cost scoring, fallback
  scorer/       QualityScorer: 4-dimension weighted response evaluation
  budget/       CostCalculator: token cost tracking and model comparison
  analytics/    Leaderboard: provider stats, routing stats, pass rates
  alerts/       YuaNotifier: cost, quality, fallback, and error alerts
  cli.py        yua CLI entry point (pip installable)
```

The core routing engine is a pure function. No HTTP calls, no async, no side effects. It takes a prompt and a config object and returns a decision. You wire your own provider SDK on top, call the model, and pass the response back through the scorer and budget tracker. This design means YuaLLM is easy to test, easy to mock at the boundary, and easy to drop into any existing agent architecture.

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=3" />

## Provider Reference

| Provider | Model | Context | Input per 1k | Output per 1k | Strengths |
|----------|-------|---------|-------------|--------------|-----------|
| Grok (xAI) | `grok-2` | 131k | $0.002 | $0.010 | Reasoning, Analysis, Chat |
| Grok (xAI) | `grok-2-mini` | 131k | $0.0002 | $0.0005 | Simple, Chat |
| Anthropic | `claude-sonnet-4-6` | 200k | $0.003 | $0.015 | Coding, Analysis |
| Anthropic | `claude-haiku-4-5` | 200k | $0.0008 | $0.004 | Simple, Summarization |
| OpenAI | `gpt-4o` | 128k | $0.0025 | $0.010 | Coding, Creative |
| OpenAI | `gpt-4o-mini` | 128k | $0.00015 | $0.0006 | Simple, Summarization |
| Groq | `llama-3.3-70b` | 128k | $0.00059 | $0.00079 | Chat, Reasoning, Coding |

Grok is the default primary provider. The router gives it a scoring bonus for every request and only falls back to other providers when task affinity, cost constraints, or `disabled_providers` in config push a different model higher.

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=3" />

## Configuration

Run `yua setup` once to configure your API keys. They are saved to `~/.yuallm/.env` and loaded automatically on each run.

```bash
GROK_API_KEY=xai-...
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GROQ_API_KEY=gsk_...
```

The router works with any subset of providers. If you only have a Grok key, it will route everything through Grok. If you add an Anthropic key later, coding tasks will start routing there automatically.

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=3" />

## Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=yua --cov-report=term-missing
```

93 unit tests across all modules. Pure logic, no API calls, no network. The full suite runs in under 200ms.

<img src="https://capsule-render.vercel.app/api?type=rect&color=gradient&customColorList=0,2,2,5,30&height=3" />

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). PRs go to `develop`, not `main`. New providers are easy to add: register a `ProviderModel` in `yua/providers/base.py` and the router, scorer, and budget tracker all pick it up automatically.

<br/>

<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=20,11,6&height=120&section=footer" />
</p>