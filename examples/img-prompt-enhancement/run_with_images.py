"""
Luminth Logo — Full Visual Image Optimization Loop
====================================================

This script runs the COMPLETE image optimization pipeline:
  1. Takes a starting image generation prompt
  2. Generates an actual image using Gemini
  3. AI judge (GPT-4o) visually evaluates the generated image
  4. Improves the prompt based on visual feedback
  5. Re-generates and re-evaluates for 5 iterations
  6. Saves everything to the database AND disk so the UI can display it

This demonstrates the full roadmap use case: generate → judge → improve → repeat.

Usage:
    cd examples/img-prompt-enhancement
    uv run python run_with_images.py
"""

from __future__ import annotations

import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Path setup
# ---------------------------------------------------------------------------
EXAMPLE_DIR = Path(__file__).parent
PROJECT_ROOT = EXAMPLE_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))
os.chdir(PROJECT_ROOT)

from asset_optimizer import Engine, load_evaluation  # noqa: E402
from asset_optimizer.providers.factory import (  # noqa: E402
    create_image_provider,
    create_text_provider,
)
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
# Configuration
# ---------------------------------------------------------------------------
STARTING_PROMPT = "Create a stylistic logo for luminth"
MAX_ITERATIONS = 5
EVALUATION_FILE = EXAMPLE_DIR / "evaluation.yaml"
IMAGE_VISUAL_EVAL = PROJECT_ROOT / "evaluations" / "image-visual.yaml"
DB_PATH = PROJECT_ROOT / "data" / "optimizer.db"
IMAGES_DIR = PROJECT_ROOT / "data" / "images"


