from enum import StrEnum
from hashlib import md5
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel
from pypdf import PdfReader

from deeppresenter.utils.typings import PowerPointType
from pptagent.model_utils import _get_lid_model

lid_model = _get_lid_model()

mapping = {
    "16:9 Widescreen": "16:9",
    None: "16:9",
    "4:3 Standard": "4:3",
    "A1 Poster (Single Page)": "A1",
}


class ConstraintType(StrEnum):
    STYLE = "style"
    COVER = "cover"
    AGENDA = "agenda"
    VISUAL_CHART = "visual_chart"
    VISUAL_KEYWORDS = "visual_keywords"
    KEYWORDS = "keywords"


class Constraint(BaseModel):
    page: int | None
    constraint: list[str]
    constraint_type: ConstraintType


class ConstraintEvalResult(BaseModel):
    """VLM evaluation result for a single constraint item"""

    constraint_type: str
    constraint: str
    status: str
    score: float
    reason: str


class SlideEvals(BaseModel):
    """Evaluation scores for a single slide"""

    page: int
    content: float = 0.0
    style: float = 0.0
    constraints: list[ConstraintEvalResult] | None = None


class Evals(BaseModel):
    """Aggregated evaluation scores (averages)"""

    constraint: float = 0.0
    constraint_vlm: float = 0.0
    content: float = 0.0
    style: float = 0.0


class DataPoint(BaseModel):
    prompt: str
    language: Literal["zh", "en"]
    source: str | None = None
    aspect_ratio: str | PowerPointType | None
    page_low: int | None
    page_high: int | None
    attachments: list[str] | None = None
    constraints: list[Constraint] | None = None
    extra_info: dict[str, Any]

    def model_post_init(self, context):
        self.aspect_ratio = PowerPointType(
            mapping.get(self.aspect_ratio, self.aspect_ratio)
        )
        return super().model_post_init(context)

    @property
    def task_id(self):
        task = self.prompt + "".join(self.attachments or [])
        return md5(task.encode()).hexdigest()[:8]

    @property
    def n_constraints(self) -> int:
        """Auto-calculate number of constraints"""
        count = 0
        if self.page_low is not None and self.page_high is not None:
            count += 1
        if self.aspect_ratio is not None:
            count += 1
        if self.language:  # language is always set
            count += 1
        return count

    def verify(self, pdf_file: Path, text: str) -> float:
        reader = PdfReader(str(pdf_file))
        result = []
        if self.page_low and self.page_high:
            result.append(self.page_low <= len(reader.pages) <= self.page_high)
        if self.aspect_ratio:
            ar_map = {
                PowerPointType.WIDE_SCREEN: 16 / 9,
                PowerPointType.STANDARD_SCREEN: 4 / 3,
                PowerPointType.POSTER: 594 / 841,
            }
            first_page = reader.pages[0]
            actual_ar = float(first_page.mediabox.width / first_page.mediabox.height)
            expected_ar = ar_map[self.aspect_ratio]
            result.append(abs(actual_ar - expected_ar) < 0.1)
        language = lid_model.predict(text[:1024].replace("\n", ""))[0][0]
        result.append(self.language == language.replace("__label__", ""))
        return sum(result) / len(result)
