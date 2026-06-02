from __future__ import annotations

import argparse
import csv
import io
import json
import os
import platform
import random
import shutil
import sys
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
from tensorflow.keras import layers
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input

from e5_utils import (
    copy_image_if_exists,
    ensure_dirs,
    project_root,
    render_pdf_first_page,
    render_text_image,
)


IMG_SIZE = (224, 224)
BATCH_SIZE = 32
SEED = 123
EPOCHS = 5
MAX_TFLITE_SAMPLES = 10
DATASET_URL = "https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz"
CLASS_DESCRIPTIONS = {
    "daisy": "雏菊",
    "dandelion": "蒲公英",
    "roses": "玫瑰",
    "sunflowers": "向日葵",
    "tulips": "郁金香",
}


def configure_tensorflow() -> None:
    os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "1")
    random.seed(SEED)
    np.random.seed(SEED)
    tf.random.set_seed(SEED)
    try:
        tf.config.threading.set_intra_op_parallelism_threads(4)
        tf.config.threading.set_inter_op_parallelism_threads(2)
    except RuntimeError:
        pass


def environment_lines() -> list[str]:
    return [
        f"Python: {sys.version.split()[0]}",
        f"Platform: {platform.platform()}",
        f"TensorFlow: {tf.__version__}",
        f"NumPy: {np.__version__}",
        f"Matplotlib: {matplotlib.__version__}",
        f"Pandas: {pd.__version__}",
        f"GPU devices: {tf.config.list_physical_devices('GPU')}",
        "Training device: local Windows CPU",
    ]


def write_data_source(root: Path, class_names: list[str], image_count: int) -> None:
    rows = "\n".join(
        f"| `{name}` | {CLASS_DESCRIPTIONS.get(name, name)} |" for name in class_names
    )
    (root / "data" / "data_source.md").write_text(
        f"""# 数据集说明

本实验使用 TensorFlow 官方示例花卉图片数据集 `flower_photos`。

| 项目 | 内容 |
|---|---|
| 数据集名称 | `flower_photos` |
| 数据来源 | `{DATASET_URL}` |
| 图片数量 | {image_count} |
| 类别数量 | {len(class_names)} |
| 是否提交完整数据集 | 不提交，Notebook 和脚本会自动下载 |

## 类别

| 标签 | 含义 |
|---|---|
{rows}

本实验使用公开示例数据完成 TensorFlow / Keras 训练、TFLite 转换和 Android 端接入验证流程。
""",
        encoding="utf-8",
    )


def download_dataset(root: Path) -> tuple[Path, list[str], int]:
    data_dir = tf.keras.utils.get_file("flower_photos", origin=DATASET_URL, untar=True)
    data_path = Path(data_dir)
    image_count = len(list(data_path.glob("*/*.jpg")))
    class_names = sorted(item.name for item in data_path.glob("*") if item.is_dir())

    lines = [
        f"Dataset directory: {data_path}",
        f"Image count: {image_count}",
        f"Classes: {', '.join(class_names)}",
        f"Source: {DATASET_URL}",
    ]
    render_text_image("Dataset Download", lines, root / "images" / "dataset_download.png")
    write_data_source(root, class_names, image_count)
    return data_path, class_names, image_count


def preview_dataset(root: Path, data_dir: Path, class_names: list[str]) -> None:
    rng = random.Random(SEED)
    sample_paths = []
    for class_name in class_names:
        paths = sorted((data_dir / class_name).glob("*.jpg"))
        sample_paths.append(rng.choice(paths))

    plt.figure(figsize=(12, 4))
    for i, path in enumerate(sample_paths):
        img = Image.open(path)
        plt.subplot(1, len(sample_paths), i + 1)
        plt.imshow(img)
        plt.title(path.parent.name)
        plt.axis("off")
    plt.tight_layout()
    plt.savefig(root / "outputs" / "dataset_preview.png", dpi=150)
    plt.savefig(root / "images" / "dataset_preview.png", dpi=150)
    plt.close()


