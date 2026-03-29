# Extending Asset Optimizer

Asset Optimizer is designed to be extended. You can add new asset types, text
providers, image providers, and scoring strategies without modifying the core library.

## Adding a New Asset Type

Asset types implement `AssetTypeProtocol` from `asset_optimizer.assets.base`.

### Step 1: Implement the protocol

```python
# my_project/assets/csv_type.py
from __future__ import annotations

import csv
import io
from pathlib import Path
from typing import Any

from asset_optimizer.assets.base import AssetContent


class CSVAssetType:
    """Optimizes CSV data schemas and column descriptions."""

    name: str = "csv"
    file_extensions: list[str] = [".csv"]

    def load(self, path: Path) -> AssetContent:
        raw = path.read_text(encoding="utf-8")
        reader = csv.reader(io.StringIO(raw))
        headers = next(reader, [])
        return AssetContent(
            text=raw,
            metadata={"headers": headers, "row_count": sum(1 for _ in reader)},
        )

    def save(self, content: AssetContent, path: Path) -> None:
        path.write_text(content.text or "", encoding="utf-8")

    def validate(self, content: AssetContent) -> list[str]:
        errors: list[str] = []
        try:
            reader = csv.reader(io.StringIO(content.text or ""))
            rows = list(reader)
            if not rows:
                errors.append("CSV must not be empty")
        except csv.Error as e:
            errors.append(f"Invalid CSV: {e}")
        return errors

    def default_evaluation(self) -> dict[str, Any]:
        return {
            "asset_type": "csv",
            "criteria": [
                {
                    "name": "header_clarity",
                    "description": "Are column names clear and descriptive?",
                    "max_score": 10,
                    "rubric": (
                        "1-3: Cryptic abbreviations (e.g. 'col1', 'dt')\n"
                        "4-6: Understandable but not self-explanatory\n"
                        "7-10: Clear, descriptive, snake_case names"
                    ),
                },
            ],
            "scorer_config": {"type": "composite", "heuristic_weight": 0.2, "ai_judge_weight": 0.8},
        }

    def render_for_prompt(self, content: AssetContent) -> str:
        headers = content.metadata.get("headers", [])
        return f"CSV with columns: {', '.join(headers)}\n\n```csv\n{content.text}\n```"
```

### Step 2: Register the type

```python
from asset_optimizer.assets.registry import AssetTypeRegistry
from my_project.assets.csv_type import CSVAssetType

registry = AssetTypeRegistry()
registry.register(CSVAssetType())
```

### Step 3: Use it in an evaluation

```yaml
# evaluations/csv-headers.yaml
name: csv-headers
asset_type: csv
criteria:
  - name: header_clarity
    description: Are column names clear and descriptive?
    max_score: 10
```

## Adding a New Text Provider

Text providers extend `TextProvider` from `asset_optimizer.providers.base` and
implement two async methods: `complete` and `judge`.

### Step 1: Implement the provider

```python
# my_project/providers/cohere_provider.py
from __future__ import annotations

import cohere

from asset_optimizer.providers.base import (
    Criterion,
    JudgmentResult,
    JudgmentScore,
    Message,
    TextProvider,
)


class CohereProvider(TextProvider):
    """Text provider backed by Cohere's Command models."""

    def __init__(self, api_key: str, model: str = "command-r-plus") -> None:
        self.model = model
        self._client = cohere.AsyncClient(api_key=api_key)

    async def complete(self, messages: list[Message], **kwargs: object) -> str:
        # Combine messages into a single prompt for simplicity
        prompt = "\n\n".join(f"{m.role}: {m.content}" for m in messages)
        response = await self._client.generate(
            model=self.model,
            prompt=prompt,
            max_tokens=2048,
        )
        return response.generations[0].text.strip()

    async def judge(self, content: str, criteria: list[Criterion]) -> JudgmentResult:
        import json

        criteria_text = "\n".join(
            f"- {c.name} (max {c.max_score}): {c.description}" for c in criteria
        )
        prompt = (
            f"Evaluate this content against each criterion and return JSON.\n\n"
            f"Content:\n{content}\n\n"
            f"Criteria:\n{criteria_text}\n\n"
            f'Format: {{"scores": [{{"criterion": "name", "score": 7.5, "reasoning": "..."}}]}}'
        )
        response_text = await self.complete([Message(role="user", content=prompt)])
        try:
            data = json.loads(response_text)
            scores = [
                JudgmentScore(
                    criterion=item["criterion"],
                    score=float(item["score"]),
                    reasoning=item.get("reasoning", ""),
                )
                for item in data.get("scores", [])
            ]
        except (json.JSONDecodeError, KeyError, ValueError):
            scores = [
                JudgmentScore(criterion=c.name, score=c.max_score / 2, reasoning="parse error")
                for c in criteria
            ]
        return JudgmentResult(scores=scores)
```

