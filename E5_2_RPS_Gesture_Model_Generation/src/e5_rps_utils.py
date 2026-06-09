from __future__ import annotations

import os
import random
import shutil
import sys
import textwrap
import zipfile
from pathlib import Path
from typing import Iterable
from urllib.request import urlretrieve

import numpy as np
from PIL import Image, ImageDraw, ImageFont


TRAIN_URL = "https://storage.googleapis.com/learning-datasets/rps.zip"
TEST_URL = "https://storage.googleapis.com/learning-datasets/rps-test-set.zip"
SEED = 123


def project_root() -> Path:
    current = Path.cwd()
    if current.name in {"src", "notebooks"}:
        return current.parent
    if (current / "E5_2_RPS_Gesture_Model_Generation").exists():
        return current / "E5_2_RPS_Gesture_Model_Generation"
    return current


def ensure_dirs(root: Path) -> None:
    for relative in ["data", "models", "models/saved_model", "notebooks", "outputs", "images", "src"]:
        (root / relative).mkdir(parents=True, exist_ok=True)


def configure_reproducibility(tf_module=None) -> None:
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "1")
    random.seed(SEED)
    np.random.seed(SEED)
    if tf_module is not None:
        tf_module.random.set_seed(SEED)
        try:
            tf_module.config.threading.set_intra_op_parallelism_threads(4)
            tf_module.config.threading.set_inter_op_parallelism_threads(2)
        except RuntimeError:
            pass


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
    width: int = 1450,
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
        wrapped.extend(textwrap.wrap(str(line), width=82, replace_whitespace=False))

    line_height = font_size + 12
    height = max(360, 120 + line_height * (len(wrapped) + 1))
    image = Image.new("RGB", (width, height), color=(248, 250, 252))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 80), fill=(22, 101, 52))
    draw.text((34, 22), title, font=title_font, fill=(255, 255, 255))

    y = 108
    for line in wrapped:
        draw.text((34, y), line, font=font, fill=(15, 23, 42))
        y += line_height
    image.save(output_path)


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
    except Exception as exc:
        render_text_image("PPT Requirement", [f"PDF screenshot failed: {exc}", str(pdf_path)], output_path)
        return False


def count_images_by_class(base_dir: Path) -> dict[str, int]:
    counts: dict[str, int] = {}
    for class_dir in sorted(base_dir.iterdir()):
        if class_dir.is_dir():
            counts[class_dir.name] = len([p for p in class_dir.iterdir() if p.is_file()])
    return counts


def download_file(url: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.exists() and output_path.stat().st_size > 0:
        return
    urlretrieve(url, output_path)


def extract_zip(zip_path: Path, destination: Path, marker_dir: Path) -> None:
    if marker_dir.exists():
        return
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(destination)


def prepare_dataset(root: Path) -> tuple[Path, Path, dict[str, int], dict[str, int]]:
    data_dir = root / "data"
    train_zip = data_dir / "rps.zip"
    test_zip = data_dir / "rps-test-set.zip"
    train_dir = data_dir / "rps"
    test_dir = data_dir / "rps-test-set"

    download_file(TRAIN_URL, train_zip)
    download_file(TEST_URL, test_zip)
    extract_zip(train_zip, data_dir, train_dir)
    extract_zip(test_zip, data_dir, test_dir)

    return train_dir, test_dir, count_images_by_class(train_dir), count_images_by_class(test_dir)


def copy_if_exists(source: Path, destination: Path) -> bool:
    if source.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return True
    return False


def format_size(path: Path) -> str:
    if not path.exists():
        return "missing"
    size = path.stat().st_size
    if size >= 1024 * 1024:
        return f"{size / 1024 / 1024:.2f} MB"
    if size >= 1024:
        return f"{size / 1024:.2f} KB"
    return f"{size} bytes"


def python_version_line() -> str:
    return sys.version.split()[0]