def build_datasets(data_dir: Path):
    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="training",
        seed=SEED,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
    )
    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="validation",
        seed=SEED,
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
    )
    class_names = train_ds.class_names
    train_ds = train_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=tf.data.AUTOTUNE)
    return train_ds, val_ds, class_names


def model_summary_text(model: tf.keras.Model) -> list[str]:
    stream = io.StringIO()
    model.summary(print_fn=lambda line: stream.write(line + "\n"))
    return stream.getvalue().splitlines()


def extract_features(
    dataset: tf.data.Dataset,
    feature_model: tf.keras.Model,
    pool_layer: layers.Layer,
) -> tuple[np.ndarray, np.ndarray]:
    features = []
    labels = []
    for images, batch_labels in dataset:
        preprocessed = preprocess_input(tf.cast(images, tf.float32))
        batch_features = feature_model(preprocessed, training=False)
        batch_features = pool_layer(batch_features)
        features.append(batch_features.numpy())
        labels.append(batch_labels.numpy())
    return np.concatenate(features, axis=0), np.concatenate(labels, axis=0)


def train_model(root: Path, train_ds, val_ds, class_names: list[str]):
    num_classes = len(class_names)

    base_model = MobileNetV2(
        input_shape=IMG_SIZE + (3,),
        include_top=False,
        weights="imagenet",
        alpha=0.35,
    )
    base_model.trainable = False
    pool_layer = layers.GlobalAveragePooling2D(name="global_average_pooling")

    render_text_image(
        "Training Started",
        [
            "Using MobileNetV2 transfer learning.",
            "Base model: MobileNetV2 alpha=0.35, ImageNet weights, frozen.",
            f"Classifier epochs: {EPOCHS}",
            f"Image size: {IMG_SIZE[0]} x {IMG_SIZE[1]}",
            f"Classes: {', '.join(class_names)}",
        ],
        root / "images" / "training_started.png",
    )

    train_features, train_labels = extract_features(train_ds, base_model, pool_layer)
    val_features, val_labels = extract_features(val_ds, base_model, pool_layer)

    feature_inputs = tf.keras.Input(shape=train_features.shape[1:], name="mobilenetv2_features")
    x = layers.Dropout(0.2, name="dropout")(feature_inputs)
    head_outputs = layers.Dense(num_classes, activation="softmax", name="predictions")(x)
    head_model = tf.keras.Model(feature_inputs, head_outputs, name="flower_classifier_head")
    head_model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    started = time.time()
    history = head_model.fit(
        train_features,
        train_labels,
        validation_data=(val_features, val_labels),
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        verbose=2,
    )
    elapsed = time.time() - started

    inputs = tf.keras.Input(shape=IMG_SIZE + (3,), name="input_image")
    x = layers.Lambda(preprocess_input, name="mobilenetv2_preprocess")(inputs)
    x = base_model(x, training=False)
    x = pool_layer(x)
    outputs = head_model(x)
    model = tf.keras.Model(inputs, outputs, name="flower_mobilenetv2_classifier")
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    val_loss, val_accuracy = model.evaluate(val_ds, verbose=0)
    metrics = {
        "val_loss": float(val_loss),
        "val_accuracy": float(val_accuracy),
        "classes": class_names,
        "image_size": list(IMG_SIZE),
        "batch_size": BATCH_SIZE,
        "epochs": EPOCHS,
        "feature_extraction_seconds": round(float(elapsed), 2),
        "training_device": "local Windows CPU",
        "tensorflow_version": tf.__version__,
        "python_version": sys.version.split()[0],
    }
    (root / "outputs" / "evaluation_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    render_text_image(
        "Training Finished",
        [
            f"Epochs: {EPOCHS}",
            f"Final train accuracy: {history.history['accuracy'][-1]:.4f}",
            f"Final val accuracy during head training: {history.history['val_accuracy'][-1]:.4f}",
            f"Full model validation accuracy: {val_accuracy:.4f}",
            f"Full model validation loss: {val_loss:.4f}",
            f"Feature head training time: {elapsed:.2f} seconds",
        ],
        root / "images" / "training_finished.png",
    )
    render_text_image(
        "Evaluation Result",
        [
            f"Validation accuracy: {val_accuracy:.4f}",
            f"Validation loss: {val_loss:.4f}",
            f"Classes: {', '.join(class_names)}",
        ],
        root / "images" / "evaluation_result.png",
    )
    render_text_image("Model Structure", model_summary_text(model), root / "images" / "model_structure.png")

    return model, history, metrics


