from __future__ import annotations

import argparse
import csv
import io
import json
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
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from e5_rps_utils import (
    SEED,
    TEST_URL,
    TRAIN_URL,
    configure_reproducibility,
    copy_if_exists,
    ensure_dirs,
    format_size,
    prepare_dataset,
    project_root,
    render_pdf_first_page,
    render_text_image,
)


IMG_SIZE = (150, 150)
BATCH_SIZE = 32
DEFAULT_EPOCHS = 5


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


def class_names_from_generator(generator) -> list[str]:
    class_indices = generator.class_indices
    index_to_class = {index: name for name, index in class_indices.items()}
    return [index_to_class[i] for i in range(len(index_to_class))]


def write_labels(root: Path, class_names: list[str]) -> None:
    (root / "models" / "labels.txt").write_text("\n".join(class_names) + "\n", encoding="utf-8")


def build_generators(train_dir: Path, test_dir: Path):
    train_datagen = ImageDataGenerator(
        rescale=1.0 / 255,
        validation_split=0.2,
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        zoom_range=0.1,
        horizontal_flip=True,
    )
    test_datagen = ImageDataGenerator(rescale=1.0 / 255)
    train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training",
        seed=SEED,
    )
    validation_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
        seed=SEED,
    )
    test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        shuffle=False,
    )
    return train_generator, validation_generator, test_generator


def build_model(num_classes: int = 3) -> tf.keras.Model:
    model = models.Sequential(
        [
            layers.InputLayer(input_shape=IMG_SIZE + (3,), name="input_image"),
            layers.Conv2D(32, (3, 3), activation="relu", name="conv2d_1"),
            layers.MaxPooling2D(2, 2, name="maxpool_1"),
            layers.Conv2D(64, (3, 3), activation="relu", name="conv2d_2"),
            layers.MaxPooling2D(2, 2, name="maxpool_2"),
            layers.Conv2D(128, (3, 3), activation="relu", name="conv2d_3"),
            layers.MaxPooling2D(2, 2, name="maxpool_3"),
            layers.Conv2D(128, (3, 3), activation="relu", name="conv2d_4"),
            layers.MaxPooling2D(2, 2, name="maxpool_4"),
            layers.Flatten(name="flatten"),
            layers.Dropout(0.5, name="dropout"),
            layers.Dense(256, activation="relu", name="dense_1"),
            layers.Dense(num_classes, activation="softmax", name="predictions"),
        ],
        name="rps_sequential_cnn",
    )
    model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])
    return model


def model_summary_lines(model: tf.keras.Model) -> list[str]:
    stream = io.StringIO()
    model.summary(print_fn=lambda line: stream.write(line + "\n"))
    return stream.getvalue().splitlines()


def plot_class_distribution(root: Path, train_counts: dict[str, int], test_counts: dict[str, int]) -> None:
    labels = sorted(train_counts)
    x = np.arange(len(labels))
    width = 0.36
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(x - width / 2, [train_counts[name] for name in labels], width, label="train")
    ax.bar(x + width / 2, [test_counts[name] for name in labels], width, label="test", alpha=0.7)
    ax.set_title("RPS Dataset Class Distribution")
    ax.set_xlabel("Class")
    ax.set_ylabel("Image Count")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    fig.tight_layout()
    fig.savefig(root / "outputs" / "class_distribution.png", dpi=150)
    fig.savefig(root / "images" / "class_distribution.png", dpi=150)
    plt.close(fig)


def preview_dataset(root: Path, train_dir: Path, train_counts: dict[str, int]) -> None:
    rng = random.Random(SEED)
    sample_paths = []
    for class_name in sorted(train_counts):
        paths = sorted((train_dir / class_name).glob("*"))
        sample_paths.append(rng.choice(paths))
    fig = plt.figure(figsize=(10, 4))
    for i, path in enumerate(sample_paths):
        image = Image.open(path).convert("RGB")
        ax = fig.add_subplot(1, len(sample_paths), i + 1)
        ax.imshow(image)
        ax.set_title(path.parent.name)
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(root / "outputs" / "dataset_preview.png", dpi=150)
    fig.savefig(root / "images" / "dataset_preview.png", dpi=150)
    plt.close(fig)


