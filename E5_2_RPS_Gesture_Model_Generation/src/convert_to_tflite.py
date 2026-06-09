from __future__ import annotations

import tensorflow as tf

from e5_rps_utils import ensure_dirs, format_size, project_root, render_text_image


def main() -> None:
    root = project_root()
    ensure_dirs(root)
    models_dir = root / "models"
    saved_model_dir = models_dir / "saved_model"
    if not saved_model_dir.exists():
        raise FileNotFoundError(f"SavedModel not found: {saved_model_dir}")

    converter = tf.lite.TFLiteConverter.from_saved_model(str(saved_model_dir))
    float_path = models_dir / "rps_classifier.tflite"
    float_path.write_bytes(converter.convert())

    quant_converter = tf.lite.TFLiteConverter.from_saved_model(str(saved_model_dir))
    quant_converter.optimizations = [tf.lite.Optimize.DEFAULT]
    quant_path = models_dir / "rps_classifier_quant.tflite"
    quant_path.write_bytes(quant_converter.convert())

    lines = [
        f"Converted: {float_path} ({format_size(float_path)})",
        f"Converted: {quant_path} ({format_size(quant_path)})",
    ]
    render_text_image("TFLite Conversion Success", lines, root / "images" / "tflite_conversion_success.png")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