def plot_history(root: Path, history) -> None:
    acc = history.history.get("accuracy", [])
    val_acc = history.history.get("val_accuracy", [])
    loss = history.history.get("loss", [])
    val_loss = history.history.get("val_loss", [])
    epochs_range = range(1, len(acc) + 1)

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label="Train Accuracy")
    plt.plot(epochs_range, val_acc, label="Val Accuracy")
    plt.legend()
    plt.title("Accuracy")

    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label="Train Loss")
    plt.plot(epochs_range, val_loss, label="Val Loss")
    plt.legend()
    plt.title("Loss")

    plt.tight_layout()
    plt.savefig(root / "outputs" / "training_accuracy_loss.png", dpi=150)
    plt.savefig(root / "images" / "accuracy_loss_curve.png", dpi=150)
    plt.close()


def plot_confusion_matrix(root: Path, model: tf.keras.Model, val_ds, class_names: list[str]) -> None:
    y_true = []
    y_pred = []
    for images, labels in val_ds:
        preds = model.predict(images, verbose=0)
        y_true.extend(labels.numpy())
        y_pred.extend(np.argmax(preds, axis=1))

    cm = confusion_matrix(y_true, y_pred)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    fig, ax = plt.subplots(figsize=(8, 8))
    disp.plot(ax=ax, cmap="Blues", xticks_rotation=45)
    plt.title("Confusion Matrix")
    plt.tight_layout()
    plt.savefig(root / "outputs" / "confusion_matrix.png", dpi=150)
    plt.savefig(root / "images" / "confusion_matrix.png", dpi=150)
    plt.close(fig)


def show_sample_predictions(
    root: Path,
    model: tf.keras.Model,
    dataset,
    class_names: list[str],
    output_name: str,
) -> None:
    plt.figure(figsize=(12, 8))
    for images, labels in dataset.take(1):
        preds = model.predict(images, verbose=0)
        pred_ids = np.argmax(preds, axis=1)
        scores = np.max(preds, axis=1)
        for i in range(min(6, images.shape[0])):
            plt.subplot(2, 3, i + 1)
            img = images[i].numpy().astype("uint8")
            plt.imshow(img)
            true_label = class_names[int(labels[i])]
            pred_label = class_names[int(pred_ids[i])]
            plt.title(f"T:{true_label}\nP:{pred_label} {scores[i]:.2f}")
            plt.axis("off")
    plt.tight_layout()
    output_path = root / "outputs" / output_name
    plt.savefig(output_path, dpi=150)
    if output_name == "sample_predictions_keras.png":
        plt.savefig(root / "images" / "sample_predictions_keras.png", dpi=150)
    plt.close()


def save_models(root: Path, model: tf.keras.Model, class_names: list[str]) -> dict[str, int]:
    models_dir = root / "models"
    saved_model_dir = models_dir / "saved_model"
    keras_path = models_dir / "flower_classifier.keras"
    labels_path = models_dir / "labels.txt"

    if saved_model_dir.exists():
        shutil.rmtree(saved_model_dir)
    model.save(str(keras_path), save_format="h5")
    model.save(str(saved_model_dir), save_format="tf")
    labels_path.write_text("\n".join(class_names) + "\n", encoding="utf-8")

    render_text_image(
        "Keras Model Saved",
        [
            f"Keras model: {keras_path}",
            f"SavedModel: {saved_model_dir}",
            f"Labels: {labels_path}",
        ],
        root / "images" / "keras_model_saved.png",
    )

    return {
        "flower_classifier.keras": keras_path.stat().st_size,
        "labels.txt": labels_path.stat().st_size,
    }


