from __future__ import annotations

import csv
import shutil
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image

from e5_rps_utils import ensure_dirs, prepare_dataset, project_root, render_text_image


IMG_SIZE = (150, 150)


def main() -> None:
    root = project_root()
    ensure_dirs(root)
    model_path = root / "models" / "rps_classifier.tflite"
    labels_path = root / "models" / "labels.txt"
    if not model_path.exists():
        raise FileNotFoundError(model_path)
    if not labels_path.exists():
        raise FileNotFoundError(labels_path)
    labels = [line.strip() for line in labels_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    _, test_dir, _, _ = prepare_dataset(root)

    ascii_model_dir = Path("C:/Temp/e5_2_tflite")
    ascii_model_dir.mkdir(parents=True, exist_ok=True)
    ascii_model_path = ascii_model_dir / "rps_classifier.tflite"
    shutil.copy2(model_path, ascii_model_path)

    interpreter = tf.lite.Interpreter(model_path=str(ascii_model_path))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]

    sample_paths = []
    for label in labels:
        sample_paths.extend(sorted((test_dir / label).glob("*"))[:3])
    rows = []
    for path in sample_paths:
        image = Image.open(path).convert("RGB").resize(IMG_SIZE)
        input_data = np.expand_dims(np.asarray(image).astype(np.float32) / 255.0, axis=0)
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
        top_ids = np.argsort(scores)[::-1][:3]
        rows.append(
            {
                "image": str(path),
                "true_label": path.parent.name,
                "pred_label": labels[int(top_ids[0])],
                "score": float(scores[int(top_ids[0])]),
                "top3": "; ".join(f"{labels[int(idx)]}:{float(scores[int(idx)]):.4f}" for idx in top_ids),
            }
        )

    csv_path = root / "outputs" / "tflite_inference_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "true_label", "pred_label", "score", "top3"])
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
    render_text_image("Python TFLite Inference", lines, root / "images" / "python_tflite_inference_result.png")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
