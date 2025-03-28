# Contributing to YuaLLM

Thanks for your interest in contributing. This guide covers everything you need to get up and running.

## Development Setup

```bash
git clone https://github.com/yuallm-dev/YuaLLM.git
cd YuaLLM
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest tests/ -v
pytest tests/ -v --cov=yua --cov-report=term-missing
```

All tests must pass before submitting a PR. Do not add tests that make real API calls.

## Code Style

We use [ruff](https://docs.astral.sh/ruff/) for linting:

```bash
ruff check yua/ tests/
ruff format yua/ tests/
```

Line length: 100. Follow PEP 8 conventions.

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(router): add max_latency_ms config option
fix(scorer): handle empty content edge case
docs: update router architecture section
chore: bump ruff to 0.5
```

## Pull Request Process

1. Fork the repo and create a feature branch from `develop`
2. Add or update tests for your changes
3. Ensure `pytest` and `ruff check` pass
4. Open a PR against `develop`, not `main`
5. Fill in the PR template — describe what changed and why

## Adding a New Provider

1. Add a `ProviderName` value to `yua/providers/base.py`
2. Register models in the `KNOWN_MODELS` list with accurate pricing
3. Update `LLMRouter._score_model()` if the provider needs routing hints
4. Add tests in `tests/test_providers.py` and `tests/test_router.py`

## Project Structure

```
yua/
  providers/    # Provider registry, model metadata, LLMResponse
  router/       # LLMRouter — task detection, cost scoring, routing
  scorer/       # QualityScorer — response quality evaluation
  budget/       # CostCalculator — token cost tracking
  analytics/    # Leaderboard — provider performance stats
  alerts/       # YuaNotifier — alert dispatch system
  cli.py        # yua CLI entry point
tests/          # Pytest unit tests — pure logic only
docs/           # Architecture and reference docs
```

## Questions

Open a GitHub issue or start a discussion. We're happy to help.