def convert_models(root: Path) -> dict[str, int]:
    models_dir = root / "models"
    saved_model_dir = models_dir / "saved_model"

    converter = tf.lite.TFLiteConverter.from_saved_model(str(saved_model_dir))
    tflite_model = converter.convert()
    float_path = models_dir / "flower_classifier.tflite"
    float_path.write_bytes(tflite_model)

    quant_converter = tf.lite.TFLiteConverter.from_saved_model(str(saved_model_dir))
    quant_converter.optimizations = [tf.lite.Optimize.DEFAULT]
    quant_model = quant_converter.convert()
    quant_path = models_dir / "flower_classifier_quant.tflite"
    quant_path.write_bytes(quant_model)

    android_copy_path = models_dir / "FlowerModel_E5.tflite"
    shutil.copy2(float_path, android_copy_path)

    sizes = {
        "flower_classifier.tflite": float_path.stat().st_size,
        "flower_classifier_quant.tflite": quant_path.stat().st_size,
        "FlowerModel_E5.tflite": android_copy_path.stat().st_size,
    }
    render_text_image(
        "TFLite Conversion Success",
        [f"{name}: {size / 1024 / 1024:.2f} MB" for name, size in sizes.items()],
        root / "images" / "tflite_conversion_success.png",
    )
    render_text_image(
        "TFLite Model Files",
        [f"{path.name}: {path.stat().st_size} bytes" for path in sorted(models_dir.glob("*.tflite"))],
        root / "images" / "tflite_model_files.png",
    )
    return sizes


def run_tflite_inference(root: Path, data_dir: Path, class_names: list[str]) -> list[dict[str, str | float]]:
    model_path = root / "models" / "flower_classifier.tflite"
    # The Windows TFLite interpreter in TensorFlow 2.10 can fail on non-ASCII paths.
    ascii_model_dir = Path("C:/Temp/e5_tflite")
    ascii_model_dir.mkdir(parents=True, exist_ok=True)
    ascii_model_path = ascii_model_dir / "flower_classifier.tflite"
    shutil.copy2(model_path, ascii_model_path)
    interpreter = tf.lite.Interpreter(model_path=str(ascii_model_path))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]

    rows = []
    sample_paths: list[Path] = []
    for class_name in class_names:
        sample_paths.extend(sorted((data_dir / class_name).glob("*.jpg"))[:2])
    sample_paths = sample_paths[:MAX_TFLITE_SAMPLES]

    plt.figure(figsize=(12, 8))
    for i, path in enumerate(sample_paths):
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
        score = float(scores[pred_id])
        true_label = path.parent.name
        pred_label = class_names[pred_id]
        rows.append(
            {
                "image": str(path),
                "true_label": true_label,
                "pred_label": pred_label,
                "score": score,
            }
        )

        if i < 6:
            plt.subplot(2, 3, i + 1)
            plt.imshow(image)
            plt.title(f"T:{true_label}\nP:{pred_label} {score:.2f}")
            plt.axis("off")

    csv_path = root / "outputs" / "tflite_inference_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "true_label", "pred_label", "score"])
        writer.writeheader()
        writer.writerows(rows)

    plt.tight_layout()
    plt.savefig(root / "outputs" / "sample_predictions_tflite.png", dpi=150)
    plt.savefig(root / "images" / "sample_predictions_tflite.png", dpi=150)
    plt.close()

    lines = [
        f"Model: {model_path}",
        f"Interpreter load path: {ascii_model_path}",
        f"Input: shape={input_details['shape']}, dtype={input_details['dtype']}",
        f"Output: shape={output_details['shape']}, dtype={output_details['dtype']}",
        f"CSV: {csv_path}",
    ]
    lines.extend(
        f"{row['true_label']} -> {row['pred_label']} ({float(row['score']):.4f})"
        for row in rows[:8]
    )
    render_text_image("Python TFLite Inference", lines, root / "images" / "python_tflite_inference.png")
    return rows


