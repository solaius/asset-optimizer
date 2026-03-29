"""
Luminth Landing Page Hero — Image Prompt Optimization
=====================================================

This script demonstrates the Asset Optimizer's autoimprove loop by
iteratively improving an image generation prompt for the Luminth.ai
landing page hero image.

What it does:
  1. Loads a deliberately simple starting prompt (starting-prompt.txt)
  2. Loads Luminth-specific evaluation criteria (evaluation.yaml)
  3. Runs 5 optimization iterations using the configured text provider
  4. At each iteration, an AI judge scores the prompt against 5 criteria:
     - Subject clarity: Are visual elements specifically described?
     - Brand fidelity: Does it encode Luminth's dark/teal/gold aesthetic?
     - Genre versatility: Does it show multiple genres coexisting?
     - Composition direction: Is it art-directed for a website hero banner?
     - Generation effectiveness: Is it well-structured for image models?
  5. The engine improves the prompt targeting the weakest criteria
  6. Saves every iteration's prompt and scores to results/

What it does NOT do (yet — see docs/product_roadmap.md):
  - It does NOT generate actual images during optimization
  - It does NOT visually evaluate generated images
  - It optimizes the PROMPT TEXT only, using text-based AI judging

Usage:
  cd examples/img-prompt-enhancement
  uv run python run_optimization.py

Prerequisites:
  - API key configured in .env (OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY)
  - Run from the project root or this directory
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Resolve paths — works whether run from project root or example directory
# ---------------------------------------------------------------------------
EXAMPLE_DIR = Path(__file__).parent
PROJECT_ROOT = EXAMPLE_DIR.parent.parent

# Add project src to path so we can import asset_optimizer
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from asset_optimizer import Engine, load_evaluation  # noqa: E402
from asset_optimizer.providers.base import Criterion  # noqa: E402
from asset_optimizer.providers.factory import create_text_provider  # noqa: E402
from asset_optimizer.scoring.ai_judge import AIJudgeScorer  # noqa: E402

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
MAX_ITERATIONS = 5
CONVERGENCE_STRATEGY = "budget"  # Run exactly 5 iterations, keep the best
RESULTS_DIR = EXAMPLE_DIR / "results"
STARTING_PROMPT_FILE = EXAMPLE_DIR / "starting-prompt.txt"
EVALUATION_FILE = EXAMPLE_DIR / "evaluation.yaml"


def save_iteration(
    iteration: int,
    content: str,
    score: float,
    scores_detail: list[dict[str, object]],
    accepted: bool,
) -> None:
    """Save one iteration's results to a JSON file for later review."""
    RESULTS_DIR.mkdir(exist_ok=True)
    result = {
        "iteration": iteration,
        "score": score,
        "accepted": accepted,
        "scores": scores_detail,
        "prompt": content,
    }
    path = RESULTS_DIR / f"iteration-{iteration:02d}.json"
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")


def print_header() -> None:
    """Print a banner so the output is easy to read."""
    print("=" * 70)
    print("  Luminth Landing Page Hero — Image Prompt Optimization")
    print("  Asset Optimizer autoimprove example")
    print("=" * 70)
    print()


def print_scores(scores_detail: list[dict[str, object]]) -> None:
    """Pretty-print per-criterion scores."""
    for s in scores_detail:
        name = s["criterion"]
        value = s["value"]
        print(f"    {name:<28} {value:>5.1f} / 10.0")