### Step 2: Use it with the engine

```python
from asset_optimizer import Engine
from my_project.providers.cohere_provider import CohereProvider

provider = CohereProvider(api_key="...", model="command-r-plus")
engine = Engine(provider=provider)
```

## Adding a New Image Provider

Image providers extend `ImageProvider` from
`asset_optimizer.providers.image_providers.base` and implement one async method:
`generate`.

### Step 1: Implement the provider

```python
# my_project/providers/stability_provider.py
from __future__ import annotations

import base64
import httpx
from asset_optimizer.providers.base import ImageResult
from asset_optimizer.providers.image_providers.base import ImageProvider


class StabilityProvider(ImageProvider):
    """Image provider backed by Stability AI's REST API."""

    def __init__(self, api_key: str, model: str = "stable-diffusion-xl-1024-v1-0") -> None:
        self.model = model
        self._client = httpx.AsyncClient(
            base_url="https://api.stability.ai",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=120.0,
        )

    async def generate(self, prompt: str, **kwargs: object) -> ImageResult:
        response = await self._client.post(
            f"/v1/generation/{self.model}/text-to-image",
            json={"text_prompts": [{"text": prompt}], "samples": 1},
        )
        response.raise_for_status()
        data = response.json()
        image_bytes = base64.b64decode(data["artifacts"][0]["base64"])
        return ImageResult(
            image_data=image_bytes,
            format="png",
            metadata={"model": self.model, "prompt": prompt},
        )
```

## Adding a New Scorer

Scorers extend `Scorer` from `asset_optimizer.scoring.base` and implement `score`.

### Step 1: Implement the scorer

```python
# my_project/scoring/json_validity_scorer.py
import json
from asset_optimizer.scoring.base import Scorer, ScoreResult


class JSONValidityScorer(Scorer):
    """Scores content based on whether it contains valid JSON."""

    def score(self, content: str) -> ScoreResult:
        try:
            json.loads(content)
            return ScoreResult(
                criterion="json_validity",
                value=10.0,
                scorer_type="heuristic",
                details={"valid": True},
            )
        except json.JSONDecodeError as e:
            return ScoreResult(
                criterion="json_validity",
                value=0.0,
                scorer_type="heuristic",
                details={"valid": False, "error": str(e)},
            )
```

### Step 2: Use it in a CompositeScorer

```python
from asset_optimizer.scoring.composite import CompositeScorer
from asset_optimizer.scoring.heuristic import LengthScorer
from my_project.scoring.json_validity_scorer import JSONValidityScorer

scorer = CompositeScorer(
    scorers=[
        {"scorer": JSONValidityScorer(), "weight": 0.5, "criterion": "json_validity"},
        {
            "scorer": LengthScorer(min_length=50, max_length=500),
            "weight": 0.5,
            "criterion": "length",
        },
    ]
)

results = scorer.score_all('{"key": "value"}')
aggregate = scorer.composite_score(results)
print(f"Score: {aggregate:.2f}/10")
```
