# TensorFlow / LiteRT 学习笔记

## 1. 什么是机器学习

机器学习是让计算机从数据中学习规律，而不是只依赖人工写死的规则。图像分类任务中，程序通过大量带标签图片学习“某类图片通常有什么特征”，再对新图片给出预测。

## 2. 训练数据和标签

训练数据是模型学习用的样本，标签是每个样本对应的答案。本实验中图片是训练数据，`daisy`、`dandelion`、`roses`、`sunflowers`、`tulips` 是标签。

## 3. 图像分类

图像分类是输入一张图片，输出它最可能属于哪个类别。本实验输出 5 个类别的概率，概率最高的类别就是模型最确信的预测。

## 4. Tensor

Tensor 可以理解为多维数组。图片在模型里通常表示为形状类似 `[1, 224, 224, 3]` 的 Tensor，含义是 1 张、224x224 像素、3 个 RGB 通道。

## 5. TensorFlow

TensorFlow 是用于构建、训练和部署机器学习模型的框架。它负责数据输入、神经网络计算、训练优化、模型保存和模型转换。

## 6. Keras

Keras 是 TensorFlow 中更高层的神经网络 API，适合快速搭建模型。本实验用 Keras 创建 MobileNetV2 迁移学习模型，并保存为 Keras / SavedModel 格式。

## 7. LiteRT / TensorFlow Lite

LiteRT 是 TensorFlow Lite 的新命名方向，核心目标是让模型能在移动端、嵌入式设备和边缘设备上高效推理。本实验生成 `.tflite` 模型并接入 Android App。

## 8. 为什么训练在电脑 / Colab，推理在手机

训练需要大量矩阵计算和数据读取，更适合电脑、服务器或 Colab。推理只需要使用训练好的模型计算一次输入结果，计算量更小，可以放到手机端实时运行。

## 9. 迁移学习

迁移学习是复用已经在大规模数据集上训练过的模型特征，再为当前任务训练新的分类头。本实验复用 ImageNet 预训练 MobileNetV2，只训练花卉 5 分类头。

## 10. 为什么使用 MobileNetV2

MobileNetV2 面向移动端设计，模型小、推理快，适合 Android App。本实验使用 `alpha=0.35` 的轻量 MobileNetV2，保证训练和转换流程顺利完成。

## 11. 训练集和验证集

训练集用于更新模型参数，验证集用于评估模型对未见样本的效果。本实验按 80% / 20% 拆分 `flower_photos` 数据集。

## 12. Accuracy

Accuracy 是准确率，表示预测正确的样本占总样本的比例。本实验验证准确率为 `0.8815`。

## 13. Loss

Loss 是损失值，用来衡量模型预测与真实标签之间的差距。训练目标是让 loss 尽量下降。本实验验证损失为 `0.3588`。

## 14. 混淆矩阵

混淆矩阵用于观察模型把每个真实类别预测成哪些类别。对角线越明显，说明分类越准确；非对角线可以帮助发现易混类别。

## 15. `.keras` 模型

`.keras` 是 Keras 模型保存文件。本实验使用 TensorFlow 2.10.1，在本地保存了 `models/flower_classifier.keras` 作为 Keras 模型文件。

## 16. SavedModel

SavedModel 是 TensorFlow 标准模型导出格式，适合继续加载、部署或转换。本实验将 SavedModel 输出到 `models/saved_model/`。

## 17. `.tflite` 模型

`.tflite` 是 TensorFlow Lite / LiteRT 使用的模型格式，体积更小，适合移动端推理。本实验生成了普通版和动态量化版。

## 18. TensorFlow Lite Converter

TensorFlow Lite Converter 用于把 SavedModel / Keras 模型转换为 `.tflite`。本实验通过 `tf.lite.TFLiteConverter.from_saved_model(...)` 完成转换。

## 19. 量化

量化是减少模型体积和计算成本的技术。动态范围量化会压缩权重，通常能显著减小文件大小。本实验量化模型约 `0.56 MB`。

## 20. 实验 5 与实验 4 的关系

实验 4 已经完成 Android 端 CameraX + TFLite 推理 + RecyclerView 展示链路。实验 5 负责训练自己的模型，并把模型替换回实验 4 App，形成训练、转换、移动端验证闭环。

## 21. 如何把 E5 模型接入 E4

本实验将 `models/FlowerModel_E5.tflite` 复制到 E4：

```text
E4_Intelligent_Image_Classification_App/TFLClassify/start/src/main/ml/FlowerModel.tflite
```

并将标签复制到：

```text
E4_Intelligent_Image_Classification_App/TFLClassify/start/src/main/assets/labels.txt
```

由于 E5 模型没有原 E4 示例模型的 metadata，Android 端改用 `Interpreter` 手动读取模型输出并映射标签。

## 22. 与期末移动 AI App 的关系

本实验完成了移动 AI App 的核心链路：模型训练、端侧格式转换、Python 端验证、Android 端模型替换和 CameraX 实时推理。期末项目可以复用这套思想，将不同任务的 `.tflite` 模型接入移动端应用。
