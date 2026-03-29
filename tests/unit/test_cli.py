from typer.testing import CliRunner

from asset_optimizer.cli.main import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Asset Optimizer" in result.stdout


def test_serve_help() -> None:
    result = runner.invoke(app, ["serve", "--help"])
    assert result.exit_code == 0
    assert "--port" in result.stdout


def test_evaluations_list_help() -> None:
    result = runner.invoke(app, ["evaluations", "list", "--help"])
    assert result.exit_code == 0
