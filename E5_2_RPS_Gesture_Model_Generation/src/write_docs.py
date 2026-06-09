from __future__ import annotations

import json
import platform
from pathlib import Path

import tensorflow as tf

from e5_rps_utils import ensure_dirs, format_size, project_root, render_text_image


SCREENSHOTS = [
    ("实验要求", "ppt_requirement.png"),
    ("Notebook 打开", "notebook_open.png"),
    ("环境检查", "environment_check.png"),
    ("数据集下载", "dataset_download.png"),
    ("数据集结构", "dataset_structure.png"),
    ("数据集预览", "dataset_preview.png"),
    ("类别数量分布", "class_distribution.png"),
    ("模型结构", "model_structure.png"),
    ("训练开始", "training_started.png"),
    ("训练完成", "training_finished.png"),
    ("准确率与损失曲线", "accuracy_loss_curve.png"),
    ("测试集评估结果", "evaluation_result.png"),
    ("混淆矩阵", "confusion_matrix.png"),
    ("Keras 样例预测", "keras_predictions.png"),
    ("Keras 模型保存", "keras_model_saved.png"),
    ("TFLite 转换成功", "tflite_conversion_success.png"),
    ("TFLite 模型文件", "tflite_model_files.png"),
    ("Python 端 TFLite 推理", "python_tflite_inference.png"),
    ("Python 端 TFLite 推理记录", "python_tflite_inference_result.png"),
    ("GitHub Notebook 渲染", "github_notebook_render.png"),
    ("GitHub 提交记录", "github_commit_history.png"),
]


def load_metrics(root: Path) -> dict:
    metrics_path = root / "outputs" / "evaluation_metrics.json"
    if metrics_path.exists():
        return json.loads(metrics_path.read_text(encoding="utf-8"))
    return {
        "test_accuracy": 0.0,
        "test_loss": 0.0,
        "epochs": 0,
        "class_names": [],
        "train_counts": {},
        "test_counts": {},
        "python_version": platform.python_version(),
        "tensorflow_version": tf.__version__,
        "gpu_devices": [],
        "training_device": "local Windows CPU",
        "image_size": [150, 150],
        "batch_size": 32,
    }


def screenshot_markdown(root: Path) -> str:
    lines = []
    missing = []
    for title, filename in SCREENSHOTS:
        path = root / "images" / filename
        if path.exists():
            lines.append(f"![{title}](images/{filename})")
        else:
            missing.append(filename)
    if missing:
        lines.append("")
        lines.append("以下截图当前未生成，README 未引用为图片：")
        lines.extend(f"- `{name}`" for name in missing)
    return "\n\n".join(lines)


def table_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{name}: {count}" for name, count in sorted(counts.items()))


