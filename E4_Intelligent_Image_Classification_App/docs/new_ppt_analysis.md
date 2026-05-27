# 新解析课件补充说明

`10_TFLClassify_智能图像分类APP_解析.pdf` 不是新实验，而是实验 4 的代码解析、知识点补充和调试指南。本文件根据新 PPT 对已有 E4 工程进行核对和补强。

## 本实验的输入、处理、输出

| 阶段 | 内容 |
|---|---|
| 输入 | 摄像头实时画面 |
| 处理 | CameraX 帧分析、YUV/Bitmap 转换、TensorImage 封装、TFLite 模型推理 |
| 输出 | Top-3 花卉类别、置信度百分比、RecyclerView 展示 |

## Preview 与 ImageAnalysis 的分工

`Preview` 只负责显示画面。代码中通过：

```kotlin
preview.setSurfaceProvider(viewFinder.surfaceProvider)
```

把摄像头预览输出连接到 `PreviewView`。

`ImageAnalysis` 才负责拿到每一帧 `ImageProxy`，并在后台线程中调用 `ImageAnalyzer.analyze(imageProxy)` 执行图像转换和模型推理。

## 一帧图像如何变成分类结果

```text
Camera 权限
    ↓
PreviewView 显示摄像头画面
    ↓
ImageAnalysis 获取每一帧 ImageProxy
    ↓
YUV / ImageProxy 转 Bitmap，并处理方向
    ↓
TensorImage.fromBitmap(...)
    ↓
FlowerModel.process(tfImage)
    ↓
probabilityAsCategoryList
    ↓
sortByDescending { it.score }.take(MAX_RESULT_DISPLAY)
    ↓
Recognition(label, score)
    ↓
RecognitionViewModel.updateData(items)
    ↓
LiveData 通知 UI
    ↓
RecognitionAdapter / RecyclerView 刷新显示结果
```

## TensorImage 与 FlowerModel 的作用

`TensorImage` 是 TFLite Support Library 的图像输入封装，用于把 Bitmap 送入模型绑定类。`FlowerModel` 是由 ML Model Binding 根据 `FlowerModel.tflite` 生成的模型访问类，项目通过 `process(tfImage)` 获取分类概率列表。

## Recognition、ViewModel、LiveData、RecyclerView 的关系

`Recognition` 保存单条识别结果。`RecognitionViewModel` 保存结果列表并通过 LiveData 暴露给 UI。`MainActivity` 观察 LiveData，当新结果到达时调用 `RecognitionAdapter.submitList()`，RecyclerView 使用 Data Binding 把 label 和 confidence 显示出来。

## 两个 Gradle 开关

```groovy
buildFeatures {
    dataBinding = true
    mlModelBinding true
}
```

`dataBinding = true` 用于生成布局绑定类，让 `recognition_item.xml` 可以直接绑定 `Recognition` 对象。`mlModelBinding true` 用于根据 `.tflite` 文件生成 `FlowerModel` 类，降低手写 Interpreter 的复杂度。

## TODO 1-6 对应知识点

| TODO | 代码动作 | 知识点 |
|---|---|---|
| TODO 1 | 声明并初始化 TFLite 模型 | 模型生命周期、lazy、分析线程 |
| TODO 2 | ImageProxy 转 Bitmap，再转 TensorImage | 图像格式、方向校正、模型输入 |
| TODO 3 | 调用模型并排序概率列表 | 模型输出、Top-K、置信度 |
| TODO 4 | 转换为 Recognition 数据对象 | 数据建模、UI 展示字段 |
| TODO 5 | 添加 GPU delegate 依赖 | 硬件加速、依赖兼容 |
| TODO 6 | 根据设备选择 GPU 或 CPU | 运行策略、fallback |

## 常见问题定位

| 问题 | 可能原因 | 解决方法 |
|---|---|---|
| 权限未授权 | Manifest 或运行时权限未正确处理 | 检查 CAMERA 权限，必要时到真机设置中重新开启 |
| FlowerModel 找不到 | `.tflite` 未导入 start 模块或 `mlModelBinding` 未开启 | 把 `FlowerModel.tflite` 放到 start 模块 `ml` 目录，开启 `mlModelBinding` 并 Sync |
| 预览有画面但结果不变 | ImageAnalysis 未绑定或 `imageProxy.close()` 缺失 | 检查 `bindToLifecycle` 和 `analyze()` 的 `finally close` |
| 运行卡顿 | 分析分辨率过高、帧处理太频繁、GPU 不兼容 | 降低分辨率，减少 Top-K，使用 CPU fallback 或 GPU delegate |
| 列表闪烁 | RecyclerView 高频刷新 | 关闭 `itemAnimator` 或降低 UI 更新频率 |

## 本文件如何帮助完善实验 4

新 PPT 把实验 4 从“补 TODO”扩展成“理解完整移动端图像分类架构”。因此本项目不仅完成代码，还在 README、代码流程、架构分析和问题排查文档中补充了 CameraX、TFLite、ViewModel、LiveData、RecyclerView、Data Binding、ML Model Binding 的协作关系。