def plot_history(root: Path, history) -> None:
    acc = history.history["accuracy"]
    val_acc = history.history["val_accuracy"]
    loss = history.history["loss"]
    val_loss = history.history["val_loss"]
    epochs_range = range(1, len(acc) + 1)
    fig = plt.figure(figsize=(12, 5))
    ax1 = fig.add_subplot(1, 2, 1)
    ax1.plot(epochs_range, acc, label="Train Accuracy")
    ax1.plot(epochs_range, val_acc, label="Validation Accuracy")
    ax1.legend()
    ax1.set_title("Training and Validation Accuracy")
    ax2 = fig.add_subplot(1, 2, 2)
    ax2.plot(epochs_range, loss, label="Train Loss")
    ax2.plot(epochs_range, val_loss, label="Validation Loss")
    ax2.legend()
    ax2.set_title("Training and Validation Loss")
    fig.tight_layout()
    fig.savefig(root / "outputs" / "training_accuracy_loss.png", dpi=150)
    fig.savefig(root / "images" / "accuracy_loss_curve.png", dpi=150)
    plt.close(fig)


def plot_confusion(root: Path, model: tf.keras.Model, test_generator, class_names: list[str]) -> np.ndarray:
    test_generator.reset()
    pred_probs = model.predict(test_generator, verbose=1)
    pred_classes = np.argmax(pred_probs, axis=1)
    true_classes = test_generator.classes
    cm = confusion_matrix(true_classes, pred_classes)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
    fig, ax = plt.subplots(figsize=(7, 7))
    disp.plot(ax=ax, cmap="Blues", xticks_rotation=45)
    ax.set_title("RPS Confusion Matrix")
    fig.tight_layout()
    fig.savefig(root / "outputs" / "confusion_matrix.png", dpi=150)
    fig.savefig(root / "images" / "confusion_matrix.png", dpi=150)
    plt.close(fig)
    return cm


def plot_keras_predictions(root: Path, model: tf.keras.Model, test_generator, class_names: list[str]) -> None:
    test_generator.reset()
    images, labels = next(test_generator)
    preds = model.predict(images, verbose=0)
    pred_ids = np.argmax(preds, axis=1)
    true_ids = np.argmax(labels, axis=1)
    fig = plt.figure(figsize=(12, 8))
    for i in range(min(6, len(images))):
        ax = fig.add_subplot(2, 3, i + 1)
        ax.imshow(images[i])
        ax.set_title(f"T:{class_names[int(true_ids[i])]}\nP:{class_names[int(pred_ids[i])]} {preds[i][pred_ids[i]]:.2f}")
        ax.axis("off")
    fig.tight_layout()
    fig.savefig(root / "outputs" / "sample_predictions_keras.png", dpi=150)
    fig.savefig(root / "images" / "keras_predictions.png", dpi=150)
    plt.close(fig)


def save_models(root: Path, model: tf.keras.Model, class_names: list[str]) -> dict[str, int]:
    models_dir = root / "models"
    saved_model_dir = models_dir / "saved_model"
    if saved_model_dir.exists():
        shutil.rmtree(saved_model_dir)
    keras_path = models_dir / "rps_classifier.keras"
    model.save(str(keras_path), save_format="h5")
    model.save(str(saved_model_dir), save_format="tf")
    write_labels(root, class_names)
    render_text_image(
        "Keras Model Saved",
        [
            f"Keras model: {keras_path}",
            f"SavedModel: {saved_model_dir}",
            f"labels.txt: {models_dir / 'labels.txt'}",
            f"Keras size: {format_size(keras_path)}",
        ],
        root / "images" / "keras_model_saved.png",
    )
    return {
        "rps_classifier.keras": keras_path.stat().st_size,
        "labels.txt": (models_dir / "labels.txt").stat().st_size,
    }