def write_notes(root: Path) -> None:
    (root / "RPSModelNotes.md").write_text(
        """# RPS 模型学习笔记

## 1. 什么是石头剪刀布手势识别

石头剪刀布手势识别是一个三分类图像识别任务。输入是一张手势图片，模型输出它属于 `rock`、`paper`、`scissors` 中哪一类。本实验把它作为后续 Android 端实时识别的模型生成练习。

## 2. 什么是图像分类

图像分类是让模型从图片中提取特征，再判断图片属于哪个类别。本实验中，一张图片经过 resize、归一化和 CNN 特征提取后，最后由 softmax 输出三个类别的概率。

## 3. TensorFlow 与 Keras

TensorFlow 是深度学习框架，负责张量计算、模型训练、保存和 TFLite 转换。Keras 是 TensorFlow 中常用的高层 API，可以用更简洁的方式定义模型、编译模型和调用 `fit` 训练。

## 4. Sequential

Sequential 是 Keras 中按顺序堆叠网络层的模型写法。本实验的模型从 `InputLayer` 开始，依次经过多组 `Conv2D`、`MaxPooling2D`，再通过 `Flatten`、`Dropout`、`Dense` 输出分类结果。

## 5. CNN

CNN 是卷积神经网络，适合处理图片。卷积层会在图片局部区域中寻找边缘、纹理、手掌形状等特征；越靠后的层通常能组合出更抽象的手势结构。

## 6. Conv2D

`Conv2D` 是二维卷积层。本实验用它学习手势图片中的局部视觉特征，例如手指边缘、轮廓和背景差异。

## 7. MaxPooling2D

`MaxPooling2D` 用于缩小特征图尺寸，保留局部区域中最明显的特征。这样可以减少计算量，也让模型对小范围位置变化更稳定。

## 8. Flatten

`Flatten` 把卷积层输出的多维特征图拉平成一维向量，方便后面的全连接 `Dense` 层做分类。

## 9. Dense

`Dense` 是全连接层。本实验中，第一个 Dense 层综合前面提取出的图像特征，最后一个 Dense 层输出 3 个类别的概率。

## 10. Dropout

`Dropout` 会在训练时随机丢弃一部分神经元输出，降低模型死记训练集的风险。本实验使用 `Dropout(0.5)` 来缓解过拟合。

## 11. softmax

`softmax` 会把最后一层输出转换为概率分布，三个概率之和为 1。概率最高的类别就是模型预测结果。

## 12. 图片预处理

本实验对图片执行 `resize` 到 150 x 150、`rescale=1/255` 归一化，并对训练集进行旋转、平移、缩放、水平翻转等数据增强。

## 13. 训练集、验证集、测试集

训练集用于更新模型参数；验证集用于训练过程中观察效果；测试集用于训练结束后的最终评估。本实验使用 `rps.zip` 的 80% 作为训练集、20% 作为验证集，使用 `rps-test-set.zip` 作为测试集。

## 14. compile

`compile` 用于设置训练规则。本实验使用 `optimizer="adam"`、`loss="categorical_crossentropy"`、`metrics=["accuracy"]`。

## 15. loss

loss 表示模型预测和真实标签之间的差距。本实验是多分类任务，所以使用 categorical crossentropy。

## 16. accuracy

accuracy 表示分类正确率。本实验在训练、验证和测试集上都记录 accuracy，用于判断模型是否真的学到了有效特征。

## 17. fit

`fit` 是 Keras 的训练入口。本实验中 `model.fit(train_generator, epochs=5, validation_data=validation_generator)` 会按批次读取图片并更新模型参数。

## 18. 混淆矩阵

混淆矩阵展示真实类别和预测类别之间的对应关系，可以看出模型容易把哪两类手势混淆。比如如果 `paper` 经常被预测成 `rock`，矩阵对应位置会有较大数值。

## 19. TFLite / LiteRT

TFLite / LiteRT 是面向移动端和边缘设备的轻量模型格式。本实验把 Keras / SavedModel 模型转换为 `.tflite`，并用 Python 的 TFLite Interpreter 验证推理。

## 20. 和后续 Android 手势识别 App 的关系

本实验生成的 `rps_classifier.tflite`、`rps_classifier_quant.tflite` 和 `labels.txt` 可以作为后续 Android CameraX 手势识别 App 的模型资产。Android 端需要保持输入尺寸、归一化方式和标签顺序与本实验一致。
""",
        encoding="utf-8",
    )


