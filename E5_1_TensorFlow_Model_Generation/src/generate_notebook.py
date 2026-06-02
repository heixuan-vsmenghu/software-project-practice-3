from __future__ import annotations

from pathlib import Path
import textwrap

import nbformat as nbf

from e5_utils import ensure_dirs, project_root


def code(source: str):
    return nbf.v4.new_code_cell(textwrap.dedent(source).strip())


def markdown(source: str):
    return nbf.v4.new_markdown_cell(textwrap.dedent(source).strip())


def main() -> None:
    root = project_root()
    ensure_dirs(root)
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3",
        },
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }

    nb["cells"] = [
        markdown(
            """
            # 实验 5-1：TensorFlow 模型生成

            本实验使用 TensorFlow / Keras 完成花卉图像分类模型训练，并使用 TensorFlow Lite Converter 将模型转换为 LiteRT / TFLite 模型。随后使用 Python 端推理脚本验证生成模型，并将生成的 `.tflite` 接入已经完成的实验 4 Android 智能图像分类 App。
            """
        ),
        markdown(
            """
            ## 1. 为什么不使用 Model Maker

            TensorFlow Lite Model Maker 曾经可以简化自定义数据集训练 TFLite 模型的流程，但该方案维护状态和依赖兼容性较差。本实验改用 TensorFlow / Keras 训练模型，再通过 TensorFlow Lite Converter 转换为 `.tflite` / LiteRT 模型。
            """
        ),
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
        code(
            """
            PROJECT_ROOT = Path.cwd()
            if PROJECT_ROOT.name == "notebooks":
                PROJECT_ROOT = PROJECT_ROOT.parent

            MODELS_DIR = PROJECT_ROOT / "models"
            OUTPUTS_DIR = PROJECT_ROOT / "outputs"
            IMAGES_DIR = PROJECT_ROOT / "images"
            SRC_DIR = PROJECT_ROOT / "src"

            print("Project root:", PROJECT_ROOT)
            print("Models dir:", MODELS_DIR)
            print("Outputs dir:", OUTPUTS_DIR)
            """
        ),
        markdown(
            """
            ## 2. 下载并查看 `flower_photos` 数据集

            数据集来自 TensorFlow 官方示例，包含 `daisy`、`dandelion`、`roses`、`sunflowers`、`tulips` 五类花卉图片。
            """
        ),
        code(
            """
            import pathlib

            dataset_url = "https://storage.googleapis.com/download.tensorflow.org/example_images/flower_photos.tgz"
            data_dir = tf.keras.utils.get_file("flower_photos", origin=dataset_url, untar=True)
            data_dir = pathlib.Path(data_dir)

            image_count = len(list(data_dir.glob("*/*.jpg")))
            class_names = sorted([item.name for item in data_dir.glob("*") if item.is_dir()])

            print("数据目录:", data_dir)
            print("图片数量:", image_count)
            print("类别:", class_names)
            """
        ),
        code(
            """
            from IPython.display import Image, display

            preview_path = OUTPUTS_DIR / "dataset_preview.png"
            if preview_path.exists():
                display(Image(filename=str(preview_path)))
            else:
                print("数据集预览图尚未生成。")
            """
        ),
        markdown(
            """
            ## 3. 训练模型并转换 TFLite

            本项目的完整训练逻辑在 `src/train_flower_model.py` 中。它会使用 MobileNetV2 迁移学习生成 `.keras`、SavedModel、普通 TFLite、量化 TFLite、标签文件、评估图表和 Python TFLite 推理结果。若模型文件已经存在，Notebook 会复用现有结果；删除 `models/flower_classifier.tflite` 后重新执行即可从头训练。
            """
        ),
        code(
            """
            import subprocess

            model_path = MODELS_DIR / "flower_classifier.tflite"
            if model_path.exists():
                print("模型已经生成，跳过重复训练:", model_path)
            else:
                subprocess.run([sys.executable, str(SRC_DIR / "train_flower_model.py")], check=True)
            """
        ),
        code(
            """
            import json

            metrics_path = OUTPUTS_DIR / "evaluation_metrics.json"
            metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
            metrics
            """
        ),
        code(
            """
            for image_name in [
                "training_accuracy_loss.png",
                "confusion_matrix.png",
                "sample_predictions_keras.png",
                "sample_predictions_tflite.png",
            ]:
                path = OUTPUTS_DIR / image_name
                print(path, "exists=", path.exists())
                if path.exists():
                    display(Image(filename=str(path)))
            """
        ),
        markdown(
            """
            ## 4. Python 端 TFLite 推理验证

            下面重新调用 `src/test_tflite_inference.py`，确认 `.tflite` 模型可以由 TensorFlow Lite Interpreter 加载并完成推理。Windows 下 TFLite Interpreter 对中文路径兼容性较差，脚本会把模型临时复制到 `C:/Temp/e5_tflite/` 再加载。
            """
        ),
        code(
            """
            subprocess.run([sys.executable, str(SRC_DIR / "test_tflite_inference.py")], check=True)
            print((OUTPUTS_DIR / "tflite_inference_results.csv").read_text(encoding="utf-8").splitlines()[:8])
            """
        ),
        markdown(
            """
            ## 5. 模型文件检查
            """
        ),
        code(
            """
            for path in sorted(MODELS_DIR.rglob("*")):
                if path.is_file():
                    print(f"{path.relative_to(PROJECT_ROOT)} - {path.stat().st_size} bytes")
            """
        ),
        markdown(
            """
            ## 6. 接入实验 4 Android App

            E5 生成的 `models/FlowerModel_E5.tflite` 已用于替换实验 4 `TFLClassify/start` 模块中的模型。由于自训练模型没有原始示例模型的 metadata，本次 Android 侧改为使用 TensorFlow Lite `Interpreter` 直接读取 `assets/FlowerModel.tflite` 和 `assets/labels.txt`，手动映射 softmax 输出为 `Recognition(label, score)`。
            """
        ),
        code(
            """
            integration_doc = PROJECT_ROOT / "android_integration" / "E4_model_replacement_record.md"
            if integration_doc.exists():
                print(integration_doc.read_text(encoding="utf-8"))
            else:
                print("Android 集成记录尚未生成。")
            """
        ),
    ]

    output = root / "notebooks" / "E5_1_TensorFlow_Flower_Model_Generation.ipynb"
    nbf.write(nb, output)
    print(output)


if __name__ == "__main__":
    main()