def convert_to_tflite(root: Path) -> dict[str, int]:
    models_dir = root / "models"
    saved_model_dir = models_dir / "saved_model"
    float_path = models_dir / "rps_classifier.tflite"
    quant_path = models_dir / "rps_classifier_quant.tflite"

    converter = tf.lite.TFLiteConverter.from_saved_model(str(saved_model_dir))
    float_path.write_bytes(converter.convert())

    quant_converter = tf.lite.TFLiteConverter.from_saved_model(str(saved_model_dir))
    quant_converter.optimizations = [tf.lite.Optimize.DEFAULT]
    quant_path.write_bytes(quant_converter.convert())

    sizes = {
        "rps_classifier.tflite": float_path.stat().st_size,
        "rps_classifier_quant.tflite": quant_path.stat().st_size,
    }
    render_text_image(
        "TFLite Conversion Success",
        [f"{name}: {size / 1024 / 1024:.2f} MB" for name, size in sizes.items()],
        root / "images" / "tflite_conversion_success.png",
    )
    render_text_image(
        "TFLite Model Files",
        [f"{path.name}: {format_size(path)}" for path in sorted(models_dir.glob("*.tflite"))],
        root / "images" / "tflite_model_files.png",
    )
    return sizes


def run_tflite_inference(root: Path, test_dir: Path, class_names: list[str]) -> list[dict[str, str | float]]:
    model_path = root / "models" / "rps_classifier.tflite"
    ascii_model_dir = Path("C:/Temp/e5_2_tflite")
    ascii_model_dir.mkdir(parents=True, exist_ok=True)
    ascii_model_path = ascii_model_dir / "rps_classifier.tflite"
    shutil.copy2(model_path, ascii_model_path)

    interpreter = tf.lite.Interpreter(model_path=str(ascii_model_path))
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()[0]
    output_details = interpreter.get_output_details()[0]
    rows: list[dict[str, str | float]] = []
    sample_paths: list[Path] = []
    for class_name in class_names:
        sample_paths.extend(sorted((test_dir / class_name).glob("*"))[:3])
    sample_paths = sample_paths[:9]

    fig = plt.figure(figsize=(12, 8))
    for i, path in enumerate(sample_paths):
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
        top_id = int(top_ids[0])
        row = {
            "image": str(path),
            "true_label": path.parent.name,
            "pred_label": class_names[top_id],
            "score": float(scores[top_id]),
            "top3": "; ".join(f"{class_names[int(idx)]}:{float(scores[int(idx)]):.4f}" for idx in top_ids),
        }
        rows.append(row)
        if i < 6:
            ax = fig.add_subplot(2, 3, i + 1)
            ax.imshow(image)
            ax.set_title(f"T:{row['true_label']}\nP:{row['pred_label']} {float(row['score']):.2f}")
            ax.axis("off")

    csv_path = root / "outputs" / "tflite_inference_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "true_label", "pred_label", "score", "top3"])
        writer.writeheader()
        writer.writerows(rows)

    fig.tight_layout()
    fig.savefig(root / "outputs" / "sample_predictions_tflite.png", dpi=150)
    fig.savefig(root / "images" / "python_tflite_inference.png", dpi=150)
    plt.close(fig)

    render_text_image(
        "Python TFLite Inference",
        [
            f"Model: {model_path}",
            f"Interpreter load path: {ascii_model_path}",
            f"Input: shape={input_details['shape']}, dtype={input_details['dtype']}",
            f"Output: shape={output_details['shape']}, dtype={output_details['dtype']}",
            f"CSV: {csv_path}",
            *[f"{row['true_label']} -> {row['pred_label']} ({float(row['score']):.4f})" for row in rows[:8]],
        ],
        root / "images" / "python_tflite_inference_result.png",
    )
    return rows


