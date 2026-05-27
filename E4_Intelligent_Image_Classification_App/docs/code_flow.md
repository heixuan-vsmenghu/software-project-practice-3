# 代码流程说明

## App 启动流程

`MainActivity.onCreate()` 设置布局，检查相机权限，初始化 RecyclerView Adapter，并观察 `RecognitionListViewModel.recognitionList`。如果权限已授权，直接启动 CameraX；否则弹出 CAMERA 权限请求。

## 摄像头权限流程

```text
onCreate()
  ↓
allPermissionsGranted()
  ↓
已授权：startCamera()
未授权：ActivityCompat.requestPermissions(...)
  ↓
onRequestPermissionsResult()
  ↓
授权成功：startCamera()
授权失败：Toast + finish()
```

## CameraX 初始化流程

`startCamera()` 获取 `ProcessCameraProvider`，创建两个 use case：

- `Preview`：负责把摄像头画面显示到 `PreviewView`。
- `ImageAnalysis`：负责把每一帧送到 `ImageAnalyzer` 做 ML 推理。

两个 use case 一起通过 `cameraProvider.bindToLifecycle(this, cameraSelector, preview, imageAnalyzer)` 绑定到 Activity 生命周期。

## ImageAnalysis 分析流程

```text
ImageAnalyzer.analyze(imageProxy)
  ↓
TensorImage.fromBitmap(toBitmap(imageProxy))
  ↓
flowerModel.process(tfImage)
  ↓
probabilityAsCategoryList
  ↓
sortByDescending { it.score }.take(MAX_RESULT_DISPLAY)
  ↓
Recognition(output.label, output.score)
  ↓
listener(items.toList())
  ↓
recogViewModel.updateData(items)
  ↓
RecyclerView 刷新
```

重点：Preview 只负责显示画面，不是模型输入；ImageAnalysis 才是拿到帧并执行 ML 推理的入口；UI 不直接跑模型，而是观察 ViewModel 中的结果。

## 模型推理流程

`ImageAnalyzer` 使用 lazy 初始化 `FlowerModel`。初始化时先通过 `CompatibilityList` 检查 GPU delegate 支持情况。兼容设备使用 GPU；不兼容设备使用 CPU 4 线程 fallback。

推理时记录耗时：

```kotlin
val startTime = SystemClock.uptimeMillis()
val outputs = flowerModel.process(tfImage)
val elapsedTime = SystemClock.uptimeMillis() - startTime
```

Logcat 中会输出推理耗时和 Top-K 结果，方便调试。

## 结果排序流程

模型输出 `probabilityAsCategoryList` 包含多个类别及其 score。项目用：

```kotlin
sortByDescending { it.score }
take(MAX_RESULT_DISPLAY)
```

按置信度降序取 Top-3，再转换成 `Recognition(label, score)`。

## ViewModel / LiveData 更新 UI 流程

`ImageAnalyzer` 通过回调把结果交给 `MainActivity`。`MainActivity` 调用 `recogViewModel.updateData(items)`，ViewModel 使用 `_recognitionList.postValue(recognitions)` 更新 LiveData。UI 层观察 LiveData 并调用 `viewAdapter.submitList(it)` 刷新列表。

## 资源释放流程

`analyze(imageProxy)` 使用 `try/catch/finally`：

```kotlin
try {
    // inference
} catch (exc: Exception) {
    Log.e(TAG, "Image analysis failed", exc)
} finally {
    imageProxy.close()
}
```

这样无论模型推理成功还是失败，都能释放当前帧，避免 CameraX 停止投递后续帧。

## 常见错误与排查

| 问题 | 排查方向 |
|---|---|
| 没有权限弹窗 | 检查 Manifest 中 CAMERA 权限和运行时权限代码 |
| 有预览但结果不变 | 检查 ImageAnalysis 是否绑定、`imageProxy.close()` 是否在 finally 中 |
| 找不到 FlowerModel | 检查 `start/src/main/ml/FlowerModel.tflite` 和 `mlModelBinding true` |
| 构建失败 | 检查 JDK、SDK、AGP、依赖仓库和 TFLite 依赖版本 |
| 结果闪烁 | 检查 RecyclerView itemAnimator 和 LiveData 刷新频率 |
