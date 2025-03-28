# Changelog

All notable changes to YuaLLM are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versioning follows [Semantic Versioning](https://semver.org/).

---

## [0.2.0] — 2025-03-28

### Added
- `yua.alerts.notifier` — YuaNotifier with cost overrun, quality failure, fallback, and provider error alerts
- `yua.analytics.leaderboard` — provider stats, routing stats, top models, cheapest models
- `YuaAlert.format_telegram()` — Telegram-formatted alert message
- `RoutingStats.task_distribution` — per-task-type routing breakdown
- `yua setup` CLI command — interactive API key configuration wizard
- `yua score` CLI command — score any response content from the terminal

### Changed
- `RouterConfig` now supports `force_model` override (e.g. `"anthropic/claude-haiku-4-5"`)
- Cost budget logic now falls back to cheapest available model instead of raising

### Fixed
- `QualityScorer._completeness_score` now correctly penalizes ellipsis endings

---

## [0.1.1] — 2025-03-14

### Added
- `CostCalculator.estimate_from_text()` — estimate cost from raw prompt/response strings
- `LLMRouter.route_batch()` — batch routing for multiple prompts
- `QualityScorer.best_response()` — select highest-scoring response from a list
- Groq `llama-3.3-70b` added to provider registry

### Changed
- `LLMRouter` scoring now applies complexity bonus for mini vs full models
- `ProviderStats.pass_rate` threshold lowered from 0.6 to 0.5 to align with scorer

### Fixed
- `models_for_task()` returned duplicates when a model had overlapping strengths

---

## [0.1.0] — 2025-02-20

### Added
- Initial release
- `yua.providers.base` — ProviderName, TaskType, ProviderModel, LLMResponse, KNOWN_MODELS registry
- `yua.router.llm_router` — LLMRouter with task detection, complexity estimation, cost scoring
- `yua.scorer.quality_scorer` — QualityScorer with length, completeness, refusal, alignment scoring
- `yua.budget.cost_calculator` — CostCalculator with per-model, per-provider cost tracking
- `yua route`, `yua cost` CLI commands
- 60+ unit tests covering all core modules

[0.2.0]: https://github.com/yuallm-dev/YuaLLM/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/yuallm-dev/YuaLLM/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/yuallm-dev/YuaLLM/releases/tag/v0.1.0