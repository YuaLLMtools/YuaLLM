# Provider Reference

YuaLLM ships with a built-in registry of seven models across four providers.

## Model Registry

| Provider | Model | Context | Input $/1k | Output $/1k | Best for |
|----------|-------|---------|-----------|------------|---------|
| Grok | `grok-2` | 131k | $0.002 | $0.010 | Reasoning, Analysis, Chat |
| Grok | `grok-2-mini` | 131k | $0.0002 | $0.0005 | Simple, Chat |
| Anthropic | `claude-sonnet-4-6` | 200k | $0.003 | $0.015 | Coding, Analysis |
| Anthropic | `claude-haiku-4-5` | 200k | $0.0008 | $0.004 | Simple, Summarization |
| OpenAI | `gpt-4o` | 128k | $0.0025 | $0.010 | Coding, Creative |
| OpenAI | `gpt-4o-mini` | 128k | $0.00015 | $0.0006 | Simple, Summarization |
| Groq | `llama-3.3-70b` | 128k | $0.00059 | $0.00079 | Chat, Reasoning |

## TaskType Enum

```python
class TaskType(Enum):
    CHAT          = "chat"
    REASONING     = "reasoning"
    CODING        = "coding"
    SUMMARIZATION = "summarization"
    CREATIVE      = "creative"
    ANALYSIS      = "analysis"
    SIMPLE        = "simple"
```

## ProviderName Enum

```python
class ProviderName(Enum):
    GROK      = "grok"
    ANTHROPIC = "anthropic"
    OPENAI    = "openai"
    GROQ      = "groq"
```

## Programmatic Queries

```python
from yua.providers.base import KNOWN_MODELS, get_model, models_for_task, ProviderName, TaskType

# Get a specific model
m = get_model(ProviderName.GROK, "grok-2")
print(m.name())         # grok/grok-2
print(m.cost_for(1000, 2000))   # USD cost for 1k input + 2k output tokens

# Models suited for a task
coding_models = models_for_task(TaskType.CODING)

# All models
for m in KNOWN_MODELS:
    print(m.name(), m.context_window)
```

## Adding a New Model

Register in `yua/providers/base.py`:

```python
ProviderModel(
    provider=ProviderName.GROQ,
    model_id="llama-3.1-8b",
    context_window=128_000,
    cost_per_1k_input=0.0001,
    cost_per_1k_output=0.0001,
    strengths=[TaskType.SIMPLE, TaskType.CHAT],
)
```

No other changes needed — the router, scorer, and calculator all read from `KNOWN_MODELS` automatically.