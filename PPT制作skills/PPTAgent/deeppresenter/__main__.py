#!/usr/bin/env python3
"""
DeepPresenter CLI - Terminal Interface

A command-line interface for DeepPresenter that can be run with uvx.

Features:
- Interactive onboarding for configuration
- Generate presentations from command line
- Support for multiple attachments
- Configurable output directory, pages, aspect ratio, and language
- Configuration management (view, reset)

Usage:
    # First time setup
    deeppresenter onboard  # or: pptagent onboard

    # Generate presentation
    deeppresenter generate "Your topic" -f file1.pdf -f file2.xlsx

    # View configuration
    deeppresenter config  # or: pptagent config

    # Reset configuration
    deeppresenter reset  # or: pptagent reset

For detailed usage, see README_CLI.md and USAGE_EXAMPLE.md
"""

from deeppresenter.cli import main

if __name__ == "__main__":
    main()