def write_data_source(root: Path, train_counts: dict[str, int], test_counts: dict[str, int]) -> None:
    classes = sorted(train_counts)
    train_rows = "\n".join(f"| `{name}` | {train_counts[name]} |" for name in classes)
    test_rows = "\n".join(f"| `{name}` | {test_counts[name]} |" for name in classes)
    (root / "data" / "data_source.md").write_text(
        f"""# 数据集说明

本实验使用 Rock Paper Scissors 石头剪刀布图片数据集，数据来自 TensorFlow 课程示例数据地址。

| 项目 | 内容 |
|---|---|
| 数据集名称 | Rock Paper Scissors |
| 训练集 URL | `{TRAIN_URL}` |
| 测试集 URL | `{TEST_URL}` |
| 类别 | `{', '.join(classes)}` |
| 使用目的 | 软件实践研发课程实验 5-2，用于学习 TensorFlow / Keras 图像分类模型生成 |
| 是否提交完整图片数据集 | 不提交，Notebook 和脚本会自动下载并解压 |

## 训练集每类图片数量

| 类别 | 图片数量 |
|---|---:|
{train_rows}

## 测试集每类图片数量

| 类别 | 图片数量 |
|---|---:|
{test_rows}

本仓库只提交数据来源说明和运行后生成的图表，不提交 `rps.zip`、`rps-test-set.zip` 以及解压后的完整图片目录，避免 GitHub 仓库过大。
""",
        encoding="utf-8",
    )


def write_model_info(
    root: Path,
    metrics: dict,
    model_sizes: dict[str, int],
    tflite_rows: list[dict[str, str | float]],
) -> None:
    size_lines = "\n".join(f"- `{name}`: {size / 1024 / 1024:.2f} MB" for name, size in model_sizes.items())
    preview = "\n".join(
        f"- `{Path(str(row['image'])).name}`: {row['true_label']} -> {row['pred_label']} ({float(row['score']):.4f})"
        for row in tflite_rows[:6]
    )
    (root / "models" / "model_info.md").write_text(
        f"""# 模型说明

| 项目 | 内容 |
|---|---|
| 模型名称 | `rps_classifier` |
| 任务类型 | 石头剪刀布手势图像分类 |
| 类别 | `rock`, `paper`, `scissors` |
| 实际标签顺序 | `{', '.join(metrics['class_names'])}`，以 `labels.txt` 为准 |
| 输入尺寸 | {metrics['image_size'][0]} x {metrics['image_size'][1]} x 3 |
| 模型结构 | Keras Sequential CNN |
| 训练方式 | 监督学习 |
| 训练数据 | `rps.zip` |
| 测试数据 | `rps-test-set.zip` |
| 训练轮数 | {metrics['epochs']} |
| 测试集准确率 | {metrics['test_accuracy']:.4f} |
| 测试集损失 | {metrics['test_loss']:.4f} |
| Python 端 TFLite 验证 | 成功，见 `outputs/tflite_inference_results.csv` |

## 输出文件

- `rps_classifier.keras`
- `saved_model/`
- `rps_classifier.tflite`
- `rps_classifier_quant.tflite`
- `labels.txt`

## 模型文件大小

{size_lines}

## Python TFLite 样例推理

{preview}

## 当前限制

- 数据集背景比较单一，真实手机摄像头环境下可能受到光照、角度、背景影响。
- 本地训练使用 CPU，为保证课堂实验闭环，训练轮数控制为 {metrics['epochs']} 轮。
- 后续需要结合 CameraX 或 Android App 进行实时手势识别验证。
""",
        encoding="utf-8",
    )


def prepare_static_images(root: Path) -> None:
    pdf_path = Path("C:/Users/Administrator/Downloads/12_实验5_2_TensorFlow石头剪刀布手势模型生成.pdf")
    render_pdf_first_page(pdf_path, root / "images" / "ppt_requirement.png")


