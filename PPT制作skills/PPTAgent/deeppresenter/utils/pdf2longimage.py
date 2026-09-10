"""Convert a PDF to a single vertically-stitched image."""

import argparse

from pdf2image import convert_from_path
from PIL import Image


def pdf_to_long_image(
    pdf_path: str, image_path: str, dpi: int = 200, first_k: int | None = None
) -> None:
    pages = convert_from_path(pdf_path, dpi=dpi, last_page=first_k)
    width = max(p.width for p in pages)
    height = sum(p.height for p in pages)

    result = Image.new("RGB", (width, height))
    y = 0
    for page in pages:
        result.paste(page, (0, y))
        y += page.height

    result.save(image_path)
    print(f"Saved {len(pages)} pages -> {image_path} ({width}x{height})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path")
    parser.add_argument("image_path")
    parser.add_argument("--dpi", type=int, default=200)
    parser.add_argument("--first-k", type=int, default=None)
    args = parser.parse_args()
    pdf_to_long_image(args.pdf_path, args.image_path, args.dpi, args.first_k)