async def main() -> None:
    print_header()

    # ------------------------------------------------------------------
    # 1. Load the starting prompt
    # ------------------------------------------------------------------
    starting_prompt = STARTING_PROMPT_FILE.read_text(encoding="utf-8").strip()
    print(f"Starting prompt ({len(starting_prompt)} chars):")
    print(f"  \"{starting_prompt}\"")
    print()

    # ------------------------------------------------------------------
    # 2. Load the evaluation criteria
    # ------------------------------------------------------------------
    evaluation = load_evaluation(EVALUATION_FILE)
    print(f"Evaluation: {evaluation.name}")
    print(f"  Criteria: {', '.join(c.name for c in evaluation.criteria)}")
    print()

    # ------------------------------------------------------------------
    # 3. Create the text provider from .env / config
    #    The factory reads AO_DEFAULT_TEXT_PROVIDER and the matching API key
    #    from .env automatically. No hardcoded keys needed.
    # ------------------------------------------------------------------

    # Change to project root so .env is found
    import os
    os.chdir(PROJECT_ROOT)

    provider = create_text_provider()
    print(f"Provider: {type(provider).__name__}")
    print(f"Max iterations: {MAX_ITERATIONS}")
    print(f"Strategy: {CONVERGENCE_STRATEGY}")
    print()

    # ------------------------------------------------------------------
    # 4. Score the baseline BEFORE optimization
    #    This gives us the full per-criterion review of the starting
    #    prompt, saved as iteration-00.json so every score is traceable.
    # ------------------------------------------------------------------
    criteria = [
        Criterion(
            name=c.name,
            description=c.description,
            max_score=c.max_score,
            rubric=c.rubric,
        )
        for c in evaluation.criteria
    ]
    scorer = AIJudgeScorer(provider=provider, criteria=criteria)
    baseline_scores = await scorer.score(starting_prompt)
    baseline_score = sum(s.value for s in baseline_scores) / len(baseline_scores)

    # Save baseline review as iteration-00
    baseline_detail = [
        {
            "criterion": s.criterion,
            "value": s.value,
            "max_value": s.max_value,
            "reasoning": s.details.get("reasoning", ""),
        }
        for s in baseline_scores
    ]
    save_iteration(
        iteration=0,
        content=starting_prompt,
        score=baseline_score,
        scores_detail=baseline_detail,
        accepted=True,
    )

    print(f"  Baseline score: {baseline_score:.2f}")
    print_scores(baseline_detail)
    print()

    # ------------------------------------------------------------------
    # 5. Create the engine and run the optimization loop
    # ------------------------------------------------------------------
    engine = Engine(provider=provider, judge_provider=provider)

    # Track all iterations for the summary report
    all_scores: list[list[dict[str, object]]] = [baseline_detail]

    def on_iteration(info: dict[str, object]) -> None:
        """Callback fired after each iteration — prints progress."""
        iteration = info["iteration"]
        score = info["score"]
        accepted = info["accepted"]
        status = "ACCEPTED" if accepted else "rejected"

        print(f"  Iteration {iteration}: score={score:.2f}  [{status}]")

    print("Running optimization...")
    print("-" * 70)

    result = await engine.optimize(
        content=starting_prompt,
        evaluation=evaluation,
        max_iterations=MAX_ITERATIONS,
        convergence_strategy=CONVERGENCE_STRATEGY,
        on_iteration=on_iteration,
    )

    print("-" * 70)
    print()

    # ------------------------------------------------------------------
    # 6. Save results for each iteration (1-N; baseline was iteration 0)
    # ------------------------------------------------------------------
    for iter_result in result.iterations:
        scores_detail = [
            {
                "criterion": s.criterion,
                "value": s.value,
                "max_value": s.max_value,
                "reasoning": s.details.get("reasoning", ""),
            }
            for s in iter_result.scores
        ]
        all_scores.append(scores_detail)
        save_iteration(
            iteration=iter_result.iteration,
            content=iter_result.output_content,
            score=iter_result.output_score,
            scores_detail=scores_detail,
            accepted=iter_result.accepted,
        )

    # ------------------------------------------------------------------
    # 7. Save the final optimized prompt
    # ------------------------------------------------------------------
    final_path = RESULTS_DIR / "final-prompt.txt"
    final_path.write_text(result.best_content, encoding="utf-8")

    # ------------------------------------------------------------------
    # 8. Save a summary report
    # ------------------------------------------------------------------
    summary = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "starting_prompt": starting_prompt,
        "final_prompt": result.best_content,
        "initial_score": result.initial_score,
        "final_score": result.best_score,
        "total_iterations": result.total_iterations,
        "improvement": round(result.best_score - result.initial_score, 2),
    }
    summary_path = RESULTS_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # ------------------------------------------------------------------
    # 9. Print the final report
    # ------------------------------------------------------------------
    print("RESULTS")
    print("=" * 70)
    print()
    print(f"  Initial score:  {result.initial_score:.2f}")
    print(f"  Final score:    {result.best_score:.2f}")
    print(f"  Improvement:    +{result.best_score - result.initial_score:.2f}")
    print(f"  Iterations run: {result.total_iterations}")
    print()

    # Show per-criterion scores for the best iteration
    if all_scores:
        best_idx = max(
            range(len(result.iterations)),
            key=lambda i: result.iterations[i].output_score,
        )
        print("  Best iteration scores:")
        print_scores(all_scores[best_idx])
        print()

    print("  Final optimized prompt:")
    print()
    # Indent the prompt for readability
    for line in result.best_content.splitlines():
        print(f"    {line}")
    print()
    print(f"  Results saved to: {RESULTS_DIR.relative_to(EXAMPLE_DIR)}/")
    print()


if __name__ == "__main__":
    asyncio.run(main())
