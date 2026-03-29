# Usage Rules

- Always validate provider connectivity before starting experiments
- Create baseline scores before optimization begins
- Warn if max_iterations > 50 (high cost potential)
- Never store API keys in config files — use environment variables (`${VAR_NAME}` syntax)
- All experiments must have an evaluation attached
- When creating evaluations, every rubric must have concrete scoring anchors at 4 levels
