"""YuaLLM CLI — yua <command>"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def cmd_route(args: argparse.Namespace) -> None:
    from yua.router.llm_router import LLMRouter, RouterConfig
    from yua.providers.base import ProviderName
    router = LLMRouter()
    config = RouterConfig(
        prefer_cheap=args.cheap,
        prefer_fast=args.fast,
    )
    decision = router.route(args.prompt, config)
    print(f"\nYuaLLM Route — \"{args.prompt[:50]}...\"" if len(args.prompt) > 50 else f"\nYuaLLM Route")
    print(f"  Provider:   {decision.provider.value}")
    print(f"  Model:      {decision.model_id}")
    print(f"  Task type:  {decision.task_type.value}")
    print(f"  Est. cost:  ${decision.estimated_cost_usd:.6f}")
    print(f"  Reason:     {decision.reason}")
    if decision.fallback_used:
        print(f"  [fallback]")


def cmd_cost(args: argparse.Namespace) -> None:
    from yua.budget.cost_calculator import CostCalculator
    from yua.providers.base import ProviderName
    calc = CostCalculator()
    comparisons = calc.compare_models(args.input_tokens, args.output_tokens)
    print(f"\nCost Comparison — {args.input_tokens} input / {args.output_tokens} output tokens\n")
    for model, cost in comparisons:
        bar = "█" * int(cost * 10000)
        print(f"  {model:35s} ${cost:.6f}  {bar}")


def cmd_score(args: argparse.Namespace) -> None:
    from yua.scorer.quality_scorer import QualityScorer
    from yua.providers.base import LLMResponse, ProviderName, TaskType
    resp = LLMResponse(
        provider=ProviderName.GROK,
        model_id="grok-2",
        content=args.content,
        input_tokens=100,
        output_tokens=len(args.content.split()),
        latency_ms=500,
        task_type=TaskType.CHAT,
    )
    result = QualityScorer().score(resp)
    print(f"\nQuality Score")
    print(f"  Overall:      {result.overall:.0%} — {result.verdict}")
    print(f"  Length:       {result.length_score:.0%}")
    print(f"  Completeness: {result.completeness_score:.0%}")
    print(f"  Refusal-free: {result.refusal_score:.0%}")
    print(f"  Alignment:    {result.alignment_score:.0%}")


def cmd_setup(args: argparse.Namespace) -> None:
    config_dir = Path.home() / ".yuallm"
    config_dir.mkdir(exist_ok=True)
    grok = input("Grok API key (xAI): ").strip()
    anthropic = input("Anthropic API key (optional): ").strip()
    openai = input("OpenAI API key (optional): ").strip()
    (config_dir / ".env").write_text(
        f"GROK_API_KEY={grok}\nANTHROPIC_API_KEY={anthropic}\nOPENAI_API_KEY={openai}\n"
    )
    print(f"Config saved to {config_dir / '.env'}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="yua", description="YuaLLM — LLM Router & Orchestrator")
    sub = parser.add_subparsers(dest="command")

    p = sub.add_parser("route", help="Route a prompt to the best model")
    p.add_argument("prompt")
    p.add_argument("--cheap", action="store_true")
    p.add_argument("--fast", action="store_true")
    p.set_defaults(func=cmd_route)

    p = sub.add_parser("cost", help="Compare model costs")
    p.add_argument("--input-tokens", type=int, default=500, dest="input_tokens")
    p.add_argument("--output-tokens", type=int, default=1000, dest="output_tokens")
    p.set_defaults(func=cmd_cost)

    p = sub.add_parser("score", help="Score a response quality")
    p.add_argument("content")
    p.set_defaults(func=cmd_score)

    p = sub.add_parser("setup", help="Configure YuaLLM API keys")
    p.set_defaults(func=cmd_setup)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
