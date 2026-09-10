from __future__ import annotations

from pydantic import BaseModel, Field


class Slide(BaseModel):
    index: int = Field(description="1-based slide index in the presentation outline.")
    title: str = Field(description="Concise slide title.")
    context: str = Field(
        default="",
        description="Short description of what the slide should present.",
    )


class Outline(BaseModel):
    slides: list[Slide] = Field(
        default_factory=list,
        description="Ordered slide outline for the presentation.",
    )
