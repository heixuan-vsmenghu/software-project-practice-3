from __future__ import annotations

import shutil
from pathlib import Path

import tensorflow as tf

from e5_utils import ensure_dirs, project_root


def main() -> None:
    root = project_root()
    ensure_dirs(root)
    models_dir = root / "models"
    saved_model_dir = models_dir / "saved_model"
    if not saved_model_dir.exists():
        raise FileNotFoundError(f"SavedModel not found: {saved_model_dir}")

    converter = tf.lite.TFLiteConverter.from_saved_model(str(saved_model_dir))
    float_model = converter.convert()
    float_path = models_dir / "flower_classifier.tflite"
    float_path.write_bytes(float_model)

    quant_converter = tf.lite.TFLiteConverter.from_saved_model(str(saved_model_dir))
    quant_converter.optimizations = [tf.lite.Optimize.DEFAULT]
    quant_path = models_dir / "flower_classifier_quant.tflite"
    quant_path.write_bytes(quant_converter.convert())

    shutil.copy2(float_path, models_dir / "FlowerModel_E5.tflite")
    print(f"Converted: {float_path}")
    print(f"Converted: {quant_path}")
    print(f"Copied: {models_dir / 'FlowerModel_E5.tflite'}")


if __name__ == "__main__":
    main()
