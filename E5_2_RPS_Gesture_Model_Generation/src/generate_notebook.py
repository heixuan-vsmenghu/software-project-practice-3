from __future__ import annotations

import textwrap

import nbformat as nbf

from e5_rps_utils import ensure_dirs, project_root


def code(source: str):
    return nbf.v4.new_code_cell(textwrap.dedent(source).strip())


def markdown(source: str):
    return nbf.v4.new_markdown_cell(textwrap.dedent(source).strip())


def main() -> None:
    root = project_root()
    ensure_dirs(root)
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }

    nb["cells"] = [
        markdown(
            """
            # 实验 5-2：TensorFlow 石头剪刀布手势模型生成

            本实验使用 TensorFlow / Keras 完成 `rock`、`paper`、`scissors` 三分类手势识别模型训练。实验过程包括数据集下载、图片预处理、Sequential 模型构建、`compile` 编译、`fit` 训练、测试集评估、图形化性能验证、模型保存、TFLite / LiteRT 转换和 Python 端 TFLite 推理验证。

            实验 5-1 完成了花卉图像分类模型生成，本实验 5-2 将同样的 TensorFlow / Keras 模型训练流程迁移到石头剪刀布手势识别任务中，为后续移动 AI 应用中的手势识别功能打基础。
            """
        ),
        markdown("## 1. 环境检查"),
        code(
            """
            import sys
            import platform
            from pathlib import Path

            import matplotlib
            import matplotlib.pyplot as plt
            import numpy as np
            import pandas as pd
            import tensorflow as tf

            print("Python:", sys.version)
            print("Platform:", platform.platform())
            print("TensorFlow:", tf.__version__)
            print("NumPy:", np.__version__)
            print("Matplotlib:", matplotlib.__version__)
            print("Pandas:", pd.__version__)
            print("GPU devices:", tf.config.list_physical_devices("GPU"))
            """
        ),
        markdown("## 2. 路径设置"),
        code(
            """
            PROJECT_ROOT = Path.cwd()
            if PROJECT_ROOT.name == "notebooks":
                PROJECT_ROOT = PROJECT_ROOT.parent

            DATA_DIR = PROJECT_ROOT / "data"
            MODELS_DIR = PROJECT_ROOT / "models"
            OUTPUTS_DIR = PROJECT_ROOT / "outputs"
            IMAGES_DIR = PROJECT_ROOT / "images"
            SRC_DIR = PROJECT_ROOT / "src"

            for directory in [DATA_DIR, MODELS_DIR, OUTPUTS_DIR, IMAGES_DIR]:
                directory.mkdir(parents=True, exist_ok=True)

            import sys
            sys.path.insert(0, str(SRC_DIR))

            print("Project root:", PROJECT_ROOT)
            print("Data dir:", DATA_DIR)
            print("Models dir:", MODELS_DIR)
            print("Outputs dir:", OUTPUTS_DIR)
            """
        ),
        markdown("## 3. 下载并解压数据集"),
        code(
            """
            from e5_rps_utils import TEST_URL, TRAIN_URL, count_images_by_class, prepare_dataset

            train_extract_dir, test_extract_dir, train_counts, test_counts = prepare_dataset(PROJECT_ROOT)
            print("Train URL:", TRAIN_URL)
            print("Test URL:", TEST_URL)
            print("Train dir:", train_extract_dir)
            print("Test dir:", test_extract_dir)
            print("训练集类别数量:", train_counts)
            print("测试集类别数量:", test_counts)
            """
        ),
        markdown("## 4. 检查数据集结构与类别分布"),
        code(
            """
            import matplotlib.pyplot as plt
            import numpy as np

            labels_for_plot = sorted(train_counts)
            x = np.arange(len(labels_for_plot))
            width = 0.36
            plt.figure(figsize=(8, 5))
            plt.bar(x - width / 2, [train_counts[name] for name in labels_for_plot], width, label="train")
            plt.bar(x + width / 2, [test_counts[name] for name in labels_for_plot], width, label="test", alpha=0.7)
            plt.title("RPS Dataset Class Distribution")
            plt.xlabel("Class")
            plt.ylabel("Image Count")
            plt.xticks(x, labels_for_plot)
            plt.legend()
            plt.tight_layout()
            plt.savefig(OUTPUTS_DIR / "class_distribution.png", dpi=150)
            plt.show()
            """
        ),
        markdown("## 5. 数据集图片预览"),
        code(
            """
            import random
            from PIL import Image

            random.seed(123)
            sample_paths = []
            for class_name in sorted(train_counts):
                paths = sorted((train_extract_dir / class_name).glob("*"))
                sample_paths.append(random.choice(paths))

            plt.figure(figsize=(10, 4))
            for i, path in enumerate(sample_paths):
                img = Image.open(path).convert("RGB")
                plt.subplot(1, len(sample_paths), i + 1)
                plt.imshow(img)
                plt.title(path.parent.name)
                plt.axis("off")
            plt.tight_layout()
            plt.savefig(OUTPUTS_DIR / "dataset_preview.png", dpi=150)
            plt.show()
            """
        ),
        markdown("## 6. 图片预处理与数据生成器"),
        code(
            """
            from tensorflow.keras.preprocessing.image import ImageDataGenerator

            IMG_SIZE = (150, 150)
            BATCH_SIZE = 32
            SEED = 123

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
                train_extract_dir,
                target_size=IMG_SIZE,
                batch_size=BATCH_SIZE,
                class_mode="categorical",
                subset="training",
                seed=SEED,
            )
            validation_generator = train_datagen.flow_from_directory(
                train_extract_dir,
                target_size=IMG_SIZE,
                batch_size=BATCH_SIZE,
                class_mode="categorical",
                subset="validation",
                seed=SEED,
            )
            test_generator = test_datagen.flow_from_directory(
                test_extract_dir,
                target_size=IMG_SIZE,
                batch_size=BATCH_SIZE,
                class_mode="categorical",
                shuffle=False,
            )

            class_indices = train_generator.class_indices
            index_to_class = {v: k for k, v in class_indices.items()}
            class_names = [index_to_class[i] for i in range(len(index_to_class))]
            (MODELS_DIR / "labels.txt").write_text("\\n".join(class_names) + "\\n", encoding="utf-8")
            print("class_indices:", class_indices)
            print("Class names in model output order:", class_names)
            """
        ),
        markdown("## 7. 定义 Sequential CNN 模型"),
        code(
            """
            from tensorflow.keras import layers, models

            preview_model = models.Sequential(
                [
                    layers.InputLayer(input_shape=(150, 150, 3), name="input_image"),
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
                    layers.Dense(3, activation="softmax", name="predictions"),
                ],
                name="rps_sequential_cnn",
            )
            preview_model.summary()
            """
        ),
        markdown(
            """
            ## 8. 编译模型 compile

            `compile` 用于告诉模型如何学习。`optimizer` 表示如何调整参数，`loss` 表示模型错得有多严重，`accuracy` 表示分类正确率。
            """
        ),
        code(
            """
            preview_model.compile(
                optimizer="adam",
                loss="categorical_crossentropy",
                metrics=["accuracy"],
            )
            print("Model compiled with optimizer=adam, loss=categorical_crossentropy, metrics=accuracy")
            """
        ),
        markdown(
            """
            ## 9. 训练模型 fit、评估、保存和 TFLite 转换

            下面调用 `src/train_rps_model.py` 中的完整训练流程。该流程会真实执行 `history = model.fit(...)`，并保存 Keras 模型、SavedModel、普通 TFLite、量化 TFLite、accuracy / loss 曲线、混淆矩阵和样例推理结果。为保证本地课堂实验效率，本次执行 5 个 epoch。
            """
        ),
        code(
            """
            import json
            from train_rps_model import run_training

            metrics = run_training(epochs=5)
            metrics
            """
        ),
        markdown("## 10. 查看准确率 / 损失曲线、混淆矩阵和样例预测"),
        code(
            """
            from IPython.display import Image as DisplayImage, display

            for image_name in [
                "training_accuracy_loss.png",
                "confusion_matrix.png",
                "sample_predictions_keras.png",
                "sample_predictions_tflite.png",
            ]:
                path = OUTPUTS_DIR / image_name
                print(path, "exists=", path.exists())
                if path.exists():
                    display(DisplayImage(filename=str(path)))
            """
        ),
        markdown("## 11. 测试集评估指标"),
        code(
            """
            import json

            metrics_path = OUTPUTS_DIR / "evaluation_metrics.json"
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            metrics
            """
        ),
        markdown("## 12. Python 端 TFLite 推理验证"),
        code(
            """
            import subprocess

            subprocess.run([sys.executable, str(SRC_DIR / "test_tflite_inference.py")], check=True)
            print((OUTPUTS_DIR / "tflite_inference_results.csv").read_text(encoding="utf-8").splitlines()[:10])
            """
        ),
        markdown("## 13. 模型文件检查"),
        code(
            """
            for path in sorted(MODELS_DIR.rglob("*")):
                if path.is_file():
                    print(f"{path.relative_to(PROJECT_ROOT)} - {path.stat().st_size} bytes")
            """
        ),
        markdown(
            """
            ## 14. 实验总结

            本实验完成了 TensorFlow 石头剪刀布手势识别模型生成。实验从数据集下载开始，完成了图片预处理、Sequential CNN 模型构建、`compile` 编译、`fit` 训练、测试集评估和性能图形绘制。通过 accuracy / loss 曲线、混淆矩阵和样例预测图，可以直观看到模型对 `rock`、`paper`、`scissors` 三类手势的识别效果。

            本实验还将 Keras 模型转换为 TFLite / LiteRT 模型，并使用 Python 端 TFLite Interpreter 验证推理结果，为后续在 Android 端接入手势识别模型打下基础。
            """
        ),
    ]

    output = root / "notebooks" / "E5_2_RPS_Gesture_Model_Generation.ipynb"
    nbf.write(nb, output)
    print(output)


if __name__ == "__main__":
    main()
