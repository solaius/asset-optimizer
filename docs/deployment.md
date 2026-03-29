# Deployment

## Docker

### Build the Image

```bash
docker build -t asset-optimizer:latest .
```

The Dockerfile uses a two-stage build:

1. **Stage 1** (`node:20-alpine`) — builds the React UI with `npm ci && npm run build`
2. **Stage 2** (`python:3.12-slim`) — installs Python dependencies with UV and copies
   the built UI assets into `src/asset_optimizer/static/`

The final image runs as a non-root user (`uid=1001`) for OpenShift compatibility.

### Run with Docker

```bash
docker run -d \
  --name asset-optimizer \
  -p 8000:8000 \
  -e ANTHROPIC_API_KEY=sk-ant-... \
  -e OPENAI_API_KEY=sk-... \
  -v $(pwd)/data:/app/data \
  asset-optimizer:latest
```

To use a custom config file:

```bash
docker run -d \
  --name asset-optimizer \
  -p 8000:8000 \
  -v $(pwd)/asset-optimizer.yaml:/app/asset-optimizer.yaml:ro \
  -v $(pwd)/data:/app/data \
  asset-optimizer:latest
```

### Health Check

The Dockerfile includes a built-in health check that calls
`/api/v1/health` every 30 seconds. Check container health:

```bash
docker inspect --format='{{.State.Health.Status}}' asset-optimizer
```

## Kubernetes / Helm

### Install with Helm

```bash
helm install asset-optimizer ./deploy/helm/asset-optimizer \
  --set image.tag=latest \
  --set secrets.anthropicApiKey=sk-ant-... \
  --set secrets.openaiApiKey=sk-... \
  --set storage.backend=postgres \
  --set postgresql.enabled=true
```

### Upgrade

```bash
helm upgrade asset-optimizer ./deploy/helm/asset-optimizer \
  --reuse-values \
  --set image.tag=v1.2.0
```

### Uninstall

```bash
helm uninstall asset-optimizer
```

## OpenShift

OpenShift requires images to run as non-root. The Dockerfile already creates and
switches to `uid=1001` to satisfy this requirement.

### Deploy to OpenShift

```bash
# Log in and select your project
oc login https://api.cluster.example.com:6443
oc project my-project

# Create secrets for API keys
oc create secret generic asset-optimizer-secrets \
  --from-literal=ANTHROPIC_API_KEY=sk-ant-... \
  --from-literal=OPENAI_API_KEY=sk-...

# Apply the deployment manifest
oc apply -f deploy/openshift/deployment.yaml

# Expose the service
oc expose svc/asset-optimizer
oc get route asset-optimizer
```

### OpenShift Deployment Manifest

The file `deploy/openshift/deployment.yaml` includes:

- `Deployment` with a readiness probe on `/api/v1/health/ready`
- `Service` exposing port 8000
- `ConfigMap` for non-secret configuration
- `SecretKeyRef` bindings for API key environment variables
- `SecurityContext` with `runAsNonRoot: true` and `runAsUser: 1001`

## Environment Variables

All configuration in `asset-optimizer.yaml` supports `${ENV_VAR}` interpolation.
The following variables are commonly set in container environments:

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | API key for Anthropic Claude models |
| `OPENAI_API_KEY` | API key for OpenAI models and DALL-E |
| `GEMINI_API_KEY` | API key for Google Gemini models |
| `NANO_BANANA_API_KEY` | API key for Nano Banana image generation |
| `DATABASE_URL` | PostgreSQL connection string (e.g. `postgresql+asyncpg://...`) |
| `ASSET_OPTIMIZER_HOST` | Override server bind host (default: `0.0.0.0`) |
| `ASSET_OPTIMIZER_PORT` | Override server bind port (default: `8000`) |

## PostgreSQL Configuration

For production deployments switch from SQLite to PostgreSQL:

```yaml
storage:
  backend: postgres
  postgres_url: ${DATABASE_URL}
```

The `DATABASE_URL` must use the `asyncpg` driver:

```
postgresql+asyncpg://user:password@host:5432/asset_optimizer
```

Run database migrations with Alembic before starting the server:

```bash
uv run alembic upgrade head
```

## Production Checklist

- Set all required API key environment variables
- Use PostgreSQL for the storage backend
- Mount a persistent volume at `/app/data` (if using SQLite)
- Configure resource requests and limits in Kubernetes/OpenShift
- Enable TLS termination at the ingress/route level
- Set `ASSET_OPTIMIZER_HOST=0.0.0.0` and configure your ingress to route traffic
