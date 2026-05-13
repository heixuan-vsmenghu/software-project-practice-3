# CameraX 学习笔记

## 1. 什么是 CameraX

CameraX 是 Android Jetpack 提供的相机开发库。它把底层 Camera2 中复杂的设备兼容、生命周期管理、输出流配置封装成更容易使用的 API，让开发者可以用较少代码完成预览、拍照、录像和逐帧分析。

本项目在 `CameraXApp` 中使用 CameraX 构建了一个 XML 界面的相机应用，主功能包括实时预览、拍照保存、视频录制、平均亮度分析和前后摄像头切换。

## 2. CameraX 为什么适合 Android 相机开发

Android 设备型号很多，不同厂商相机能力差异也很大。直接使用 Camera2 时，需要手动处理相机设备打开、会话创建、Surface 组合、线程、方向、生命周期等细节。CameraX 通过 Use Case 抽象和 `bindToLifecycle()` 简化这些流程，更适合课程实验和后续移动 AI App 原型开发。

本项目的 `startCamera()` 中只需要创建 `Preview`、`ImageCapture`、`VideoCapture`、`ImageAnalysis`，再统一绑定到 Activity 生命周期，就能让相机随页面启动和销毁自动管理资源。

## 3. CameraX 和 Camera2 的区别

Camera2 是 Android 平台的底层相机 API，能力强但代码复杂。CameraX 是建立在 Camera2 之上的 Jetpack 库，目标是提供更稳定、简洁和兼容的开发体验。

在本项目里，我们不直接操作 `CameraDevice` 或 `CaptureSession`，而是使用 CameraX 的 Use Case。这样代码重点放在业务功能上：预览显示、点击拍照、点击录像、分析每一帧亮度。

## 4. 什么是 Use Case

Use Case 是 CameraX 对相机功能的抽象。一个 Use Case 表示一种相机数据使用方式。

本项目使用了四类 Use Case：

| Use Case | 本项目作用 |
|---|---|
| `Preview` | 把摄像头画面显示到 `PreviewView` |
| `ImageCapture` | 拍摄静态图片并保存到 MediaStore |
| `VideoCapture` | 录制视频并保存到 MediaStore |
| `ImageAnalysis` | 获取实时帧并计算平均亮度 |

不同设备对多个 Use Case 同时绑定的支持可能不同，因此本项目在 `startCamera()` 中先尝试绑定四个 Use Case。如果失败，会 fallback 到 `Preview + ImageCapture + VideoCapture`，避免直接崩溃。

## 5. Preview 的作用

`Preview` 用于显示实时相机画面。它本身不负责 UI 绘制，而是把输出连接到 `PreviewView`：

```kotlin
Preview.Builder()
    .build()
    .also {
        it.setSurfaceProvider(viewBinding.viewFinder.surfaceProvider)
    }
```

`viewBinding.viewFinder` 对应 XML 中的 `androidx.camera.view.PreviewView`。

## 6. ImageCapture 的作用

`ImageCapture` 负责拍照。本项目在 `takePhoto()` 中使用时间戳作为文件名，并通过 `MediaStore` 保存到系统相册：

- Android 10 及以上：`Pictures/CameraX-Image`
- Android 9 及以下：依赖系统默认图片集合和写入权限

拍照成功后，页面状态区和 Toast 会显示保存 URI。

## 7. VideoCapture 的作用

`VideoCapture<Recorder>` 负责视频录制。本项目使用：

```kotlin
val recorder = Recorder.Builder()
    .setQualitySelector(QualitySelector.from(Quality.HIGHEST))
    .build()

videoCapture = VideoCapture.withOutput(recorder)
```

录像按钮同时承担开始和停止功能。开始录像后按钮文字变为 `STOP CAPTURE`；停止并保存后恢复为 `START CAPTURE`。

`VideoRecordEvent.Start` 表示录制真正开始，`VideoRecordEvent.Finalize` 表示录制结束并得到保存结果。

## 8. ImageAnalysis 的作用

`ImageAnalysis` 可以拿到相机实时帧。本项目目前只计算 Y 平面的平均亮度：

```kotlin
val buffer = image.planes[0].buffer
val data = buffer.toByteArray()
val pixels = data.map { it.toInt() and 0xFF }
val luma = pixels.average()
```

页面显示 `Average luminosity`，Logcat 也输出同样的亮度值。

这部分是后续 LiteRT / 移动 AI 推理最重要的入口。后续可以把 `ImageProxy` 转成 `Bitmap` 或 `ByteBuffer`，再 resize、normalize，并传入 LiteRT 模型进行分类或检测。

## 9. ProcessCameraProvider 的作用

`ProcessCameraProvider` 是 CameraX 的相机入口。它负责把 Use Case 绑定到生命周期，也负责解绑旧的 Use Case。

本项目中每次启动相机、切换摄像头、开启或关闭分析时，都会重新调用 `startCamera()`，内部先 `unbindAll()`，再 `bindToLifecycle()`。

## 10. CameraSelector 的作用

`CameraSelector` 用来选择使用哪个摄像头。本项目默认使用后置摄像头：

```kotlin
private var cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
```

点击 `SWITCH CAMERA` 会在前置和后置之间切换，然后重新绑定 CameraX。

## 11. PreviewView / ViewFinder 的作用

`PreviewView` 是 CameraX 提供的专用预览控件，负责承载相机画面。本项目 XML 中的 id 是 `viewFinder`，MainActivity 通过 ViewBinding 访问它。

这也是本实验坚持 XML 布局的核心控件，不使用 Compose 作为主界面。

## 12. bindToLifecycle 的作用

`bindToLifecycle()` 把 Use Case 绑定到 Activity 生命周期。Activity 启动后相机开始工作，Activity 销毁时 CameraX 自动释放底层资源。

本项目仍然在 `onDestroy()` 中关闭 `Recording` 并关闭 `cameraExecutor`，避免后台线程泄漏。

## 13. Android 权限申请流程

本项目使用 `ActivityResultContracts.RequestMultiplePermissions()` 申请运行时权限。

申请权限包括：

- `CAMERA`
- `RECORD_AUDIO`
- Android 9 及以下额外申请 `WRITE_EXTERNAL_STORAGE`

如果用户授权，则调用 `startCamera()`；如果拒绝，则页面状态区提示缺少权限，并显示 Toast。

## 14. MediaStore 保存照片和视频的作用

`MediaStore` 是 Android 推荐的媒体文件写入方式。通过它保存的照片和视频会进入系统媒体库，能被相册、文件管理器等应用发现。

本项目照片保存到 `Pictures/CameraX-Image`，视频保存到 `Movies/CameraX-Video`。

## 15. ImageProxy.close() 为什么必须调用

`ImageAnalysis.Analyzer` 每收到一帧都会得到一个 `ImageProxy`。分析完成后必须调用：

```kotlin
image.close()
```

如果不关闭，CameraX 会认为这一帧仍在使用，后续帧可能被阻塞，亮度分析和预览都会出现卡顿。本项目在 `finally` 中调用 `image.close()`，确保异常情况下也会释放。

## 16. CameraX 如何为后续 LiteRT / 移动 AI 项目铺路

移动 AI App 需要持续获取相机画面，并把每一帧转成模型输入。CameraX 的 `ImageAnalysis` 正好负责这个环节。

本实验已经完成了实时帧获取和轻量计算。后续只需要把当前亮度分析逻辑替换为 LiteRT 推理流程，就可以扩展为垃圾分类、植物识别、食物识别、手势识别、目标检测等应用。
