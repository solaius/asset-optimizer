# API Reference

The REST API is served at `http://localhost:8000` (default). All endpoints are under
the `/api/v1` prefix. The server generates an OpenAPI schema at `/docs` (Swagger UI)
and `/redoc`.

## Endpoint Summary

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/health` | Liveness check |
| GET | `/api/v1/health/ready` | Readiness check |
| GET | `/api/v1/providers` | List available providers |
| POST | `/api/v1/evaluations` | Create an evaluation |
| GET | `/api/v1/evaluations` | List evaluations |
| GET | `/api/v1/evaluations/{id}` | Get evaluation by ID |
| DELETE | `/api/v1/evaluations/{id}` | Delete an evaluation |
| POST | `/api/v1/experiments` | Create an experiment |
| GET | `/api/v1/experiments` | List experiments |
| GET | `/api/v1/experiments/{id}` | Get experiment by ID |
| DELETE | `/api/v1/experiments/{id}` | Delete an experiment |

## Health

### GET /api/v1/health

Returns service liveness. Always returns 200 if the process is running.

**Response 200:**

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### GET /api/v1/health/ready

Returns service readiness. Use this as a Kubernetes readiness probe.

**Response 200:**

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

## Providers

### GET /api/v1/providers

Returns all registered text and image providers.

**Response 200:**

```json
{
  "text": [
    {"name": "openai", "type": "text", "description": "OpenAI GPT models"},
    {"name": "anthropic", "type": "text", "description": "Anthropic Claude models"},
    {"name": "gemini", "type": "text", "description": "Google Gemini models"},
    {"name": "openai_compat", "type": "text", "description": "OpenAI-compatible API endpoint"}
  ],
  "image": [
    {"name": "openai_image", "type": "image", "description": "OpenAI DALL-E image generation"},
    {"name": "nano_banana", "type": "image", "description": "Nano Banana image generation"}
  ]
}
```

## Evaluations

### POST /api/v1/evaluations

Create a new evaluation definition. The evaluation is stored in the database and
can be referenced by experiments.

**Request body:**

```json
{
  "name": "prompt-clarity",
  "asset_type": "prompt",
  "description": "Evaluates prompt clarity and effectiveness",
  "criteria": [
    {
      "name": "clarity",
      "description": "Is the prompt unambiguous?",
      "max_score": 10,
      "rubric": "1-3: Vague\n4-6: Mostly clear\n7-10: Crystal clear"
    }
  ],
  "scorer_config": {
    "type": "composite",
    "heuristic_weight": 0.2,
    "ai_judge_weight": 0.8
  }
}
```

**Response 201:**

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "name": "prompt-clarity",
  "asset_type": "prompt",
  "description": "Evaluates prompt clarity and effectiveness",
  "criteria": [...],
  "scorer_config": {...},
  "created_at": "2026-03-29T12:00:00Z",
  "updated_at": "2026-03-29T12:00:00Z"
}
```

### GET /api/v1/evaluations

List all evaluations. Filter by asset type with the `asset_type` query parameter.

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `asset_type` | string | Filter by asset type (e.g. `prompt`, `skill`, `image`) |

**Response 200:** Array of evaluation objects (same shape as POST response).

### GET /api/v1/evaluations/{evaluation_id}

Get a single evaluation by UUID.

**Response 404** if the evaluation does not exist:

```json
{"detail": "Evaluation not found"}
```

### DELETE /api/v1/evaluations/{evaluation_id}

Delete an evaluation. Returns 204 on success, 404 if not found.

## Experiments

### POST /api/v1/experiments

Create a new experiment. An experiment links an asset type, an evaluation, and
provider configuration. Running the experiment executes the autoimprove loop.

**Request body:**

```json
{
  "name": "improve-system-prompt",
  "description": "Optimize the customer support system prompt",
  "asset_type": "prompt",
  "evaluation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "provider_config": {
    "text": "openai",
    "model": "gpt-4o"
  },
  "config": {
    "max_iterations": 10,
    "convergence_strategy": "greedy",
    "stagnation_limit": 3
  }
}
```

**Response 201:**

```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "name": "improve-system-prompt",
  "description": "Optimize the customer support system prompt",
  "asset_type": "prompt",
  "evaluation_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "status": "pending",
  "config": {...},
  "best_score": null,
  "created_at": "2026-03-29T12:00:00Z",
  "updated_at": "2026-03-29T12:00:00Z"
}
```

### GET /api/v1/experiments

List experiments. Supports filtering by status and asset type.

**Query parameters:**

| Parameter | Type | Description |
|---|---|---|
| `exp_status` | string | Filter by status: `pending`, `running`, `completed`, `failed`, `cancelled` |
| `asset_type` | string | Filter by asset type |

### GET /api/v1/experiments/{experiment_id}

Get a single experiment by UUID. Returns 404 if not found.

### DELETE /api/v1/experiments/{experiment_id}

Delete an experiment. Returns 204 on success, 404 if not found.

## Error Responses

All errors follow FastAPI's default format:

```json
{
  "detail": "Human-readable error message"
}
```

Common HTTP status codes:

| Code | Meaning |
|---|---|
| 400 | Bad request — invalid input data |
| 404 | Resource not found |
| 422 | Unprocessable entity — request body validation failed |
| 500 | Internal server error |
