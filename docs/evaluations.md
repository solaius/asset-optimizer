# Evaluations

An evaluation defines what "good" looks like for a specific asset. It is a collection
of scoring criteria plus configuration for how scores are computed.

## What Evaluations Are

Every optimization run requires an evaluation. The engine:

1. Scores the current content against all criteria
2. Uses the two weakest criteria to build the improvement prompt
3. Accepts or rejects the new version based on aggregate score
4. Repeats until convergence

Without a well-designed evaluation, the engine has no definition of "better" and will
produce inconsistent results.

## Creating an Evaluation YAML File

Place evaluation files in `evaluations/` with a `.yaml` extension.

**Minimal example** (`evaluations/prompt-clarity.yaml`):

```yaml
name: prompt-clarity
asset_type: prompt
description: Evaluates prompt clarity, specificity, and effectiveness

criteria:
  - name: clarity
    description: "Is the prompt unambiguous and easy to understand?"
    max_score: 10
    rubric: |
      1-3: Vague, multiple interpretations possible
      4-6: Mostly clear but some ambiguity
      7-9: Clear and specific
      10: Crystal clear, no room for misinterpretation

  - name: specificity
    description: "Does the prompt include specific, actionable instructions?"
    max_score: 10
    rubric: |
      1-3: Generic instructions, no concrete guidance
      4-6: Some specifics but leaves gaps
      7-9: Detailed, actionable instructions
      10: Exhaustively specific with examples

  - name: effectiveness
    description: "Would this prompt reliably produce the desired output?"
    max_score: 10
    rubric: |
      1-3: Unreliable, inconsistent results expected
      4-6: Sometimes produces desired output
      7-9: Reliably produces good output
      10: Consistently produces excellent output

scorer_config:
  type: composite
  heuristic_weight: 0.2
  ai_judge_weight: 0.8
```

## Evaluation Fields

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Unique identifier for this evaluation |
| `asset_type` | Yes | One of `prompt`, `skill`, `image`, or a custom type name |
| `description` | No | Human-readable description of what this evaluation measures |
| `criteria` | Yes | List of one or more criterion objects |
| `scorer_config` | No | Scoring configuration (defaults to composite 20/80) |

### Criterion Fields

| Field | Required | Description |
|---|---|---|
| `name` | Yes | Short identifier (used in prompts and reports) |
| `description` | Yes | What this criterion measures — shown to the AI judge |
| `max_score` | No | Maximum score value (default: `10`) |
| `rubric` | No | Detailed scoring guide — significantly improves AI judge accuracy |
| `requires_image` | No | If `true`, this criterion is only scored when an image is provided (default: `false`) |

`requires_image: true` is used for visual criteria that require the AI judge to look
at a generated image (e.g. composition, color palette, style match). These criteria
are silently skipped in text-only runs and only scored when the engine's
`image_provider` is set.

## Scoring Concepts

### Heuristic Scoring

Heuristic scorers are deterministic rules applied to the content string. They are
fast, free, and reproducible. Built-in heuristic scorers:

| Scorer | What it measures |
|---|---|
| `LengthScorer` | How close the content length is to a target range |
| `StructureScorer` | Presence of required section headings or markers |
| `KeywordScorer` | Presence of required keywords |
| `ReadabilityScorer` | Flesch-Kincaid reading ease score |

Heuristic scorers run locally with no API calls, making them suitable for fast
feedback and as a sanity check layer.

### AI-Judged Scoring

The `AIJudgeScorer` sends content and criteria to a language model and asks for
per-criterion scores with reasoning. The judge returns structured JSON:

```json
{
  "scores": [
    {"criterion": "clarity", "score": 7.5, "reasoning": "The prompt is mostly clear..."},
    {"criterion": "specificity", "score": 4.0, "reasoning": "Instructions are generic..."}
  ]
}
```

AI judging is slower and incurs API costs, but captures nuanced quality dimensions
that heuristics cannot.

### Composite Scoring

`CompositeScorer` combines heuristic and AI-judge scores using configurable weights:

```yaml
scorer_config:
  type: composite
  heuristic_weight: 0.2
  ai_judge_weight: 0.8
```

The aggregate score used by the engine is the mean of all criterion scores. The
convergence decision is based on whether this aggregate improves across iterations.

## Rubric Design Tips

Good rubrics dramatically improve AI judge consistency:

1. **Use concrete examples at each level.** Vague rubrics produce inconsistent scores.
   Instead of "good vs bad", describe what a 3, 6, and 9 look like specifically.

2. **Match rubric scale to `max_score`.** If `max_score` is 10, describe levels 1-3,
   4-6, 7-9, and 10. If `max_score` is 5, describe levels 1, 2, 3, 4, and 5.

3. **Keep criteria independent.** If clarity and specificity always correlate, merge
   them. Overlapping criteria waste judge tokens and dilute the score signal.

4. **Describe the worst and best clearly.** The extremes anchor the scale for
   everything in between.

5. **Use domain language.** For prompt optimization, mention "ambiguity" and
   "instruction-following". For image prompts, mention "composition" and "style".

## Built-in Evaluation Files

The repository ships with three ready-to-use evaluations in `evaluations/`:

| File | Asset type | Purpose |
|---|---|---|
| `prompt-clarity.yaml` | `prompt` | Evaluates clarity, specificity, and effectiveness of text prompts |
| `image-visual.yaml` | `image` | Mixed text + visual criteria; includes `requires_image: true` criteria for composition, color, and style match |
| `luminth-hero-strict.yaml` | `image` | Strict visual evaluation for Luminth hero image generation with detailed rubrics |

`image-visual.yaml` uses `requires_image: true` on visual criteria so the text-only
scorer can still run when no image provider is configured.

## Loading Evaluations in Code

```python
from pathlib import Path
from asset_optimizer import load_evaluation

evaluation = load_evaluation(Path("evaluations/prompt-clarity.yaml"))

print(evaluation.name)           # "prompt-clarity"
print(evaluation.asset_type)     # "prompt"
for criterion in evaluation.criteria:
    print(criterion.name, criterion.max_score)
```

`load_evaluation` raises `FileNotFoundError` if the file does not exist and
`ValueError` if the file has no criteria.
