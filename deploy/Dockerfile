# Stage 1: Build UI
FROM node:20-alpine AS ui-build
WORKDIR /app/ui
COPY ui/package.json ui/package-lock.json ./
RUN npm ci
COPY ui/ ./
RUN npm run build

# Stage 2: Python application
FROM python:3.12-slim

# Create non-root user (required by OpenShift)
RUN useradd -r -u 1001 -m optimizer

WORKDIR /app

# Install UV and dependencies
COPY pyproject.toml uv.lock ./
RUN pip install --no-cache-dir uv && uv sync --no-dev --no-editable

# Copy application code
COPY src/ src/

# Copy built UI assets
COPY --from=ui-build /app/ui/dist src/asset_optimizer/static/

# Switch to non-root user
USER 1001

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')" || exit 1

CMD ["uv", "run", "asset-optimizer", "serve", "--host", "0.0.0.0", "--port", "8000"]
