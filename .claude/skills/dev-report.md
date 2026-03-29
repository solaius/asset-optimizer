---
name: dev-report
description: Generate standardized development work reports
---

# Dev Report

## Process

1. **Gather context:**
   - `git diff --stat HEAD~N` for files changed
   - `git log --oneline -N` for recent commits
   - Check test coverage changes

2. **Fill template** from `dev-reports/TEMPLATE.md`:
   - **Summary**: 1-2 sentences on what was accomplished
   - **Changes**: Bulleted list of changes with rationale
   - **Decisions**: Key decisions and why they were made
   - **Metrics**: Tests added, coverage delta, files changed count
   - **Next Steps**: What should happen next

3. **Save to** `dev-reports/YYYY-MM-DD-<topic>.md`

4. **Commit** the report

## Rules

- Keep it concise — the report supplements the git log, not replaces it
- Focus on decisions and rationale — the "why" behind changes
- Include metrics — numbers make progress tangible
