#!/usr/bin/env python3
"""DeepPresenter CLI package entry."""

import warnings

import typer

from .commands import clean, config, generate, onboard, serve

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*urllib3.*")
warnings.filterwarnings("ignore", message=".*chardet.*")
warnings.filterwarnings("ignore", message=".*charset_normalizer.*")

app = typer.Typer(
    help="DeepPresenter - Agentic PowerPoint Generation", no_args_is_help=True
)

app.command()(onboard)
app.command()(serve)
app.command()(generate)
app.command()(config)
app.command()(clean)


def main():
    """Entry point for uvx."""
    app()
