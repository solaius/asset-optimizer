---
name: register-asset-type
description: Step-by-step guide for adding new asset types to the framework
---

# Register Asset Type

## Process (TDD)

1. **Write test file** — Create `tests/unit/test_<type>_asset.py` with tests for:
   - `name` and `file_extensions` attributes
   - `load()` from file
   - `save()` to file
   - `validate()` with valid and invalid content
   - `default_evaluation()` returns valid config
   - `render_for_prompt()` produces useful output

2. **Implement asset type** — Create `src/asset_optimizer/assets/<type>.py`:
   - Implement all methods from `AssetTypeProtocol`
   - Handle edge cases (empty files, invalid content)

3. **Create default evaluation** — Create `evaluations/<type>-default.yaml`:
   - Define 3-5 criteria specific to this asset type
   - Write rubrics with concrete scoring anchors

4. **Register in registry** — Add to `src/asset_optimizer/assets/registry.py` default_registry

5. **Run tests** — `uv run pytest tests/unit/test_<type>_asset.py -v`

6. **Update documentation** — Add to `docs/asset-types.md`
