# 架构分析

## 模块职责

| 组件 | 职责 |
|---|---|
| MainActivity | 应用入口，申请权限、启动 CameraX、观察识别结果 |
| CameraX Preview | 显示摄像头画面 |
| CameraX ImageAnalysis | 获取每一帧图像并交给分析器 |
| ImageAnalyzer | 将相机帧转换成模型输入，执行 TFLite 推理，输出识别结果 |
| YuvToRgbConverter / toBitmap | 把 CameraX 的 YUV 帧转换为 Bitmap，并处理旋转方向 |
| TensorImage | TensorFlow Lite Support Library 的图像输入格式 |
| FlowerModel | ML Model Binding 生成的 TFLite 花卉分类模型调用类 |
| Recognition | 识别结果数据对象，包含 label 和 confidence |
| RecognitionViewModel | 保存识别结果列表，并跨配置变化保留状态 |
| LiveData | 通知 UI 数据变化 |
| RecognitionAdapter | 把识别结果显示到 RecyclerView |

## 数据流

```text
CameraX Preview / ImageAnalysis
        ↓
ImageProxy
        ↓
toBitmap()
        ↓
TensorImage
        ↓
FlowerModel.process()
        ↓
probabilityAsCategoryList
        ↓
sortByDescending(score)
        ↓
List<Recognition>
        ↓
RecognitionViewModel / LiveData
        ↓
RecyclerView / RecognitionAdapter
        ↓
屏幕显示花卉识别结果
```

## MainActivity

`MainActivity` 不直接执行复杂 UI 渲染，也不在主线程里跑模型。它负责把权限、相机、分析器、ViewModel 和 Adapter 连接起来。`recogViewModel.recognitionList.observe(...)` 是 UI 更新入口。

## CameraX

`Preview` 和 `ImageAnalysis` 是两个不同 use case。Preview 的输出接到 `PreviewView`，给用户看实时画面。ImageAnalysis 的输出进入 `ImageAnalyzer`，给模型推理使用。

## 模型层

模型层由 `FlowerModel.tflite` 和 ML Model Binding 生成的 `FlowerModel` 类组成。代码不手写 `Interpreter`，而是调用 `FlowerModel.newInstance(ctx, options)` 与 `flowerModel.process(tfImage)`。

## 状态与 UI 层

`RecognitionViewModel` 持有 `MutableLiveData<List<Recognition>>`。Adapter 使用 `ListAdapter` 和 `DiffUtil` 只刷新变化项。`recognition_item.xml` 通过 Data Binding 将 `Recognition.label` 与 `Recognition.probabilityString` 绑定到 TextView。

## 线程与稳定性

ImageAnalysis 使用 `Executors.newSingleThreadExecutor()` 在后台线程推理。`STRATEGY_KEEP_ONLY_LATEST` 保留最近帧，避免处理堆积。`imageProxy.close()` 放在 `finally` 中，保证 CameraX 能继续投递帧。