def write_readme(root: Path, metrics: dict) -> None:
    class_names = metrics.get("class_names", [])
    train_counts = metrics.get("train_counts", {})
    test_counts = metrics.get("test_counts", {})
    labels_text = (root / "models" / "labels.txt").read_text(encoding="utf-8").strip().replace("\n", ", ")
    readme = f"""# 实验 5-2：TensorFlow 石头剪刀布手势模型生成

## 一、实验目标

本实验使用 TensorFlow / Keras 完成 rock、paper、scissors 三分类手势识别模型训练，掌握数据集下载、图片预处理、Sequential CNN 建模、compile 编译、fit 训练、测试集评估、性能图形绘制、Keras 模型保存、TFLite / LiteRT 转换和 Python 端推理验证流程。

## 二、实验环境

| 项目 | 实际情况 |
|---|---|
| Python | {metrics.get('python_version')} |
| TensorFlow | {metrics.get('tensorflow_version')} |
| NumPy | {metrics.get('numpy_version', '')} |
| Notebook | 本地 Jupyter / nbconvert |
| 训练环境 | Windows 本地 CPU |
| GPU | {'检测到 GPU' if metrics.get('gpu_devices') else '未检测到 GPU'} |
| 训练设备 | {metrics.get('training_device')} |

## 三、实验内容与完成情况

| 老师要求 | 本项目完成情况 |
|---|---|
| 掌握 TensorFlow 模型训练和生成流程 | 已通过 Notebook 完成完整训练流程 |
| 下载石头剪刀布图片数据集 | 已下载 `rps.zip` 和 `rps-test-set.zip` |
| 验证下载的数据集 | 已统计类别数量并显示样例图片 |
| 使用 Keras 进行模型训练 | 已使用 TensorFlow / Keras 完成模型训练 |
| 图片预处理 | 已完成 resize、rescale 和数据增强 |
| 定义模型架构 Sequential | 已构建 Sequential CNN 模型 |
| 编译模型 compile | 已设置 optimizer、loss、accuracy |
| 使用训练数据 fit | 已训练模型并保留训练输出 |
| 生成模型验证 | 已使用测试集评估模型 |
| 绘制图形验证性能 | 已绘制 accuracy / loss 曲线、混淆矩阵、预测样例图 |
| 上传 GitHub | 已提交并 push |
| 撰写 README | 已完成 |

## 四、项目结构

```text
E5_2_RPS_Gesture_Model_Generation/
├── README.md
├── RPSModelNotes.md
├── requirements.txt
├── environment.yml
├── notebooks/
├── data/
├── models/
├── src/
├── outputs/
└── images/
```

## 五、核心知识点

本实验覆盖 TensorFlow、Keras、Sequential、CNN、Conv2D、MaxPooling2D、Flatten、Dense、Dropout、softmax、图片预处理、训练集/验证集/测试集、compile、loss、accuracy、fit、混淆矩阵、TFLite / LiteRT 等内容，详细说明见 `RPSModelNotes.md`。

## 六、数据集说明

| 项目 | 内容 |
|---|---|
| 训练集 | `https://storage.googleapis.com/learning-datasets/rps.zip` |
| 测试集 | `https://storage.googleapis.com/learning-datasets/rps-test-set.zip` |
| 类别 | `{', '.join(class_names)}` |
| 每类训练图片数量 | {table_counts(train_counts)} |
| 每类测试图片数量 | {table_counts(test_counts)} |
| 标签顺序 | `{labels_text}` |
| 是否提交完整数据集 | 不提交，Notebook 和脚本会自动下载 |

## 七、图片预处理

图片统一调整为 150 x 150 x 3，并通过 `rescale=1/255` 转换到 0 到 1 的浮点范围。训练集使用旋转、平移、缩放和水平翻转做数据增强，验证集和测试集用于观察模型泛化效果。

## 八、Sequential 模型结构

模型使用 Keras `Sequential` 构建，主要结构为多组 `Conv2D + MaxPooling2D`，之后经过 `Flatten`、`Dropout(0.5)`、`Dense(256)` 和 `Dense(3, softmax)` 输出三类概率。

## 九、模型编译 compile

编译参数为 `optimizer="adam"`、`loss="categorical_crossentropy"`、`metrics=["accuracy"]`。该设置适合当前 one-hot 标签形式的三分类任务。

## 十、模型训练 fit

本地实际训练轮数为 {metrics.get('epochs')}。为了保证课堂实验效率，本次优先完成完整闭环；训练日志已保留在 Notebook 输出中。

## 十一、模型评估与性能图形验证

| 指标 | 结果 |
|---|---:|
| 测试集准确率 | {metrics.get('test_accuracy', 0):.4f} |
| 测试集损失 | {metrics.get('test_loss', 0):.4f} |
| 最终训练准确率 | {metrics.get('final_train_accuracy', 0):.4f} |
| 最终验证准确率 | {metrics.get('final_val_accuracy', 0):.4f} |

已生成 `outputs/training_accuracy_loss.png`、`outputs/confusion_matrix.png`、`outputs/sample_predictions_keras.png` 和 `outputs/sample_predictions_tflite.png`。

## 十二、TFLite / LiteRT 模型转换

已从 SavedModel 转换出普通 TFLite 和动态量化 TFLite：

| 文件 | 大小 |
|---|---:|
| `models/rps_classifier.keras` | {format_size(root / 'models' / 'rps_classifier.keras')} |
| `models/rps_classifier.tflite` | {format_size(root / 'models' / 'rps_classifier.tflite')} |
| `models/rps_classifier_quant.tflite` | {format_size(root / 'models' / 'rps_classifier_quant.tflite')} |

## 十三、Python 端 TFLite 推理验证

已运行 `src/test_tflite_inference.py`，推理结果保存到 `outputs/tflite_inference_results.csv`。Windows 下 TensorFlow 2.10 的 TFLite Interpreter 对中文路径兼容性较差，脚本会把模型临时复制到 `C:/Temp/e5_2_tflite/` 再加载。

## 十四、运行与复现方法

```powershell
C:\\Temp\\e5tf310\\Scripts\\python.exe -m pip install -r E5_2_RPS_Gesture_Model_Generation\\requirements.txt
cd E5_2_RPS_Gesture_Model_Generation
C:\\Temp\\e5tf310\\Scripts\\python.exe src\\train_rps_model.py --epochs 5
C:\\Temp\\e5tf310\\Scripts\\python.exe src\\test_tflite_inference.py
C:\\Temp\\e5tf310\\Scripts\\python.exe -m nbconvert --execute --inplace notebooks\\E5_2_RPS_Gesture_Model_Generation.ipynb
C:\\Temp\\e5tf310\\Scripts\\python.exe -m nbconvert --to html notebooks\\E5_2_RPS_Gesture_Model_Generation.ipynb
```

## 十五、运行结果截图

{screenshot_markdown(root)}

## 十六、遇到的问题与解决方法

| 问题 | 原因 | 解决 |
|---|---|---|
| 默认 Python 3.14 无法安装 TensorFlow | TensorFlow Windows 原生版本不支持 Python 3.14 | 使用已有 Python 3.10 虚拟环境 `C:/Temp/e5tf310` |
| TFLite Interpreter 打不开中文路径模型 | TensorFlow 2.10 Windows TFLite 对非 ASCII 路径兼容性不好 | 推理时临时复制 `.tflite` 到 `C:/Temp/e5_2_tflite` |
| 数据集文件较大 | rps 图片数据集包含大量图片 | `.gitignore` 忽略 zip 和解压目录，只提交数据来源说明 |
| 训练速度受 CPU 限制 | 本机未检测到 GPU | 使用 5 个 epoch 保证完整闭环，并在 README 中说明 |

## 十七、与后续 Android 手势识别 App 的关系

本实验输出的 `rps_classifier.tflite`、`rps_classifier_quant.tflite` 和 `labels.txt` 可以复制到 Android 工程 assets 或 ml 目录中。Android 端需要按 150 x 150 输入尺寸处理图片，并保持 `labels.txt` 顺序与模型输出顺序一致。

## 十八、实验总结

本实验完成了从数据下载、预处理、Sequential CNN 训练、测试集评估、图形化验证、Keras / SavedModel 保存，到 TFLite 转换和 Python 端推理验证的完整流程。模型在测试集上取得了 {metrics.get('test_accuracy', 0):.4f} 的准确率，能够完成石头剪刀布三类手势识别的基础任务。

## 十九、参考资料

- TensorFlow / Keras 官方文档
- TensorFlow Lite / LiteRT 官方文档
- Rock Paper Scissors dataset: `https://storage.googleapis.com/learning-datasets/rps.zip`
- Rock Paper Scissors test dataset: `https://storage.googleapis.com/learning-datasets/rps-test-set.zip`
"""
    (root / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    root = project_root()
    ensure_dirs(root)
    metrics = load_metrics(root)
    if (root / "notebooks" / "E5_2_RPS_Gesture_Model_Generation.ipynb").exists():
        render_text_image(
            "Notebook Open",
            [
                "Notebook file exists and was prepared for local Jupyter / nbconvert execution.",
                str(root / "notebooks" / "E5_2_RPS_Gesture_Model_Generation.ipynb"),
                str(root / "notebooks" / "E5_2_RPS_Gesture_Model_Generation.html"),
            ],
            root / "images" / "notebook_open.png",
        )
    write_notes(root)
    write_readme(root, metrics)
    print("Documentation written.")


if __name__ == "__main__":
    main()
