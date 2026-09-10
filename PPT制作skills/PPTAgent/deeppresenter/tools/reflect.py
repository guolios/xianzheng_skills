import base64
import os
import re
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Literal

from fastmcp import FastMCP
from mcp.types import ImageContent

from deeppresenter.utils.config import DeepPresenterConfig
from deeppresenter.utils.log import info, set_logger
from deeppresenter.utils.webview import (
    PlaywrightConverter,
    convert_html_to_pptx,
    playwright_lifespan,
)
from pptagent.model_utils import _get_lid_model

mcp = FastMCP("DeepPresenter", lifespan=playwright_lifespan)
CONFIG = DeepPresenterConfig.load_from_file(os.getenv("CONFIG_FILE"))
LID_MODEL = _get_lid_model()
REFLECTIVE_DESIGN = CONFIG.design_agent.is_multimodal and CONFIG.heavy_reflect


@mcp.tool()
async def inspect_slide(
    html_file: str,
    aspect_ratio: Literal["16:9", "4:3", "A1", "A2", "A3", "A4"] = "16:9",
) -> ImageContent | str:
    """
    Read the HTML file as an image.

    Returns:
        ImageContent: The slide as an image content
        str: Error message if inspection fails
    """
    html_path = Path(html_file).absolute()
    assert html_path.is_file() and html_path.suffix == ".html", (
        f"HTML path {html_path} does not exist or is not an HTML file"
    )
    await convert_html_to_pptx(html_path, aspect_ratio=aspect_ratio)

    if REFLECTIVE_DESIGN:
        pdf_path = Path(tempfile.mkdtemp()) / "slide.pdf"
        async with PlaywrightConverter() as converter:
            image_dir = await converter.convert_to_pdf(
                [html_path], pdf_path, aspect_ratio
            )
        image_path = image_dir / "slide_01.jpg"
        image_data = image_path.read_bytes()
        base64_data = (
            f"data:image/jpeg;base64,{base64.b64encode(image_data).decode('utf-8')}"
        )
        return ImageContent(
            type="image",
            data=base64_data,
            mimeType="image/jpeg",
        )
    else:
        return "This slide is valid."


@mcp.tool()
def inspect_manuscript(md_file: str) -> dict:
    """
    Inspect the markdown manuscript for general statistics and image asset validation.
    Args:
        md_file (str): The path to the markdown file
    """
    md_path = Path(md_file)
    assert md_path.exists(), f"file does not exist: {md_file}"
    assert md_file.lower().endswith(".md"), f"file is not a markdown file: {md_file}"

    with open(md_file, encoding="utf-8") as f:
        markdown = f.read()

    pages = [p for p in markdown.split("\n---\n") if p.strip()]
    result = defaultdict(list)
    result["num_pages"] = len(pages)
    label = LID_MODEL.predict(markdown[:1000].replace("\n", " "))
    result["language"] = label[0][0].replace("__label__", "")

    seen_images = set()
    for match in re.finditer(r"!\[(.*?)\]\((.*?)\)", markdown):
        label, path = match.group(1), match.group(2)
        path = path.split()[0].strip("\"'")

        if path in seen_images:
            continue
        seen_images.add(path)

        if re.match(r"https?://", path):
            result["warnings"].append(
                f"External link detected: {match.group(0)}, consider downloading to local storage."
            )
            continue

        if not (md_path.parent / path).exists() and not Path(path).exists():
            result["warnings"].append(f"Image file does not exist: {path}")

        if not label.strip():
            result["warnings"].append(f"Image {path} is missing alt text.")

        count = markdown.count(path)
        if count > 1:
            result["warnings"].append(
                f"Image {path} used {count} times in the whole presentation manuscript."
            )

    if len(result["warnings"]) == 0:
        result["success"].append(
            "Image asset validation passed: all referenced images exist."
        )

    return result


if __name__ == "__main__":
    work_dir = Path(os.environ["WORKSPACE"])
    assert work_dir.exists(), f"Workspace {work_dir} does not exist."
    os.chdir(work_dir)
    set_logger(f"task-{work_dir.stem}", work_dir / ".history" / "task.log")

    if REFLECTIVE_DESIGN:
        info("Reflective Design is enabled.")

    mcp.run(show_banner=False)
