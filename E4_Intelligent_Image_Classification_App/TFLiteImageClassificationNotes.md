# TFLite 图像分类学习笔记

## 什么是图像分类

图像分类是让模型判断一张图像最可能属于哪个类别。本实验中的类别是花卉，例如 `roses`、`tulips`、`daisy`、`dandelion` 等。模型不会框出花在图中的位置，而是给整张图像输出各类别的概率。

## 图像分类和目标检测的区别

| 任务 | 输出 | 本实验是否涉及 |
|---|---|---|
| 图像分类 | 一张图属于哪些类别，以及每类置信度 | 是 |
| 目标检测 | 物体类别、位置框、可能还有多个目标 | 否 |

## TensorFlow Lite / LiteRT

TensorFlow Lite，也可放在 Android + LiteRT 的移动 AI 主线中理解，是面向移动端和边缘设备的轻量模型运行方案。移动端算力、内存和电量都有限，因此需要体积小、推理快、能离线运行的模型。

## `.tflite` 模型文件

`.tflite` 是已经转换好的端侧模型文件。本实验使用 `FlowerModel.tflite`，它已经在教程工程的 `finish` 模块中提供。本实验没有重新训练模型，只是把模型导入 `start` 模块并调用。

## CameraX、ImageAnalysis 与 ImageProxy

CameraX 是 Android Jetpack 提供的相机库。本项目中：

- `Preview` 负责把摄像头画面显示到 `PreviewView`。
- `ImageAnalysis` 负责把每一帧交给 `ImageAnalyzer.analyze(imageProxy)`。
- `ImageProxy` 是 CameraX 传给分析器的一帧图像，用完必须 `close()`，否则后续帧可能不再进入分析器。

## 为什么要转 Bitmap 和 TensorImage

摄像头帧通常是 YUV 格式，不适合直接交给图像分类模型。项目通过 `YuvToRgbConverter` 转成 RGB Bitmap，并用旋转矩阵校正方向。随后：

```kotlin
val tfImage = TensorImage.fromBitmap(bitmap)
```

`TensorImage` 是 TensorFlow Lite Support Library 提供的图像输入封装，方便传给模型绑定类。

## FlowerModel.tflite 的作用

`FlowerModel.tflite` 接收图像输入，输出每个花卉类别的概率。开启 ML Model Binding 后，Android Studio/Gradle 会生成 `FlowerModel` 类，代码可以直接调用：

```kotlin
val outputs = flowerModel.process(tfImage).probabilityAsCategoryList
```

## 置信度 score 与 Top-K

模型输出中的 `score` 表示某个类别的置信度。界面通常不展示所有类别，而是排序后显示前几个：

```kotlin
sortByDescending { it.score }
take(MAX_RESULT_DISPLAY)
```

本项目 `MAX_RESULT_DISPLAY = 3`，即显示 Top-3。

## Recognition、ViewModel、LiveData、RecyclerView

`Recognition` 是 UI 使用的数据对象，保存 `label` 和 `confidence`，并把置信度格式化成百分比。

`RecognitionViewModel` 使用 `MutableLiveData<List<Recognition>>` 保存最新识别结果。`MainActivity` 观察 LiveData；每次模型推理结束后，分析器回调更新 ViewModel，RecyclerView 的 Adapter 通过 `submitList()` 刷新界面。

## GPU delegate 与 CPU fallback

GPU delegate 可以在兼容设备上加速推理，但并非所有设备都支持。本项目使用 `CompatibilityList` 检查设备能力：

- 支持 GPU：使用 `Model.Device.GPU`。
- 不支持 GPU：使用 CPU 4 线程 fallback。

这样既尝试加速，又不会因为 GPU 不可用导致 App 无法运行。

## 与后续 E5 的关系

E4 学的是端侧部署和调用链路。E5 如果训练自己的 LiteRT/TensorFlow Lite 模型，只需要替换模型文件和对应标签/输入输出适配，CameraX、TensorImage、ViewModel、LiveData、RecyclerView 的整体结构仍然可以复用。
