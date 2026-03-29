"""Typer CLI application for Asset Optimizer."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from asset_optimizer import __version__

app = typer.Typer(
    name="asset-optimizer",
    help="Asset Optimizer — automatic asset optimization using the autoimprove pattern.",  # noqa: E501
    no_args_is_help=True,
)
console = Console()

evaluations_app = typer.Typer(help="Manage evaluations")
experiments_app = typer.Typer(help="Manage experiments")
providers_app = typer.Typer(help="Manage AI providers")

app.add_typer(evaluations_app, name="evaluations")
app.add_typer(experiments_app, name="experiments")
app.add_typer(providers_app, name="providers")


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"asset-optimizer {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(  # noqa: B008
        False,
        "--version",
        "-v",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """Asset Optimizer CLI."""
    pass


@app.command()
def serve(
    host: str = typer.Option("0.0.0.0", help="Host to bind to"),  # noqa: B008
    port: int = typer.Option(8000, help="Port to bind to"),  # noqa: B008
    reload: bool = typer.Option(False, help="Enable auto-reload for development"),  # noqa: B008
) -> None:
    """Start the web server."""
    import uvicorn  # noqa: PLC0415

    from asset_optimizer.api.app import create_app  # noqa: PLC0415

    console.print(f"Starting Asset Optimizer on {host}:{port}")
    app_instance = create_app()
    uvicorn.run(app_instance, host=host, port=port, reload=reload)


@app.command()
def init(
    directory: Path = typer.Argument(Path("."), help="Directory to initialize"),  # noqa: B008
) -> None:
    """Initialize a new Asset Optimizer project."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "assets").mkdir(exist_ok=True)
    (directory / "evaluations").mkdir(exist_ok=True)
    (directory / "data").mkdir(exist_ok=True)

    config_file = directory / "asset-optimizer.yaml"
    if not config_file.exists():
        config_file.write_text(
            "# Asset Optimizer Configuration\n"
            "# See asset-optimizer.yaml.example for full options.\n\n"
            "storage:\n  backend: sqlite\n  sqlite_path: ./data/optimizer.db\n\n"
            "server:\n  host: 0.0.0.0\n  port: 8000\n\n"
            "defaults:\n  max_iterations: 20\n  convergence_strategy: greedy\n"
        )

    console.print(f"[green]Initialized Asset Optimizer project in {directory}[/green]")


@evaluations_app.command("list")
def evaluations_list() -> None:
    """List all evaluations."""
    console.print("Evaluations listing requires a running server or database.")
    console.print("Use: asset-optimizer serve, then visit the web UI.")


@evaluations_app.command("show")
def evaluations_show(
    name: str = typer.Argument(..., help="Evaluation name"),  # noqa: B008
) -> None:
    """Show evaluation details."""
    console.print(f"Evaluation: {name}")


@experiments_app.command("list")
def experiments_list() -> None:
    """List all experiments."""
    console.print("Experiments listing requires a running server or database.")


@experiments_app.command("show")
def experiments_show(
    experiment_id: str = typer.Argument(..., help="Experiment ID"),  # noqa: B008
) -> None:
    """Show experiment details."""
    console.print(f"Experiment: {experiment_id}")


@providers_app.command("test")
def providers_test(
    provider: str = typer.Option("openai", help="Provider name to test"),  # noqa: B008
) -> None:
    """Test provider connectivity."""
    console.print(f"Testing provider: {provider}")
    console.print("[yellow]Provider testing not yet implemented[/yellow]")
