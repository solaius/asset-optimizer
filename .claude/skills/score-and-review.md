---
name: score-and-review
description: Systematic scoring and feedback for asset improvements
---

# Score and Review

## Process

1. **Load both versions** — Read the before (input) and after (output) asset content
2. **Load evaluation** — Read the evaluation criteria and rubrics
3. **Score each criterion** — For each criterion in the evaluation:
   - Apply the rubric to the content
   - Assign a specific score with reasoning
   - Identify the specific parts of the content that justify the score
4. **Generate actionable feedback** — For each criterion:
   - Quote the specific part that needs improvement
   - Explain what's wrong and why it matters
   - Suggest a concrete fix (not vague "make it better")
5. **Produce structured output** — Return scores and feedback in structured format

## Rules

- Never give vague feedback like "improve clarity" — say exactly what's unclear and how to fix it
- Quote specific content when pointing out issues
- Score against the rubric levels, not on gut feeling
- Compare before/after to identify what improved and what regressed
