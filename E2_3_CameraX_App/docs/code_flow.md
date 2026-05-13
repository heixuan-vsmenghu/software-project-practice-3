# CameraXApp 代码流程说明

## 1. 总体流程图

```text
onCreate()
  ↓
初始化 ViewBinding 和 cameraExecutor
  ↓
绑定 TAKE PHOTO / START CAPTURE / ANALYSIS / SWITCH CAMERA 按钮
  ↓
检查 CAMERA / RECORD_AUDIO / WRITE_EXTERNAL_STORAGE 权限
  ↓
授权成功
  ↓
startCamera()
  ↓
创建 Preview / ImageCapture / VideoCapture / ImageAnalysis
  ↓
bindToLifecycle()
  ↓
用户点击按钮
  ├── TAKE PHOTO → takePhoto() → MediaStore 保存图片
  ├── START CAPTURE → captureVideo() → MediaStore 保存视频
  ├── ANALYSIS → 开启或关闭 ImageAnalysis
  └── SWITCH CAMERA → 切换前后摄像头并重新绑定
```

## 2. App 启动流程

`MainActivity.onCreate()` 是入口。它完成四件事：

1. 使用 `ActivityMainBinding.inflate(layoutInflater)` 加载 XML 布局。
2. 创建 `Executors.newSingleThreadExecutor()` 作为图像分析线程。
3. 绑定拍照、录像、分析开关、切换摄像头按钮。
4. 检查运行时权限，权限通过后调用 `startCamera()`。

## 3. 权限检查流程

本项目把权限集中在 `requiredPermissions()` 中：

- 始终申请 `CAMERA`
- 始终申请 `RECORD_AUDIO`
- Android 9 及以下额外申请 `WRITE_EXTERNAL_STORAGE`

流程如下：

```text
allPermissionsGranted()
  ├── true  → startCamera()
  └── false → requestPermissionsLauncher.launch(requiredPermissions())
                 ├── 授权成功 → startCamera()
                 └── 授权失败 → Toast + 状态栏提示
```

这样避免了没有权限时直接启动摄像头导致崩溃。

## 4. startCamera 初始化流程

`startCamera()` 是 CameraX 初始化核心。

主要步骤：

1. 通过 `ProcessCameraProvider.getInstance(this)` 获取相机提供者。
2. 创建 `Preview` 并连接到 `PreviewView.surfaceProvider`。
3. 创建 `ImageCapture`。
4. 创建 `Recorder` 和 `VideoCapture<Recorder>`。
5. 如果启用分析，则创建 `ImageAnalysis` 并设置 `LuminosityAnalyzer`。
6. 调用 `cameraProvider.unbindAll()` 清理旧绑定。
7. 优先绑定 `Preview + ImageCapture + VideoCapture + ImageAnalysis`。
8. 如果设备不支持该组合，则 fallback 到 `Preview + ImageCapture + VideoCapture`。

## 5. Preview 绑定流程

XML 中的 `PreviewView` id 是 `viewFinder`。

```text
Preview.Builder().build()
  ↓
setSurfaceProvider(viewBinding.viewFinder.surfaceProvider)
  ↓
bindToLifecycle()
  ↓
实时摄像头画面显示在页面上半部分
```

在模拟器 Pixel_8 API 35 的 Virtual Scene 中，预览能显示室内虚拟场景。

## 6. 拍照流程

用户点击 `TAKE PHOTO` 后进入 `takePhoto()`：

```text
检查 imageCapture 是否为空
  ↓
生成时间戳文件名
  ↓
构造 ContentValues
  ↓
Android 10+ 设置 Pictures/CameraX-Image
  ↓
创建 ImageCapture.OutputFileOptions
  ↓
imageCapture.takePicture()
  ├── 成功 → Toast + 状态栏显示 savedUri
  └── 失败 → Log.e + 状态栏显示错误
```

照片通过 MediaStore 写入系统图片库。

## 7. 录像流程

用户点击 `START CAPTURE` 后进入 `captureVideo()`。

第一次点击：

```text
recording == null
  ↓
生成时间戳文件名
  ↓
构造 MediaStoreOutputOptions
  ↓
如果 RECORD_AUDIO 已授权，启用 withAudioEnabled()
  ↓
pendingRecording.start()
  ↓
VideoRecordEvent.Start
  ↓
按钮变成 STOP CAPTURE，状态栏显示 Recording...
```

第二次点击：

```text
recording != null
  ↓
recording.stop()
  ↓
VideoRecordEvent.Finalize
  ├── 成功 → Toast + 状态栏显示视频 URI
  └── 失败 → Log.e + 状态栏显示错误
  ↓
按钮恢复 START CAPTURE
```

视频通过 MediaStore 写入系统视频库。

## 8. ImageAnalysis 亮度分析流程

`LuminosityAnalyzer` 接收实时帧：

```text
analyze(image: ImageProxy)
  ↓
读取 image.planes[0].buffer
  ↓
ByteBuffer 转 ByteArray
  ↓
把每个字节转成 0..255 的亮度值
  ↓
计算平均值
  ↓
更新 UI：Average luminosity
  ↓
Logcat 输出 Average luminosity
  ↓
finally { image.close() }
```

`image.close()` 必须执行，否则后续帧会被阻塞。

## 9. 资源释放流程

Activity 销毁时执行：

```kotlin
override fun onDestroy() {
    super.onDestroy()
    recording?.close()
    cameraExecutor.shutdown()
}
```

CameraX 的 Use Case 绑定在生命周期上，页面销毁时底层相机资源会随生命周期释放。额外关闭 `cameraExecutor` 是为了释放图像分析后台线程。

## 10. 常见错误与排查

| 问题 | 原因 | 解决方式 |
|---|---|---|
| Windows 中文路径构建失败 | AGP 默认检查非 ASCII 路径 | 在项目 `gradle.properties` 中加入 `android.overridePathCheck=true` |
| CameraX 1.6.1 与 minSdk 21 冲突 | `camera-camera2-pipe:1.6.1` 要求 minSdk 23 | 改用兼容 minSdk 21 的稳定版 CameraX 1.4.2 |
| 授权前相机打不开 | 缺少 `CAMERA` 或 `RECORD_AUDIO` 权限 | 使用运行时权限申请，通过后再 `startCamera()` |
| 绑定四个 Use Case 失败 | 设备不支持该组合 | catch 异常并 fallback 到不含 ImageAnalysis 的组合 |
| 亮度分析卡住 | `ImageProxy` 未关闭 | 在 `finally` 中调用 `image.close()` |
| 模拟器预览黑屏 | Virtual Scene 尚未初始化或摄像头延迟启动 | 等待几秒或重启 App，确认模拟器启用了虚拟摄像头 |