def run_training(epochs: int = DEFAULT_EPOCHS) -> dict:
    configure_reproducibility(tf)
    root = project_root()
    ensure_dirs(root)
    prepare_static_images(root)

    render_text_image("Environment Check", environment_lines(), root / "images" / "environment_check.png")
    train_dir, test_dir, train_counts, test_counts = prepare_dataset(root)
    write_data_source(root, train_counts, test_counts)
    render_text_image(
        "Dataset Download",
        [
            f"Train URL: {TRAIN_URL}",
            f"Test URL: {TEST_URL}",
            f"Train dir: {train_dir}",
            f"Test dir: {test_dir}",
            f"Train counts: {train_counts}",
            f"Test counts: {test_counts}",
        ],
        root / "images" / "dataset_download.png",
    )
    render_text_image(
        "Dataset Structure",
        [
            f"Train dir: {train_dir}",
            f"Test dir: {test_dir}",
            f"Train classes: {train_counts}",
            f"Test classes: {test_counts}",
        ],
        root / "images" / "dataset_structure.png",
    )
    plot_class_distribution(root, train_counts, test_counts)
    preview_dataset(root, train_dir, train_counts)

    train_generator, validation_generator, test_generator = build_generators(train_dir, test_dir)
    class_names = class_names_from_generator(train_generator)
    write_labels(root, class_names)

    model = build_model(num_classes=len(class_names))
    (root / "outputs" / "model_architecture.txt").write_text(
        "\n".join(model_summary_lines(model)) + "\n",
        encoding="utf-8",
    )
    render_text_image("Model Structure", model_summary_lines(model), root / "images" / "model_structure.png")
    render_text_image(
        "Training Started",
        [
            f"Model: {model.name}",
            f"Image size: {IMG_SIZE[0]} x {IMG_SIZE[1]}",
            f"Batch size: {BATCH_SIZE}",
            f"Epochs: {epochs}",
            f"Classes in output order: {class_names}",
            "Architecture: Sequential CNN with Conv2D, MaxPooling2D, Flatten, Dropout, Dense, softmax",
        ],
        root / "images" / "training_started.png",
    )

    started = time.time()
    history = model.fit(train_generator, epochs=epochs, validation_data=validation_generator, verbose=2)
    elapsed = time.time() - started
    plot_history(root, history)
    test_loss, test_accuracy = model.evaluate(test_generator, verbose=1)
    metrics = {
        "test_loss": float(test_loss),
        "test_accuracy": float(test_accuracy),
        "class_indices": train_generator.class_indices,
        "class_names": class_names,
        "image_size": list(IMG_SIZE),
        "batch_size": BATCH_SIZE,
        "epochs": epochs,
        "train_counts": train_counts,
        "test_counts": test_counts,
        "python_version": sys.version.split()[0],
        "tensorflow_version": tf.__version__,
        "numpy_version": np.__version__,
        "matplotlib_version": matplotlib.__version__,
        "pandas_version": pd.__version__,
        "gpu_devices": [str(device) for device in tf.config.list_physical_devices("GPU")],
        "training_device": "local Windows CPU",
        "training_seconds": round(float(elapsed), 2),
        "final_train_accuracy": float(history.history["accuracy"][-1]),
        "final_val_accuracy": float(history.history["val_accuracy"][-1]),
        "final_train_loss": float(history.history["loss"][-1]),
        "final_val_loss": float(history.history["val_loss"][-1]),
    }
    (root / "outputs" / "evaluation_metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    render_text_image(
        "Training Finished",
        [
            f"Epochs: {epochs}",
            f"Training time: {elapsed:.2f} seconds",
            f"Final train accuracy: {metrics['final_train_accuracy']:.4f}",
            f"Final validation accuracy: {metrics['final_val_accuracy']:.4f}",
            f"Test accuracy: {test_accuracy:.4f}",
            f"Test loss: {test_loss:.4f}",
        ],
        root / "images" / "training_finished.png",
    )
    render_text_image(
        "Evaluation Result",
        [
            f"Test accuracy: {test_accuracy:.4f}",
            f"Test loss: {test_loss:.4f}",
            f"Class order: {class_names}",
            f"Metrics JSON: {root / 'outputs' / 'evaluation_metrics.json'}",
        ],
        root / "images" / "evaluation_result.png",
    )
    plot_confusion(root, model, test_generator, class_names)
    plot_keras_predictions(root, model, test_generator, class_names)
    model_sizes = save_models(root, model, class_names)
    model_sizes.update(convert_to_tflite(root))
    tflite_rows = run_tflite_inference(root, test_dir, class_names)
    write_model_info(root, metrics, model_sizes, tflite_rows)
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()
    root = project_root()
    if args.skip_existing and (root / "models" / "rps_classifier.tflite").exists():
        print(f"Existing model found: {root / 'models' / 'rps_classifier.tflite'}")
        return
    metrics = run_training(epochs=args.epochs)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