async def main() -> None:
    print("=" * 70)
    print("  Luminth Logo — Full Visual Image Optimization")
    print("  generate -> judge -> improve -> repeat")
    print("=" * 70)
    print()

    # ------------------------------------------------------------------
    # 1. Set up providers
    #    - Text provider (OpenAI GPT-4o): improves prompts + judges images
    #    - Image provider (Gemini): generates images
    # ------------------------------------------------------------------
    print("Setting up providers...")
    text_provider = create_text_provider(name="openai", model="gpt-4o")
    image_provider = create_image_provider(name="openai_image")
    print("  Text/Judge: OpenAI gpt-4o")
    print("  Image gen:  OpenAI DALL-E 3")
    print()

    # ------------------------------------------------------------------
    # 2. Load evaluation with visual criteria
    #    Uses image-visual.yaml which has requires_image=true criteria
    #    that trigger multimodal judging of the generated image
    # ------------------------------------------------------------------
    evaluation = load_evaluation(IMAGE_VISUAL_EVAL)
    print(f"Evaluation: {evaluation.name}")
    for c in evaluation.criteria:
        tag = " [visual]" if c.requires_image else " [text]"
        print(f"  - {c.name}{tag}")
    print()

    # ------------------------------------------------------------------
    # 3. Set up database and image storage
    # ------------------------------------------------------------------
    db_engine = create_engine_from_config("sqlite", sqlite_path=DB_PATH)
    session_factory = get_session_factory(db_engine)
    async with db_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    image_storage = ImageStorage(IMAGES_DIR)

    # ------------------------------------------------------------------
    # 4. Create experiment and evaluation records in the database
    # ------------------------------------------------------------------
    async with session_factory() as session:
        repo = Repository(session)

        # Save evaluation to DB
        db_eval = Evaluation(
            name=f"{evaluation.name}-{datetime.now(timezone.utc).strftime('%H%M%S')}",
            asset_type=evaluation.asset_type,
            criteria=[
                {
                    "name": c.name,
                    "description": c.description,
                    "max_score": c.max_score,
                    "rubric": c.rubric,
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

        # Save experiment to DB
        experiment = Experiment(
            name="Luminth Logo — Visual Optimization",
            description=(
                "Full visual loop: generate logo with Gemini, "
                "judge with GPT-4o vision, improve prompt, repeat 5x."
            ),
            asset_type="image",
            evaluation_id=db_eval.id,
            provider_config={
                "text": "openai/gpt-4o",
                "image": "gemini/gemini-2.0-flash-preview-image-generation",
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
        print(f"Starting prompt: \"{STARTING_PROMPT}\"")
        print()

    # ------------------------------------------------------------------
    # 5. Run the optimization engine with image generation
    # ------------------------------------------------------------------
    engine = Engine(
        provider=text_provider,
        judge_provider=text_provider,
        image_provider=image_provider,
    )

    iteration_data: list[dict] = []

    def on_iteration(info: dict) -> None:
        status = "ACCEPTED" if info["accepted"] else "rejected"
        print(f"  Iteration {info['iteration']}: "
              f"score={info['score']:.2f}  [{status}]")

    print("Running visual optimization loop...")
    print("-" * 70)

    result = await engine.optimize(
        content=STARTING_PROMPT,
        evaluation=evaluation,
        max_iterations=MAX_ITERATIONS,
        convergence_strategy="budget",
        on_iteration=on_iteration,
    )

    print("-" * 70)
    print()

    if result.stopped_early:
        print(f"  Stopped early: {result.stop_reason}")
        print()

    # ------------------------------------------------------------------
    # 6. Save all iteration results to the database + images to disk
    # ------------------------------------------------------------------
    print("Saving results to database and disk...")

    async with session_factory() as session:
        repo = Repository(session)

        for iter_result in result.iterations:
            # Determine iteration status
            if iter_result.accepted:
                it_status = IterationStatus.IMPROVED
            else:
                it_status = IterationStatus.NO_IMPROVEMENT

            # Save iteration record
            db_iteration = Iteration(
                experiment_id=exp_id,
                number=iter_result.iteration,
                status=it_status,
                strategy_used="budget",
                improvement_prompt=iter_result.improvement_prompt,
                feedback=None,
                duration_ms=int(iter_result.duration_ms),
            )
            db_iteration = await repo.create_iteration(db_iteration)

            # Save input asset version
            await repo.create_asset_version(AssetVersion(
                iteration_id=db_iteration.id,
                role=AssetVersionRole.INPUT,
                content=iter_result.input_content,
                metadata_={"type": "prompt"},
            ))

            # Save output asset version
            output_meta: dict = {"type": "prompt"}

            # Save generated image to disk if present
            if iter_result.image_data:
                img_path = image_storage.save(
                    experiment_id=exp_id,
                    iteration_number=iter_result.iteration,
                    image_data=iter_result.image_data,
                    image_format=iter_result.image_format or "png",
                )
                output_meta["image_path"] = str(img_path)
                output_meta["image_format"] = iter_result.image_format
                output_meta["image_size_bytes"] = len(iter_result.image_data)
                print(f"  Saved image: {img_path.name} "
                      f"({len(iter_result.image_data):,} bytes)")

            await repo.create_asset_version(AssetVersion(
                iteration_id=db_iteration.id,
                role=AssetVersionRole.OUTPUT,
                content=iter_result.output_content,
                file_path=output_meta.get("image_path"),
                metadata_=output_meta,
            ))

            # Save scores
            for score_result in iter_result.scores:
                await repo.create_score(Score(
                    iteration_id=db_iteration.id,
                    criterion_name=score_result.criterion,
                    value=score_result.value,
                    max_value=score_result.max_value,
                    scorer_type=ScorerType.AI_JUDGE,
                    details=score_result.details,
                ))

        # Update experiment status and best score
        await repo.update_experiment_status(exp_id, ExperimentStatus.COMPLETED)
        await repo.update_experiment_best_score(exp_id, result.best_score)

    # Save best image separately
    if result.best_image:
        best_path = image_storage.save(
            experiment_id=exp_id,
            iteration_number=999,  # special "best" marker
            image_data=result.best_image,
            image_format=result.best_image_format or "png",
        )
        print(f"  Best image: {best_path}")

    print()

    # ------------------------------------------------------------------
    # 7. Print summary
    # ------------------------------------------------------------------
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print()
    print(f"  Initial score:    {result.initial_score:.2f}")
    print(f"  Final score:      {result.best_score:.2f}")
    print(f"  Improvement:      +{result.best_score - result.initial_score:.2f}")
    print(f"  Iterations:       {result.total_iterations}")
    if result.total_cost is not None:
        print(f"  Estimated cost:   ${result.total_cost:.4f}")
    print()
    print("  Final optimized prompt:")
    print()
    for line in result.best_content.splitlines():
        print(f"    {line}")
    print()
    print(f"  Experiment ID: {exp_id}")
    print(f"  Images saved to: {IMAGES_DIR / str(exp_id)}")
    print()
    print("  View in UI: http://localhost:5173/experiments/" + str(exp_id))
    print()

    await db_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
