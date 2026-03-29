from pathlib import Path

import pytest


@pytest.fixture
def tmp_asset_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for test assets."""
    assets = tmp_path / "assets"
    assets.mkdir()
    return assets


@pytest.fixture
def sample_prompt(tmp_asset_dir: Path) -> Path:
    """Create a sample prompt file for testing."""
    prompt_file = tmp_asset_dir / "test-prompt.txt"
    prompt_file.write_text("You are a helpful assistant.")
    return prompt_file
