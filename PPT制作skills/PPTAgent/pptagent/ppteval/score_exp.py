import asyncio
import base64
import json
import shutil
import sys
import tempfile
from collections import defaultdict
from pathlib import Path

from deeppresenter.utils.config import LLM, get_json_from_response
from deeppresenter.utils.mineru_api import parse_pdf_online
from deeppresenter.utils.typings import ChatMessage, Role
from pptagent.ppteval import (
    content_descriptor,
    style_descriptor,
    text_scorer,
    vision_scorer,
)
from pptagent.ppteval.typings import (
    DataPoint,
    Evals,
    SlideEvals,
)
from pptagent.utils import get_logger

logger = get_logger(__name__)

sem = asyncio.Semaphore(8)
gpt = LLM(
    model="gpt-5-2025-08-07",
    api_key="",
    is_multimodal=True,
)
mineru_token = ""
language_lm = vision_lm = gpt


async def score_workspace(workspace: Path):
    if (workspace / "evals.json").exists():
        return
    if not (workspace / ".datapoint.json").exists():
        return

    async with sem:
        dp = DataPoint(**json.loads((workspace / ".datapoint.json").read_text()))
        if (workspace / "intermediate_output.json").exists():
            inter = json.load((workspace / "intermediate_output.json").open())
            if "final" not in inter:
                return
            output_pdf = Path(inter["final"]).with_suffix(".pdf")
        else:
            return
        slide_folder = workspace / f".slide_images-pdf-{output_pdf.stem}"

        if not (workspace / ".slides.md").exists():
            if (workspace / "intermediate_output.json").exists():
                inter = json.load((workspace / "intermediate_output.json").open())
                shutil.copy(inter["manuscript"], workspace / ".slides.md")
            else:
                temp_dir = tempfile.mkdtemp()
                await parse_pdf_online(
                    output_pdf,
                    temp_dir,
                    mineru_token,
                )
                shutil.move(f"{temp_dir}/full.md", workspace / ".slides.md")
        slide_evals: list[SlideEvals] = []
        constraint_score = None
        if dp.n_constraints:
            constraint_score = dp.verify(
                output_pdf,
                (workspace / ".slides.md").read_text(encoding="utf-8", errors="ignore"),
            )

        for image in sorted(slide_folder.glob("*.jpg")):
            # Extract page number from filename like "slide_01.jpg"
            page_num = int(image.stem.split("_")[-1])
            base64_image = base64.b64encode(image.read_bytes()).decode("utf-8")
            messages = [
                ChatMessage(role=Role.SYSTEM, content=""),
                ChatMessage(
                    role=Role.USER,
                    content=[
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                ),
            ]
            messages[0].content = content_descriptor
            content_desc = await vision_lm.run(messages)

            messages[0].content = style_descriptor
            style_desc = await vision_lm.run(messages)

            messages.pop()
            messages[0].role = Role.USER

            messages[0].content = text_scorer.render(
                descr=content_desc.choices[0].message.content
            )
            text_score = await language_lm.run(messages)

            messages[0].content = vision_scorer.render(
                descr=style_desc.choices[0].message.content
            )
            vision_score = await language_lm.run(messages)

            try:
                content_score = get_json_from_response(
                    text_score.choices[0].message.content
                )
                vision_score = get_json_from_response(
                    vision_score.choices[0].message.content
                )
                slide_evals.append(
                    SlideEvals(
                        page=page_num,
                        content=content_score["score"],
                        style=vision_score["score"],
                    )
                )
            except Exception as exc:
                logger.warning(
                    "Failed to score slide %s in workspace %s: %s",
                    image,
                    workspace,
                    exc,
                )

        try:
            with open(workspace / "slide_evals.json", "w") as f:
                json.dump(
                    [s.model_dump() for s in slide_evals],
                    f,
                    ensure_ascii=False,
                    indent=4,
                )
            evals = Evals(
                constraint=constraint_score if constraint_score is not None else 0.0,
                content=sum(s.content for s in slide_evals) / len(slide_evals)
                if slide_evals
                else 0.0,
                style=sum(s.style for s in slide_evals) / len(slide_evals)
                if slide_evals
                else 0.0,
            )
            with open(workspace / "evals.json", "w") as f:
                json.dump(evals.model_dump(), f, ensure_ascii=False, indent=4)
        except Exception:
            logger.exception("Failed to write evaluation results for %s", workspace)
        # finally:
        #   print(f"Scored {workspace}")


def log_scores(root: str, pattern: str):
    # framework/model/task dimension
    eval_files = list(Path(root).glob(pattern))
    scores = defaultdict(
        lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    )
    for ws in eval_files:
        framework, model, task = ws.parts[-4:-1]
        with open(ws) as f:
            evals = json.load(f)
        for dim, score in evals.items():
            if dim == "constraint":
                score *= 5
            scores[framework][model][task][dim].append(score)

    print(f"Total evals: {len(eval_files)}")
    for framework in sorted(scores):
        print(f"\n=== {framework} ===")
        for model in sorted(scores[framework]):
            print(f"  {model}:")
            all_dims = defaultdict(list)
            for task in sorted(scores[framework][model]):
                dims = scores[framework][model][task]
                for d, v in dims.items():
                    all_dims[d].extend(v)

            avg_stats = {d: sum(v) / len(v) for d, v in all_dims.items()}
            avg_stats = {k: v for k, v in avg_stats.items()}
            overall_avg = sum(avg_stats.values()) / len(avg_stats)
            avg_str = " | ".join(f"{d}: {v:.2f}" for d, v in avg_stats.items())
            print(
                f"    {'[AVERAGE]':<20} (n={len(list(all_dims.values())[0]):>3}): {avg_str} | avg: {overall_avg:.2f}"
            )
