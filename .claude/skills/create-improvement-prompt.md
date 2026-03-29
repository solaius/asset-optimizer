---
name: create-improvement-prompt
description: Create high-quality prompts that drive the autoimprove loop
---

# Create Improvement Prompt

## Process

1. **Analyze current state** — Read the asset content and understand its purpose
2. **Review scores** — Identify the lowest-scoring criteria
3. **Target weaknesses** — Focus the improvement on the 2-3 weakest areas
4. **Write specific instructions** — Tell the improver exactly what to change
5. **Include anti-patterns** — List what NOT to do

## Anti-Patterns to Avoid

- "Make it better" — Too vague, no direction
- "Improve all criteria" — Unfocused, leads to mediocre changes
- Contradictory instructions — "Be more concise but add more detail"
- Scope creep — "Also add error handling and..." (stick to evaluation criteria)

## Template

```
Improve the following [asset type]. Focus on these weak areas:
- [criterion]: scored [X]/[max] — [specific feedback from rubric]
- [criterion]: scored [X]/[max] — [specific feedback from rubric]

Do NOT:
- [anti-pattern relevant to this asset]
- [anti-pattern relevant to this asset]

Current content:
[content]
```
