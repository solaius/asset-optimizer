from pathlib import Path

import yaml

from asset_optimizer.config import (
    AppConfig,
    DefaultsConfig,
    ServerConfig,
    StorageConfig,
    load_config,
)


def test_default_config_values() -> None:
    config = AppConfig()
    assert config.storage.backend == "sqlite"
    assert config.storage.sqlite_path == Path("./data/optimizer.db")
    assert config.server.host == "0.0.0.0"
    assert config.server.port == 8000
    assert config.defaults.max_iterations == 20
    assert config.defaults.min_improvement == 0.01
    assert config.defaults.convergence_strategy == "greedy"
    assert config.defaults.stagnation_limit == 5


def test_load_config_from_yaml(tmp_path: Path) -> None:
    config_data = {
        "storage": {"backend": "postgres", "postgres_url": "postgresql+asyncpg://localhost/test"},
        "server": {"port": 9000},
        "defaults": {"max_iterations": 50},
    }
    config_file = tmp_path / "asset-optimizer.yaml"
    config_file.write_text(yaml.dump(config_data))

    config = load_config(config_file)
    assert config.storage.backend == "postgres"
    assert config.storage.postgres_url == "postgresql+asyncpg://localhost/test"
    assert config.server.port == 9000
    assert config.defaults.max_iterations == 50


def test_load_config_missing_file_uses_defaults() -> None:
    config = load_config(Path("/nonexistent/config.yaml"))
    assert config.storage.backend == "sqlite"
    assert config.server.port == 8000


def test_storage_config_sqlite_defaults() -> None:
    config = StorageConfig()
    assert config.backend == "sqlite"
    assert config.sqlite_path == Path("./data/optimizer.db")
    assert config.postgres_url is None


def test_server_config_defaults() -> None:
    config = ServerConfig()
    assert config.host == "0.0.0.0"
    assert config.port == 8000


def test_defaults_config() -> None:
    config = DefaultsConfig(max_iterations=100, convergence_strategy="target")
    assert config.max_iterations == 100
    assert config.convergence_strategy == "target"
