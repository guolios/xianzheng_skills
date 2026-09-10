import shlex
import subprocess
from pathlib import Path

from rich.console import Console

from deeppresenter import __version__ as version
from deeppresenter.utils.constants import PACKAGE_DIR

console = Console()
CONFIG_DIR = Path.home() / ".config" / "deeppresenter"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
MCP_FILE = CONFIG_DIR / "mcp.json"
CACHE_DIR = Path.home() / ".cache" / "deeppresenter"

LOCAL_MODEL = "Forceless/DeepPresenter-9B-GGUF:q4_K_M"
LOCAL_LID_MODEL = "Forceless/fasttext-language-id"
LOCAL_BASE_URL = "http://127.0.0.1:7811/v1"
REQUIRED_LLM_KEYS = ["research_agent", "design_agent", "long_context_model"]


def format_command(cmd: list[str]) -> str:
    """Format command for display."""
    return shlex.join(cmd)


def run_streaming_command(
    cmd: list[str],
    *,
    success_message: str | None = None,
    failure_message: str | None = None,
) -> bool:
    """Run command and stream output to console."""
    console.print(f"[dim]$ {format_command(cmd)}[/dim]")

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
    except FileNotFoundError:
        raise
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] Failed to start command: {e}")
        return False

    if process.stdout is not None:
        for line in process.stdout:
            console.print(line.rstrip())

    if process.wait() == 0:
        if success_message:
            console.print(success_message)
        return True

    if failure_message:
        console.print(failure_message)
    return False


__all__ = [
    "CACHE_DIR",
    "CONFIG_DIR",
    "CONFIG_FILE",
    "LOCAL_BASE_URL",
    "LOCAL_LID_MODEL",
    "LOCAL_MODEL",
    "MCP_FILE",
    "PACKAGE_DIR",
    "REQUIRED_LLM_KEYS",
    "console",
    "format_command",
    "run_streaming_command",
    "version",
]
