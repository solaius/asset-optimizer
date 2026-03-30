# Product Roadmap

## Status

### DONE — Visual Image Optimization Loop

The full visual optimization loop has been implemented:

- `Engine` accepts an optional `image_provider` parameter
- When set, the engine generates an image each iteration using the image provider
- Generated images are passed to the multimodal AI judge alongside the prompt text
- `TextProvider.judge()` accepts an optional `image: bytes` parameter; OpenAI,
  Anthropic, and Gemini providers all support multimodal judging
- `CriterionConfig` has `requires_image: bool = False`; visual criteria are skipped
  in text-only runs
- `OptimizationResult` carries `best_image`, `best_image_format`, `total_cost`,
  `stopped_early`, and `stop_reason`
- `IterationResult` carries `image_data`, `image_format`, and `image_cost`
- `GeminiImageProvider` implemented using the `google-genai` SDK
- `ImageStorage` class saves generated images to disk by experiment and iteration

### DONE — Provider Factory

- `create_text_provider()`, `create_judge_provider()`, `create_image_provider()`,
  and `create_engine()` in `asset_optimizer.providers.factory`
- All four are exported from the top-level `asset_optimizer` package
- Auto-wired from `.env` + YAML config — no manual provider construction needed

### DONE — API Extensions

- `GET /api/v1/experiments/{id}/iterations` returns iterations with scores and
  asset versions
- `GET /api/v1/assets/{id}/image` serves generated images as binary responses

### DONE — UI Improvements

- Score progression charts on experiment detail page
- Iteration cards with generated images
- Score bars with per-criterion reasoning
- Clickable evaluations showing criteria and rubrics

### DONE — Built-in Evaluations

- `evaluations/prompt-clarity.yaml` — text prompt quality
- `evaluations/image-visual.yaml` — mixed text + visual criteria
- `evaluations/luminth-hero-strict.yaml` — strict visual evaluation

### DONE — Examples

- `examples/img-prompt-enhancement/` — runnable scripts for image prompt optimization

---

## Future Work

### Run experiments from UI

Allow users to trigger and monitor optimization runs directly from the web UI
without writing any Python code. Requires a run/start button on the experiment
detail page and real-time status updates.

### WebSocket real-time updates

Replace polling with WebSocket push notifications so the UI reflects iteration
progress live without page refreshes. The server already has `websockets` in scope;
needs a `/ws/experiments/{id}` endpoint and client-side event handling.

### Gemini text provider migration to google-genai

The `GeminiProvider` text provider should be migrated from `google-generativeai`
to `google-genai` (already done for `GeminiImageProvider`). This ensures a single
SDK dependency and access to newer Gemini models.

### Cost warnings and budget caps

Warn users before starting a visual optimization run about projected cost. Add a
`max_cost` parameter to `engine.optimize()` that stops the loop when the cumulative
API cost exceeds the cap (sets `stopped_early=True`, `stop_reason="budget_cap"`).

### Evaluation builder in UI

A guided form in the web UI for creating evaluation YAML files without editing files
manually. Should support adding criteria, writing rubrics, and previewing the
generated YAML.

### Prompt diff view

Per-iteration side-by-side diff of the prompt content so users can see exactly what
changed between accepted iterations.

### Batch experiment runner

CLI command to run all YAML experiment definitions in a directory and write a
summary report (e.g. `asset-optimizer batch experiments/ --report report.md`).

### PostgreSQL migration guide

Documented steps and an example `asset-optimizer.yaml` for migrating from the
default SQLite backend to PostgreSQL for production deployments.
