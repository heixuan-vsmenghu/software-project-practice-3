from __future__ import annotations

import csv
import pathlib
import shutil
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image

from e5_utils import ensure_dirs, project_root, render_text_image


IMG_SIZE = (224, 224)
DATASET_URL = "https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz"


def main() -> None:
    root = project_root()
    ensure_dirs(root)
    model_path = root / "models" / "flower_classifier.tflite"
    labels_path = root / "models" / "labels.txt"
    if not model_path.exists():
        raise FileNotFoundError(model_path)
    if not labels_path.exists():
        raise FileNotFoundError(labels_path)

    class_names = [line.strip() for line in labels_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    data_dir = pathlib.Path(tf.keras.utils.get_file("flower_photos", origin=DATASET_URL, untar=True))
    sample_paths = []
    for class_name in class_names:
        sample_paths.extend(sorted((data_dir / class_name).glob("*.jpg"))[:2])

    # TensorFlow 2.10's Windows TFLite interpreter can fail on non-ASCII paths.
    ascii_model_dir = Path("C:/Temp/e5_tflite")
    ascii_model_dir.mkdir(parents=True, exist_ok=True)
    ascii_model_path = ascii_model_dir / "flower_classifier.tflite"
    shutil.copy2(model_path, ascii_model_path)
    interpreter = tf.lite.Interpreter(model_path=str(ascii_model_path))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]

    rows = []
    for path in sample_paths:
        image = Image.open(path).convert("RGB").resize(IMG_SIZE)
        input_data = np.expand_dims(np.asarray(image).astype(np.float32), axis=0)
        if input_details["dtype"] == np.uint8:
            scale, zero_point = input_details["quantization"]
            input_data = input_data / scale + zero_point
            input_data = input_data.astype(np.uint8)
        interpreter.set_tensor(input_details["index"], input_data)
        interpreter.invoke()
        scores = interpreter.get_tensor(output_details["index"])[0]
        if output_details["dtype"] == np.uint8:
            scale, zero_point = output_details["quantization"]
            scores = scale * (scores.astype(np.float32) - zero_point)
        pred_id = int(np.argmax(scores))
        rows.append(
            {
                "image": str(path),
                "true_label": path.parent.name,
                "pred_label": class_names[pred_id],
                "score": float(scores[pred_id]),
            }
        )

    csv_path = root / "outputs" / "tflite_inference_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "true_label", "pred_label", "score"])
        writer.writeheader()
        writer.writerows(rows)

    lines = [
        f"Model: {model_path}",
        f"Interpreter load path: {ascii_model_path}",
        f"Input: shape={input_details['shape']}, dtype={input_details['dtype']}",
        f"Output: shape={output_details['shape']}, dtype={output_details['dtype']}",
        f"CSV: {csv_path}",
    ]
    lines.extend(f"{row['true_label']} -> {row['pred_label']} ({row['score']:.4f})" for row in rows[:8])
    render_text_image("Python TFLite Inference", lines, root / "images" / "python_tflite_inference.png")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
