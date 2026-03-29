# Development Rules

- All code must pass `uv run ruff check src/ tests/`, `uv run mypy src/asset_optimizer/`, and `uv run pytest` before committing
- TDD: write tests before implementation code
- Follow existing patterns in the codebase — check before adding new patterns
- Use UV for all dependency management (`uv add`, `uv sync`)
- All public functions must have type annotations
- Use `async/await` throughout the core engine
- Database access only through the repository layer (`storage/repository.py`)
- No direct SQL — use SQLAlchemy ORM
- Keep files focused — if a file grows beyond ~300 lines, consider splitting by responsibility
