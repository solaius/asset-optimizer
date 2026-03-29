# Image Prompt Enhancement Example

Demonstrates Asset Optimizer's autoimprove loop by iteratively improving an
image generation prompt for the **Luminth.ai** landing page hero image.

## What This Example Does

1. Starts with a deliberately vague prompt: *"A fantasy landing page hero image
   for Luminth, an AI world-building platform..."*
2. Scores it against 5 Luminth-specific criteria (subject clarity, brand
   fidelity, genre versatility, composition direction, generation effectiveness)
3. Runs 5 optimization iterations — each time the AI judge identifies the weakest
   criteria and the improver rewrites the prompt to fix them
4. Outputs the optimized prompt + per-iteration scores to `results/`

## What This Does NOT Do (Yet)

This example optimizes the **text of the prompt**, not the generated image.
The AI judge reads and scores the prompt's specificity, brand alignment, and
art direction — but it never generates or visually evaluates an actual image.

For the full visual loop (generate image → judge image → improve prompt → repeat),
see `docs/product_roadmap.md`.

## Files

| File | Purpose |
|---|---|
| `starting-prompt.txt` | The intentionally vague starting prompt |
| `evaluation.yaml` | 5 scoring criteria tailored to Luminth's brand and hero image needs |
| `context.md` | Background on Luminth's visual identity, audience, and requirements |
| `run_optimization.py` | The runner script — loads config, runs 5 iterations, saves results |
| `results/` | Output directory (created on run) with per-iteration JSON + final prompt |

## How to Run

```bash
# From the project root
cd examples/img-prompt-enhancement
uv run python run_optimization.py
```

**Prerequisites:** An API key configured in `.env` at the project root.
The script uses whichever provider is set as `AO_DEFAULT_TEXT_PROVIDER`
(defaults to OpenAI/gpt-4o).

## Understanding the Output

Each iteration produces a JSON file in `results/`:

```json
{
  "iteration": 1,
  "score": 6.4,
  "accepted": true,
  "scores": [
    {"criterion": "subject_clarity", "value": 7.0, "reasoning": "..."},
    {"criterion": "brand_fidelity", "value": 5.0, "reasoning": "..."},
    ...
  ],
  "prompt": "The improved prompt text..."
}
```

The `summary.json` shows the before/after comparison:

```json
{
  "starting_prompt": "A fantasy landing page hero image...",
  "final_prompt": "The fully optimized prompt...",
  "initial_score": 3.2,
  "final_score": 8.1,
  "improvement": 4.9
}
```

## Customizing

- **Change the starting prompt** — edit `starting-prompt.txt`
- **Adjust scoring criteria** — edit `evaluation.yaml` (add/remove criteria, change rubrics)
- **Use a different provider** — set `AO_DEFAULT_TEXT_PROVIDER=claude` in `.env`
- **Run more iterations** — change `MAX_ITERATIONS` in `run_optimization.py`
- **Change convergence** — switch from `budget` (fixed iterations) to `greedy` (stop on stagnation) or `target` (stop at score threshold)
