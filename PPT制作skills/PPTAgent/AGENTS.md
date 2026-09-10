# Project and User Background

> Do not use plan mode unless user explicitly mentioned

## Purpose

This repository contains an agentic PowerPoint generation system with two closely related codepaths:

- `deeppresenter/`: the current runtime, CLI, multi-agent loop, MCP tool wiring, and HTML-to-PPTX pipeline.
- `pptagent/`: the earlier core generation and evaluation library, still shipped in the package and still used for the MCP server entrypoint `pptagent-mcp`.

When making changes, treat `deeppresenter` as the primary product surface unless the task is explicitly about legacy `pptagent` generation internals or the MCP server.

## Ground Truth

- Python package metadata and console entrypoints live in `pyproject.toml`.
- The main CLI command is `pptagent`, which points to `deeppresenter.cli:main`.
- The MCP server command is `pptagent-mcp`, which points to `pptagent.mcp_server:main`.
- Default runtime workspaces are created under `~/.cache/deeppresenter` unless `DEEPPRESENTER_WORKSPACE_BASE` is set.
- Configuration templates live at `deeppresenter/config.yaml.example` and `deeppresenter/mcp.json.example`.

Do not assume the root `README.md` is fully current. It still references paths like `webui.py` that are not present in this checkout. Prefer the code and `pyproject.toml` over prose docs when they conflict.

## Core Philosophy

### 1. Good Taste First

> "Sometimes you can look at a problem differently, restate it, and the special case disappears."

- Prefer restructuring the code so edge cases become ordinary cases.
- Good taste is mostly accumulated engineering judgment.
- Removing special-case branches is better than piling on conditionals.

### 2. Pragmatism Over Theory

> "I am a pragmatic bastard."

- Solve the real problem in this repository, not a hypothetical one.
- Reject theoretically elegant but operationally heavy designs when simpler approaches work.
- Code serves reality, not paper architecture.

### 3. Simplicity As A Constraint

> "If you need more than 3 levels of indentation, you're screwed and should fix your program."

- Keep functions short and focused.
- Prefer direct, obvious naming and structure.
- Treat unnecessary complexity as a defect.

## Code Style Rules

1. Avoid excessive exception handling. Do not hide normal control flow behind defensive wrappers unless there is a concrete failure mode to handle.
2. Add type hints to all functions and methods.
3. Write technical documentation and code comments in English.
4. Prefer modern tooling and current best practices:
   - use `uv`, `rg`, and current Python features where appropriate
   - follow current library APIs such as Pydantic `model_dump()` instead of legacy patterns
5. Prefer fewer dependencies and less code.
6. Keep `pyproject.toml` focused on the main `deeppresenter` product surface. Dependencies for isolated subdirectories should live in local `requirements.txt` files when that separation is real and maintainable.

## Communication Rules

- Think in English, reply to the user in Chinese.
- Be direct and concise. If code is bad, explain why in technical terms.
- Keep criticism focused on the implementation, design, or assumptions, never the person.
- Do not dilute technical judgment just to sound polite.

## High-Level Architecture

### `deeppresenter/`

- `cli/`: Typer CLI for `onboard`, `generate`, `serve`, `config`, and `clean`.
- `main.py`: orchestration entrypoint. `AgentLoop.run()` executes `Research` first, then either `PPTAgent` or `Design`, and finally exports artifacts.
- `agents/`: agent wrappers around the shared `Agent` base class.
  - `research.py`: builds manuscript / research output from prompt and attachments.
  - `pptagent.py`: runs PPT-oriented generation flow from markdown.
  - `design.py`: generates slide HTML, then relies on browser conversion.
- `tools/`: MCP-style tool servers for search, research, reflection, file conversion, and task management.
- `utils/`: config loading, constants, logging, MinerU integration, web conversion, MCP client support.
- `html2pptx/`: Node-based conversion helper used by the HTML slide pipeline.
- `test/`: integration-style tests for sandbox tools, browser/PDF conversion, image processing, and related utilities.

### `pptagent/`

- Core presentation generation, layout induction, document parsing, evaluation, and template-driven PPT production.
- `mcp_server.py` exposes the template-based slide creation workflow through FastMCP.
- `test/` contains both unit tests and tests marked `llm` / `parse`.

## Working Rules For Agents

- Inspect the actual entrypoint before editing. The same concept may exist in both `deeppresenter/` and `pptagent/`.
- Keep changes scoped. Do not refactor both stacks unless the task clearly spans both.
- If touching CLI behavior, inspect `deeppresenter/cli/commands.py`, `deeppresenter/cli/common.py`, and any config-loading path together.
- If touching orchestration, inspect `deeppresenter/main.py` and the relevant agent class under `deeppresenter/agents/`.
- If touching MCP behavior, confirm whether the change belongs in `deeppresenter/tools/*.py` or `pptagent/mcp_server.py`.
- If touching export/conversion, check both Python and Node sides:
  - `deeppresenter/utils/webview.py`
  - `deeppresenter/html2pptx/`
- Prefer preserving existing config names and environment variables; these are wired into onboarding and example configs.

## Known Sharp Edges

- The repository contains stale documentation from older layouts. Verify files exist before referencing or editing them.
- `deeppresenter` and `pptagent` both define generation-related concepts; changing one does not automatically update the other.
- Browser and Docker dependencies are part of the normal runtime, not optional dev extras for some codepaths.
- Some tests are integration-heavy and may fail if Playwright, Docker images, or model credentials are absent.

## File Map

- `pyproject.toml`: package metadata, dependencies, pytest markers, console scripts.
- `README.md`: user-facing overview, partially current.
- `pptagent/README.md`: older project framing focused on the original PPTAgent paper/system.
- `pptagent/DOC.md`: legacy documentation with useful conceptual background, but not always current for paths and startup flow.
- `deeppresenter/config.yaml.example`: model/runtime configuration schema.
- `deeppresenter/mcp.json.example`: MCP tool definitions and expected environment variables.

## Preferred Change Strategy

1. Confirm which stack owns the behavior.
2. Edit the smallest relevant surface.
3. Run the narrowest meaningful test subset.
4. Call out any dependency you could not validate locally.
