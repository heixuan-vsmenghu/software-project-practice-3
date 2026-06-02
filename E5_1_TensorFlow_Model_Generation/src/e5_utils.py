from __future__ import annotations

import shutil
import textwrap
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


def project_root() -> Path:
    current = Path.cwd()
    if current.name == "notebooks":
        return current.parent
    if current.name == "src":
        return current.parent
    if (current / "E5_1_TensorFlow_Model_Generation").exists():
        return current / "E5_1_TensorFlow_Model_Generation"
    return current


def ensure_dirs(root: Path) -> None:
    for relative in [
        "data",
        "models",
        "models/saved_model",
        "notebooks",
        "outputs",
        "android_integration",
        "images",
    ]:
        (root / relative).mkdir(parents=True, exist_ok=True)


def find_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def render_text_image(
    title: str,
    lines: Iterable[str],
    output_path: Path,
    width: int = 1400,
    font_size: int = 24,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    font = find_font(font_size)
    title_font = find_font(font_size + 8)
    wrapped: list[str] = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        wrapped.extend(textwrap.wrap(str(line), width=78, replace_whitespace=False))

    line_height = font_size + 12
    height = max(360, 120 + line_height * (len(wrapped) + 1))
    image = Image.new("RGB", (width, height), color=(248, 250, 252))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 78), fill=(30, 64, 175))
    draw.text((34, 22), title, font=title_font, fill=(255, 255, 255))

    y = 108
    for line in wrapped:
        draw.text((34, y), line, font=font, fill=(15, 23, 42))
        y += line_height

    image.save(output_path)


def copy_image_if_exists(source: Path, destination: Path) -> bool:
    if source.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return True
    return False


def render_pdf_first_page(pdf_path: Path, output_path: Path) -> bool:
    try:
        import fitz

        if not pdf_path.exists():
            return False
        doc = fitz.open(str(pdf_path))
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(output_path))
        doc.close()
        return True
    except Exception:
        return False
