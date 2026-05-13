# ImageAnalysis 到 LiteRT / 移动 AI 的扩展计划

## 1. 当前 ImageAnalysis 做了什么

本实验中的 `ImageAnalysis` 已经能从 CameraX 获取实时视频帧。当前分析器 `LuminosityAnalyzer` 只读取 `ImageProxy` 的 Y 平面数据，计算平均亮度，然后把结果显示到页面并输出到 Logcat。

它还没有接入真实 AI 模型，也没有完成分类、检测或分割任务。

## 2. 为什么 ImageAnalysis 可以作为 AI 推理入口

移动 AI 相机应用的核心流程是：

```text
摄像头实时画面
  ↓
逐帧获取图像
  ↓
转换成模型输入
  ↓
LiteRT 推理
  ↓
把结果显示到 UI
```

CameraX 的 `ImageAnalysis` 正好解决“逐帧获取图像”这一步。它让 App 可以在预览继续运行的同时，把每一帧交给后台线程处理。

当前的亮度计算可以看作最小版本的实时推理：输入是相机帧，输出是一个数值。后续把“计算亮度”替换为“调用 LiteRT 模型”，就能升级成真实 AI 功能。

## 3. 后续接入 LiteRT 的大致步骤

1. 在 `ImageAnalysis.Analyzer.analyze(image: ImageProxy)` 中获取相机帧。
2. 将 `ImageProxy` 转换为 `Bitmap` 或模型需要的 `ByteBuffer`。
3. 根据模型输入尺寸进行 resize，例如 224 x 224 或 320 x 320。
4. 对像素进行 normalize，例如把 0..255 转换到 0..1 或 -1..1。
5. 加载 `.tflite` / LiteRT 模型文件。
6. 把输入 `ByteBuffer` 传入 LiteRT Interpreter。
7. 获取分类、检测框或分割结果。
8. 在主线程更新 UI，例如显示类别名称、置信度、检测框。
9. 始终在 `finally` 中调用 `image.close()`，保证下一帧能继续进入分析器。

## 4. 可扩展项目方向

| 方向 | 说明 |
|---|---|
| 垃圾分类 | 摄像头对准物体，模型判断可回收物、厨余垃圾、有害垃圾等类别 |
| 植物识别 | 对叶片或花朵进行拍摄，识别植物种类 |
| 食物识别 | 识别餐盘中的食物，为健康记录或热量估算做准备 |
| 手势识别 | 识别手势动作，用于无接触交互 |
| 物体检测 | 在画面中框出目标位置，例如人、瓶子、书本、电子设备 |

## 5. 当前实验的限制

当前实验只完成 CameraX 基础能力：

- 实时 Preview 预览
- ImageCapture 拍照
- VideoCapture 录像
- ImageAnalysis 平均亮度分析
- Android 运行时权限
- MediaStore 保存媒体文件

当前没有接入真实 LiteRT 模型，也没有声称完成真实 AI 推理。

## 6. 后续计划

后续可以在 E3 / E4 / E5 中逐步完成：

1. 添加 LiteRT 依赖和模型文件。
2. 编写 `ImageProxy` 到模型输入的转换工具。
3. 在 `ImageAnalysis` 中调用模型推理。
4. 通过节流或跳帧控制推理频率，避免 UI 卡顿。
5. 在预览界面叠加分类结果或检测框。
6. 结合本实验的拍照和录像能力，保存 AI 分析结果。

本实验的价值在于先把相机数据入口打通，为后续移动 AI 项目铺好基础。
