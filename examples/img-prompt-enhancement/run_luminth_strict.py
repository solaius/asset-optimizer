"""
Luminth Hero — Strict Visual Optimization with Full Brand Context
=================================================================

Runs the image optimization loop with:
  - Full Luminth brand context injected into improvement prompts
  - Strict evaluation criteria (7+ means genuinely production-ready)
  - Gemini 2.5 Flash for image generation
  - GPT-4o for tough judging

Usage:
    cd examples/img-prompt-enhancement
    uv run python run_luminth_strict.py
"""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

EXAMPLE_DIR = Path(__file__).parent
PROJECT_ROOT = EXAMPLE_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
os.chdir(PROJECT_ROOT)

from asset_optimizer.core.convergence import create_strategy  # noqa: E402
from asset_optimizer.core.evaluation import load_evaluation  # noqa: E402
from asset_optimizer.providers.base import Criterion, Message  # noqa: E402
from asset_optimizer.providers.factory import (  # noqa: E402
    _load_dotenv,
    create_text_provider,
)
from asset_optimizer.providers.image_providers.gemini_image import (  # noqa: E402
    GeminiImageProvider,
)
from asset_optimizer.scoring.ai_judge import AIJudgeScorer  # noqa: E402
from asset_optimizer.storage.database import (  # noqa: E402
    create_engine_from_config,
    get_session_factory,
)
from asset_optimizer.storage.image_storage import ImageStorage  # noqa: E402
from asset_optimizer.storage.models import (  # noqa: E402
    AssetVersion,
    AssetVersionRole,
    Base,
    Evaluation,
    Experiment,
    ExperimentStatus,
    Iteration,
    IterationStatus,
    Score,
    ScorerType,
)
from asset_optimizer.storage.repository import Repository  # noqa: E402

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
STARTING_PROMPT = "Create a stylistic logo for luminth"
MAX_ITERATIONS = 5
EVAL_FILE = PROJECT_ROOT / "evaluations" / "luminth-hero-strict.yaml"
CONTEXT_FILE = EXAMPLE_DIR / "luminth-context.md"
DB_PATH = PROJECT_ROOT / "data" / "optimizer.db"
IMAGES_DIR = PROJECT_ROOT / "data" / "images"

# Load brand context once
BRAND_CONTEXT = CONTEXT_FILE.read_text(encoding="utf-8")

# ---------------------------------------------------------------------------
# Custom improvement prompt that includes Luminth brand context
# ---------------------------------------------------------------------------
IMPROVE_SYSTEM = """You are an expert image prompt engineer specializing in
brand-aligned visual design for SaaS landing pages. You are working on the
hero image for luminth.ai.

BRAND CONTEXT:
{context}

Your job: rewrite the image generation prompt to score higher on the weak
criteria listed below. Be SPECIFIC — name exact visual elements, colors
(teal #0D9488, gold #D4A843, brown-black #1A1208), textures (parchment,
aged paper, metallic circuitry), lighting direction, and composition.

Return ONLY the improved image generation prompt. No explanation."""


def build_improvement_prompt(
    content: str,
    scores: list,
    criteria: list,
) -> str:
    """Build an improvement prompt with full Luminth brand context."""
    sorted_scores = sorted(scores, key=lambda s: s.value)
    weakest = sorted_scores[:3]  # Target 3 weakest for tougher standards

    focus_parts = []
    visual_feedback_parts = []
    criterion_map = {c.name: c for c in criteria}

    for s in weakest:
        crit = criterion_map.get(s.criterion)
        if crit:
            rubric = f" Rubric: {crit.rubric}" if crit.rubric else ""
            focus_parts.append(
                f"- {crit.name}: scored {s.value:.1f}/{crit.max_score:.1f}"
                f" -- {crit.description}.{rubric}"
            )
            if crit.requires_image and s.details.get("reasoning"):
                visual_feedback_parts.append(
                    f"- {crit.name}: {s.details['reasoning']}"
                )

    prompt = (
        IMPROVE_SYSTEM.format(context=BRAND_CONTEXT)
        + f"\n\nCURRENT PROMPT:\n{content}\n\n"
        + f"WEAK CRITERIA:\n" + "\n".join(focus_parts) + "\n\n"
    )

    if visual_feedback_parts:
        prompt += (
            "VISUAL FEEDBACK (what the judge SAW in the generated image):\n"
            + "\n".join(visual_feedback_parts) + "\n\n"
        )

    prompt += "Write the improved image generation prompt now:"
    return prompt


