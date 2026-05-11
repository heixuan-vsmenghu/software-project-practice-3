# ComposeAiDemo 页面设计说明

## 1. 页面整体结构

本次应用是一个面向课程实验的 Compose 布局原型，包含两个页面：

- Compose 布局练习页面：用于证明已经实践基础布局组件。
- AI 应用布局页面：用于模拟移动端 AI 识别应用的主要界面。

应用入口是 `ComposeAiDemoApp()`。整体使用 `Scaffold` 组织顶部栏和内容区，内容区顶部用两个按钮切换页面。

## 2. Compose 布局练习页面说明

`LayoutPracticeScreen()` 主要练习 Compose 基础布局：

- 用 `Column` 纵向排列标题、卡片、预览占位区和说明按钮。
- 用 `Row` 排列卡片中的文字和 Show more 按钮。
- 用 `Box` 做预览占位区域，模拟后续图片或相机画面区域。
- 用 `Card` 展示 Hello World 和 Hello Compose 两张练习卡片。
- 用 `remember + mutableStateOf` 保存展开状态和说明显示状态。

这个页面不是简单的 Hello World，而是把多个基础组件组合成一个可交互页面。

## 3. AI 应用布局页面说明

`AiDemoScreen()` 按 AI 应用常见结构设计：

- 顶部栏：显示应用标题 `LiteRT AI Demo`。
- 预览区：显示图片或相机预览占位。
- 结果区：显示模型名称、识别结果、置信度和推理耗时。
- 按钮区：提供拍照识别、相册导入、切换模型、清空结果四种操作。

页面当前是布局原型，不接入真实 CameraX 和 LiteRT。所有识别结果来自模拟状态，方便先完成 Compose 布局和状态流转。

## 4. 顶部栏设计

顶部栏由 `Scaffold` 的 `topBar` 和 `TopAppBar` 实现。

布局练习页显示“Compose 布局实验”，AI 页面显示“LiteRT AI Demo”。右侧保留“说明”入口，点击后会切换到 AI Demo 页面，表示顶部栏可以承载页面操作。

## 5. 预览区设计

预览区由 `PreviewBox()` 实现，使用灰色圆角 `Box`：

- 初始状态显示“等待输入”。
- 点击“拍照识别”后显示“来自相机模拟输入”。
- 点击“相册导入”后显示“来自相册模拟输入”。
- 点击“清空结果”后恢复“等待输入”。

当前预览区只是 Box 占位，后续可以替换为 CameraX 相机预览。例如保留外层区域和标题，把内部内容换成 `PreviewView` 或 CameraX 与 Compose 的桥接视图。

## 6. 结果区设计

结果区由 `ResultCard()` 实现，使用 `Card + Column` 展示结构化信息：

- `Model: MobileNet`
- `Result: Cat`
- `Confidence: 96.2%`
- `Time: 28 ms`

这些字段来自 `AiRecognitionState`，不是直接写死在 UI 文本里。没有识别结果时，`confidence` 和 `inferenceTimeMs` 为可空字段，界面用 `?:` 和 `?.let {}` 显示 `--`。

## 7. 按钮区设计

按钮区由 `ActionButtons()` 实现，两行两列：

- 拍照识别：模拟相机输入，结果为 Cat，模型为 MobileNet。
- 相册导入：模拟相册输入，结果为 Dog，模型为 EfficientNet。
- 切换模型：在 MobileNet、EfficientNet、LiteRT Demo Model 之间循环。
- 清空结果：恢复 Waiting、`--` 和“等待输入”。

按钮的点击逻辑通过 Lambda 从 `ActionButtons()` 传入，按钮组件本身只负责触发事件。

## 8. 状态流转说明

初始状态：

```text
Model: MobileNet
Result: Waiting
Confidence: --
Time: --
Preview: 等待输入
```

拍照识别：

```text
Model: MobileNet
Result: Cat
Confidence: 96.2%
Time: 28 ms
Preview: 来自相机模拟输入
```

相册导入：

```text
Model: EfficientNet
Result: Dog
Confidence: 91.4%
Time: 35 ms
Preview: 来自相册模拟输入
```

切换模型：

```text
MobileNet -> EfficientNet -> LiteRT Demo Model -> MobileNet
```

清空结果：

```text
Model: MobileNet
Result: Waiting
Confidence: --
Time: --
Preview: 等待输入
```

## 9. 后续如何替换为 CameraX 和 LiteRT

后续接入 CameraX 时，可以保留 `PreviewBox()` 的位置，把内部占位文字替换为相机预览。拍照按钮不再写模拟状态，而是调用拍照或帧捕获逻辑。

后续接入 LiteRT 时，可以保留 `AiRecognitionState` 的结构，把 `result`、`confidence`、`inferenceTimeMs` 改为模型推理后的真实输出。这样 UI 层不用大改，只需要改变状态来源。

本次实验只完成 Compose 布局原型和模拟交互，没有声称已经完成真实相机采集或真实模型推理。
