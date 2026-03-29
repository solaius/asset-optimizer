---
name: create-evaluation
description: Guide creation of well-structured evaluation criteria for any asset type
---

# Create Evaluation

## Process

1. **Identify the asset type** — What kind of asset will be evaluated? (prompt, skill, image, or custom)
2. **Define quality dimensions** — What aspects of quality matter? Use sequential thinking to explore dimensions.
3. **Write rubrics** — For each criterion, write concrete scoring anchors:
   - 1-3: Clearly failing (describe what this looks like)
   - 4-6: Acceptable but needs improvement (describe)
   - 7-9: Good quality (describe)
   - 10: Exceptional (describe)
4. **Configure scoring** — Set scorer type (heuristic, ai_judge, composite) and weights.
5. **Output YAML** — Write the evaluation to `evaluations/<name>.yaml`.

## Quality Checks

- Every rubric must have concrete, distinguishable levels (not just "good" vs "bad")
- Each criterion must be independently scorable
- Criteria should not overlap significantly
- The set of criteria should cover the key quality aspects for this asset type

## Template

```yaml
name: <evaluation-name>
asset_type: <prompt|skill|image|custom>
description: <what this evaluation measures>

criteria:
  - name: <criterion-name>
    description: "<what this measures>"
    max_score: 10
    rubric: |
      1-3: <failing description>
      4-6: <acceptable description>
      7-9: <good description>
      10: <exceptional description>

scorer_config:
  type: composite
  heuristic_weight: 0.2
  ai_judge_weight: 0.8
```
