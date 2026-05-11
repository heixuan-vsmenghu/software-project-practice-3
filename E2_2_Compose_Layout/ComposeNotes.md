# Compose 学习笔记

## 1. Jetpack Compose 是什么

Jetpack Compose 是 Android 官方推出的声明式 UI 框架。以前写 Android 界面通常要同时维护 XML 布局和 Activity / Fragment 代码，界面结构和状态逻辑分散在不同文件中。Compose 则直接用 Kotlin 函数描述界面，代码里写清楚“当前状态下界面应该长什么样”。

本实验的 `ComposeAiDemo` 就是一个最小 Compose Android 应用，入口在 `MainActivity.kt`。`MainActivity` 里通过 `setContent { ComposeAiDemoApp() }` 加载 Compose 界面。

## 2. 什么是声明式 UI

声明式 UI 的重点不是手动命令某个控件“改文字、改颜色、改可见性”，而是根据状态重新描述界面。

例如 AI Demo 页面里有一个状态对象：

```kotlin
data class AiRecognitionState(
    val modelName: String = "MobileNet",
    val result: String = "Waiting",
    val confidence: String? = null,
    val inferenceTimeMs: Int? = null,
    val inputSource: String = "等待输入",
)
```

点击“拍照识别”后，代码更新 `state`，`ResultCard(state)` 和 `PreviewBox(inputSource)` 会根据新状态自动显示 Cat、96.2%、28 ms 和“来自相机模拟输入”。

## 3. @Composable 的作用

`@Composable` 表示这个函数可以参与 Compose 界面绘制。普通 Kotlin 函数只负责计算或逻辑处理，Composable 函数负责声明 UI。

本实验中的主要 Composable 有：

- `ComposeAiDemoApp()`：应用整体入口，包含 `MaterialTheme`、`Scaffold` 和页面切换。
- `LayoutPracticeScreen()`：Compose 基础布局练习页面。
- `AiDemoScreen()`：面向 AI 应用的布局页面。
- `PreviewBox()`：相机或图片预览占位区。
- `ResultCard()`：AI 识别结果卡片。
- `ActionButtons()`：拍照、相册、切换模型、清空结果四个操作按钮。

## 4. Text、Button、Image、Card 的作用

`Text` 用来显示文字，例如页面标题、模型名称、识别结果。

`Button` 用来承载点击操作。本实验里“拍照识别”“相册导入”“切换模型”“清空结果”都是按钮，并且每个按钮都有实际状态变化。

`Image` 用来显示图片。本实验没有接入真实图片和相机流，所以暂时没有使用 `Image` 组件，而是用 `Box` 做预览区占位。后续接入相册图片或 CameraX 预览后，可以把图片内容放到这个区域。

`Card` 用来组织一组相关信息。本实验中 `PracticeCard()` 展示布局练习内容，`ResultCard()` 展示模型、结果、置信度和耗时。

## 5. Column、Row、Box 的区别

`Column` 纵向排列组件。`LayoutPracticeScreen()` 和 `AiDemoScreen()` 都用 Column 从上到下组织标题、预览区、结果区和按钮区。

`Row` 横向排列组件。页面切换按钮、结果行、按钮区的两列按钮都用了 Row。

`Box` 适合做叠放或占位。本实验的预览区用 Box 画出灰色圆角区域，文字居中显示 `Image / Camera Preview` 和当前输入来源。

## 6. Modifier 的作用

`Modifier` 用来描述组件的尺寸、间距、背景、圆角、对齐方式等。比如：

```kotlin
Modifier
    .fillMaxWidth()
    .height(210.dp)
    .clip(RoundedCornerShape(8.dp))
    .background(Color(0xFFCBD5E1))
```

这段代码把预览区设置为全宽、高度 210dp、8dp 圆角、灰色背景。

## 7. Scaffold 和 TopAppBar 的作用

`Scaffold` 是 Material Design 中常用的页面脚手架，可以统一管理顶部栏、内容区、底部栏等结构。本实验在 `ComposeAiDemoApp()` 中使用 Scaffold。

`TopAppBar` 是顶部栏。布局练习页显示“Compose 布局实验”，AI 页面显示“LiteRT AI Demo”，符合课件中对 AI 应用顶部区域的要求。

## 8. remember 和 mutableStateOf 的作用

`remember` 用来在重组之间保存状态，`mutableStateOf` 创建可观察状态。当状态变化时，依赖它的 Composable 会自动更新。

本实验中：

- `selectedScreen` 控制当前显示“布局练习”还是“AI Demo”。
- `showGuide` 控制布局说明是否显示。
- `expanded` 控制每个练习卡片是否展开。
- `state` 保存 AI Demo 的模型、结果、置信度、耗时和输入来源。

## 9. 状态驱动 UI

AI Demo 页面没有直接去修改某一个 Text，而是更新 `AiRecognitionState`。界面展示时再统一读取状态：

```kotlin
val confidenceText = state.confidence ?: "--"
val timeText = state.inferenceTimeMs?.let { "$it ms" } ?: "--"
```

这里使用了 Kotlin 空安全。没有结果时显示 `--`，有耗时时显示字符串模板生成的 `28 ms`、`35 ms`。

## 10. Recomposition 是什么

Recomposition 指状态改变后，Compose 自动重新执行受影响的 Composable，并刷新界面。点击“相册导入”后，`state` 从 Waiting 变为 Dog，Compose 只需要根据新状态重组相关区域，不需要手动查找控件。

## 11. 为什么 AI 应用原型适合先用 Compose 搭界面

AI 应用通常有固定的交互结构：输入区、模型选择、推理结果、操作按钮。真实 CameraX 和 LiteRT 接入前，先用 Compose 把布局和状态流转搭出来，可以提前验证操作路径是否清楚。

本实验的预览区只是 Box 占位，识别结果是模拟数据。后续可以把 Box 替换成 CameraX 预览，把 `AiRecognitionState` 的数据来源替换成 LiteRT 模型推理结果，页面结构仍然可以继续使用。

## 12. 本实验对应课件要求的位置

- 首个 Kotlin APP：`ComposeAiDemo/` 是完整 Android Kotlin Compose 工程。
- Compose 基础布局：`LayoutPracticeScreen()` 使用 Column、Row、Box、Text、Button、Card。
- 面向 AI 应用布局：`AiDemoScreen()` 包含顶部栏、预览区、结果区和按钮区。
- 状态交互：四个按钮通过 Lambda 更新 `AiRecognitionState`。
- Kotlin 特性：代码中使用 data class、val / var、默认参数、字符串模板、可空字段、when、List、forEach 和 Lambda。