async def main() -> None:
    print("=" * 70)
    print("  Luminth Hero -- Strict Evaluation with Brand Context")
    print("  Gemini 2.5 Flash Image + GPT-4o Strict Judging")
    print("=" * 70)
    print()

    # --- Providers ---
    _load_dotenv()
    text_provider = create_text_provider(name="openai", model="gpt-4o")
    image_provider = GeminiImageProvider(
        api_key=os.environ["GEMINI_API_KEY"],
        model="gemini-2.5-flash-image",
    )
    print("  Text/Judge: OpenAI gpt-4o (strict mode)")
    print("  Image gen:  Gemini 2.5 Flash Image")
    print()

    # --- Evaluation ---
    evaluation = load_evaluation(EVAL_FILE)
    print(f"Evaluation: {evaluation.name}")
    for c in evaluation.criteria:
        tag = " [VISUAL]" if c.requires_image else " [text]"
        print(f"  - {c.name}{tag}")
    print()

    # --- Database ---
    db_engine = create_engine_from_config("sqlite", sqlite_path=DB_PATH)
    session_factory = get_session_factory(db_engine)
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    image_storage = ImageStorage(IMAGES_DIR)

    # --- Create DB records ---
    async with session_factory() as session:
        repo = Repository(session)

        db_eval = Evaluation(
            name=f"luminth-strict-{datetime.now(timezone.utc).strftime('%H%M%S')}",
            asset_type=evaluation.asset_type,
            criteria=[
                {
                    "name": c.name, "description": c.description,
                    "max_score": c.max_score, "rubric": c.rubric,
                    "requires_image": c.requires_image,
                }
                for c in evaluation.criteria
            ],
            scorer_config={
                "type": evaluation.scorer_config.type,
                "heuristic_weight": evaluation.scorer_config.heuristic_weight,
                "ai_judge_weight": evaluation.scorer_config.ai_judge_weight,
            },
        )
        db_eval = await repo.create_evaluation(db_eval)

        experiment = Experiment(
            name="Luminth Hero -- Strict + Brand Context",
            description=(
                "Strict evaluation with full Luminth brand context. "
                "Gemini 2.5 Flash Image generation, GPT-4o strict judging. "
                "7+ means genuinely production-ready."
            ),
            asset_type="image",
            evaluation_id=db_eval.id,
            provider_config={
                "text": "openai/gpt-4o",
                "image": "gemini/gemini-2.5-flash-image",
                "mode": "strict",
            },
            config={
                "max_iterations": MAX_ITERATIONS,
                "convergence_strategy": "budget",
                "starting_prompt": STARTING_PROMPT,
            },
            status=ExperimentStatus.RUNNING,
        )
        experiment = await repo.create_experiment(experiment)
        exp_id = experiment.id
        print(f"Experiment ID: {exp_id}")
        print(f"Starting: \"{STARTING_PROMPT}\"")
        print()

    # --- Build scorer ---
    criteria = [
        Criterion(
            name=c.name, description=c.description,
            max_score=c.max_score, rubric=c.rubric,
            requires_image=c.requires_image,
        )
        for c in evaluation.criteria
    ]
    scorer = AIJudgeScorer(provider=text_provider, criteria=criteria)

    # --- Generate baseline image ---
    print("Generating baseline image...")
    baseline_gen = await image_provider.generate(STARTING_PROMPT)
    baseline_image = baseline_gen.image_data
    baseline_format = baseline_gen.format
    print(f"  Baseline image: {len(baseline_image):,} bytes")

    # --- Score baseline ---
    print("Scoring baseline (strict)...")
    baseline_scores = await scorer.score(
        STARTING_PROMPT, image=baseline_image, image_format=baseline_format
    )
    baseline_score = sum(s.value for s in baseline_scores) / len(baseline_scores)
    print(f"  Baseline score: {baseline_score:.2f}")
    for s in baseline_scores:
        print(f"    {s.criterion:<25} {s.value:>5.1f}/10")
    print()

    # --- Run optimization loop ---
    print("Running strict optimization loop...")
    print("-" * 70)

    best_content = STARTING_PROMPT
    best_score = baseline_score
    best_image = baseline_image
    best_image_format = baseline_format
    current_scores = baseline_scores
    iterations_data = []

    for iteration in range(1, MAX_ITERATIONS + 1):
        import time
        t_start = time.monotonic()

        # Build context-rich improvement prompt
        improvement_prompt = build_improvement_prompt(
            best_content, current_scores, evaluation.criteria
        )

        # Get improved prompt
        messages = [Message(role="user", content=improvement_prompt)]
        new_content = await text_provider.complete(messages)

        # Generate image
        try:
            gen_result = await image_provider.generate(new_content)
            new_image = gen_result.image_data
            new_format = gen_result.format
        except Exception as e:
            print(f"  Iteration {iteration}: IMAGE GENERATION FAILED - {e}")
            continue

        # Score with strict judge
        new_scores = await scorer.score(
            new_content, image=new_image, image_format=new_format
        )
        new_score = sum(s.value for s in new_scores) / len(new_scores)

        accepted = new_score > best_score
        if accepted:
            best_content = new_content
            best_score = new_score
            best_image = new_image
            best_image_format = new_format
            current_scores = new_scores

        duration_ms = int((time.monotonic() - t_start) * 1000)
        status_str = "ACCEPTED" if accepted else "rejected"
        print(f"  Iteration {iteration}: score={new_score:.2f}  [{status_str}]")
        for s in new_scores:
            print(f"    {s.criterion:<25} {s.value:>5.1f}/10  "
                  f"{'  ' + s.details.get('reasoning', '')[:60] if s.details.get('reasoning') and s.details['reasoning'] != 'parse error' else ''}")

        iterations_data.append({
            "iteration": iteration,
            "content": new_content,
            "score": new_score,
            "scores": new_scores,
            "accepted": accepted,
            "image_data": new_image,
            "image_format": new_format,
            "improvement_prompt": improvement_prompt,
            "duration_ms": duration_ms,
            "input_content": best_content if not accepted else iterations_data[-1]["content"] if iterations_data else STARTING_PROMPT,
        })
        print()

    print("-" * 70)
    print()

    # --- Save to DB ---
    print("Saving results to database...")

    async with session_factory() as session:
        repo = Repository(session)

        for it_data in iterations_data:
            it_status = (
                IterationStatus.IMPROVED if it_data["accepted"]
                else IterationStatus.NO_IMPROVEMENT
            )
            db_it = Iteration(
                experiment_id=exp_id,
                number=it_data["iteration"],
                status=it_status,
                strategy_used="budget",
                improvement_prompt=it_data["improvement_prompt"][:2000],
                duration_ms=it_data["duration_ms"],
            )
            db_it = await repo.create_iteration(db_it)

            await repo.create_asset_version(AssetVersion(
                iteration_id=db_it.id,
                role=AssetVersionRole.INPUT,
                content=it_data.get("input_content", STARTING_PROMPT),
                metadata_={"type": "prompt"},
            ))

            output_meta: dict = {"type": "prompt"}
            if it_data["image_data"]:
                img_path = image_storage.save(
                    experiment_id=exp_id,
                    iteration_number=it_data["iteration"],
                    image_data=it_data["image_data"],
                    image_format=it_data["image_format"] or "png",
                )
                output_meta["image_path"] = str(img_path)
                output_meta["image_format"] = it_data["image_format"]
                output_meta["image_size_bytes"] = len(it_data["image_data"])
                print(f"  Saved: {img_path.name} ({len(it_data['image_data']):,} bytes)")

            await repo.create_asset_version(AssetVersion(
                iteration_id=db_it.id,
                role=AssetVersionRole.OUTPUT,
                content=it_data["content"],
                file_path=output_meta.get("image_path"),
                metadata_=output_meta,
            ))

            for s in it_data["scores"]:
                await repo.create_score(Score(
                    iteration_id=db_it.id,
                    criterion_name=s.criterion,
                    value=s.value,
                    max_value=s.max_value,
                    scorer_type=ScorerType.AI_JUDGE,
                    details=s.details,
                ))

        await repo.update_experiment_status(exp_id, ExperimentStatus.COMPLETED)
        await repo.update_experiment_best_score(exp_id, best_score)

    if best_image:
        best_path = image_storage.save(
            experiment_id=exp_id, iteration_number=999,
            image_data=best_image, image_format=best_image_format or "png",
        )
        print(f"  Best: {best_path}")

    print()
    print("=" * 70)
    print("RESULTS (STRICT EVALUATION)")
    print("=" * 70)
    print()
    print(f"  Baseline score:   {baseline_score:.2f}")
    print(f"  Final score:      {best_score:.2f}")
    print(f"  Improvement:      +{best_score - baseline_score:.2f}")
    print(f"  Iterations:       {MAX_ITERATIONS}")
    print()
    print("  Final prompt:")
    print()
    for line in best_content.splitlines():
        print(f"    {line}")
    print()
    print(f"  View: http://localhost:5173/experiments/{exp_id}")
    print()

    await db_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