def write_model_info(root: Path, metrics: dict, model_sizes: dict[str, int], tflite_rows: list[dict]) -> None:
    size_lines = "\n".join(f"- `{name}`: {size / 1024 / 1024:.2f} MB" for name, size in model_sizes.items())
    tflite_preview = "\n".join(
        f"- `{Path(row['image']).name}`: {row['true_label']} -> {row['pred_label']} ({float(row['score']):.4f})"
        for row in tflite_rows[:5]
    )
    (root / "models" / "model_info.md").write_text(
        f"""# 模型说明

| 项目 | 内容 |
|---|---|
| 模型名称 | `flower_classifier` |
| 任务类型 | 花卉图像分类 |
| 类别 | `{', '.join(metrics['classes'])}` |
| 输入尺寸 | {metrics['image_size'][0]} x {metrics['image_size'][1]} x 3 |
| 模型结构 | MobileNetV2 alpha=0.35 + GlobalAveragePooling + Dropout + Dense softmax |
| 训练方式 | 迁移学习，冻结 ImageNet 预训练 MobileNetV2，训练分类头 |
| 训练数据 | TensorFlow 官方 `flower_photos` |
| 训练轮数 | {metrics['epochs']} |
| 验证准确率 | {metrics['val_accuracy']:.4f} |
| 验证损失 | {metrics['val_loss']:.4f} |
| Python 端 TFLite 验证 | 成功 |
| E4 Android 接入 | 见 `android_integration/` 记录 |

## 输出文件大小

{size_lines}

## Python TFLite 样例推理

{tflite_preview}

## 当前限制

- 本地环境未检测到 GPU，训练在 CPU 上完成。
- 为保证实验闭环，使用冻结 MobileNetV2 特征提取并训练轻量分类头。
- Android 端效果会受摄像头画面、光照和模型 metadata 差异影响。
""",
        encoding="utf-8",
    )


def prepare_static_images(root: Path) -> None:
    course_root = root.parent
    pdf_path = Path("C:/Users/Administrator/Downloads/11_实验5_1_TensorFlow模型生成.pdf")
    render_pdf_first_page(pdf_path, root / "images" / "ppt_requirement.png")
    copy_image_if_exists(
        course_root / "E4_Intelligent_Image_Classification_App" / "images" / "final_app_overview.png",
        root / "images" / "e4_completed_before_e5.png",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-existing", action="store_true", help="Skip when core model files already exist.")
    args = parser.parse_args()

    configure_tensorflow()
    root = project_root()
    ensure_dirs(root)
    prepare_static_images(root)

    core_model = root / "models" / "flower_classifier.tflite"
    if args.skip_existing and core_model.exists():
        print(f"Existing model found: {core_model}")
        return

    render_text_image("Environment Check", environment_lines(), root / "images" / "environment_check.png")
    data_dir, class_names, image_count = download_dataset(root)
    preview_dataset(root, data_dir, class_names)
    train_ds, val_ds, class_names = build_datasets(data_dir)
    (root / "models" / "labels.txt").write_text("\n".join(class_names) + "\n", encoding="utf-8")

    model, history, metrics = train_model(root, train_ds, val_ds, class_names)
    plot_history(root, history)
    plot_confusion_matrix(root, model, val_ds, class_names)
    show_sample_predictions(root, model, val_ds, class_names, "sample_predictions_keras.png")

    model_sizes = save_models(root, model, class_names)
    tflite_sizes = convert_models(root)
    model_sizes.update(tflite_sizes)
    tflite_rows = run_tflite_inference(root, data_dir, class_names)
    write_model_info(root, metrics, model_sizes, tflite_rows)

    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
