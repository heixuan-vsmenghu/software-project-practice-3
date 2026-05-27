# 模型说明

| 项目 | 内容 |
|---|---|
| 模型名称 | `FlowerModel.tflite` |
| 模型任务 | 花卉图像分类 |
| 模型输入 | 图像 |
| 模型输出 | 各类别概率 |
| 模型来源 | TFLClassify 项目 `finish` 模块 |
| 是否本实验训练 | 否 |
| 是否本实验导入并调用 | 是 |

## 文件位置

来源：

```text
TFLClassify/finish/src/main/ml/FlowerModel.tflite
```

导入到 start 模块：

```text
TFLClassify/start/src/main/ml/FlowerModel.tflite
```

## ML Model Binding 的作用

开启：

```groovy
buildFeatures {
    mlModelBinding true
}
```

Gradle 会根据 `.tflite` 文件生成 `FlowerModel` 类。代码可以直接调用：

```kotlin
val flowerModel = FlowerModel.newInstance(ctx, options)
val outputs = flowerModel.process(tfImage).probabilityAsCategoryList
```

## 本实验中的调用方式

相机帧先经过 `toBitmap(imageProxy)` 转换为 Bitmap，再通过 `TensorImage.fromBitmap(bitmap)` 转为模型输入。模型输出按 score 降序排序，取 Top-3 并映射为 `Recognition`。

## 后续 E5 如何替换模型

后续如果训练自己的 LiteRT/TensorFlow Lite 模型，可以将新 `.tflite` 放入 `start/src/main/ml/`，同步项目生成新的模型绑定类，再根据新模型的输入输出结构调整 `TensorImage` 预处理和结果映射逻辑。
