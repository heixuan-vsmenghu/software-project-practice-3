# Kotlin 基础语法学习笔记

## 1. Kotlin 简介

Kotlin 是 JetBrains 设计的现代静态类型语言，也是 Android 官方推荐语言。它运行在 JVM 上，可以和 Java 生态互操作，同时提供更简洁的语法、空安全、Lambda、高阶函数、data class 等特性。对本课程后续的 Android + LiteRT 移动 AI 开发来说，Kotlin 主要承担应用层业务逻辑、UI 状态建模、模型推理结果处理和事件回调编写。

最小程序：

```kotlin
fun main() {
    val language = "Kotlin"
    println("Hello, $language")
}
```

## 2. val 与 var

- `val` 表示只读引用，赋值后不能重新指向另一个对象。Android 中常用于不需要变化的配置、模型名称、一次推理得到的结果列表。
- `var` 表示可变引用，可以重新赋值。Android 中常用于确实会变化的临时状态，例如计数器、加载状态、调试变量。

建议优先使用 `val`，只有状态确实需要变化时再使用 `var`，这样代码更容易推理，也更接近 Compose 和 ViewModel 中常见的不可变状态思想。

```kotlin
val modelName = "mobilenet_v1_litert.tflite"
var inferenceCount = 0
inferenceCount += 1
```

## 3. 基础类型

常见基础类型包括：

| 类型 | 说明 | Android 场景 |
|---|---|---|
| `Int` | 整数 | 列表下标、图片宽高、检测框坐标 |
| `Long` | 长整数 | 时间戳、文件大小 |
| `Float` | 单精度小数 | LiteRT 置信度、阈值 |
| `Double` | 双精度小数 | 更高精度的计算 |
| `Boolean` | 布尔值 | 是否加载中、权限是否授权 |
| `Char` | 字符 | 单个字符处理 |
| `String` | 字符串 | 页面标题、Intent 参数、模型标签 |

## 4. 类型推断

Kotlin 能根据右侧表达式推断类型：

```kotlin
val appName = "AI Camera"       // String
val threshold = 0.6f            // Float
val count = 3                   // Int
```

在复杂返回值、公共 API、容易误解的数字类型中，建议显式写出类型：

```kotlin
val confidence: Float = 0.91f
val results: List<RecognitionResult> = emptyList()
```

## 5. 字符串模板

Kotlin 用 `$name` 插入变量，用 `${expression}` 插入表达式：

```kotlin
val label = "cat"
val confidence = 0.94f
println("label=$label, percent=${confidence * 100}%")
```

Android 中常用于日志、调试输出、UI 文案拼接，例如显示“识别到 3 个结果”。

## 6. Null Safety

Kotlin 默认变量不可为 `null`：

```kotlin
val title: String = "Kotlin"
// val bad: String = null // 编译错误
```

如果变量可能为空，需要写成可空类型：

```kotlin
val imagePath: String? = intent.getStringExtra("image_path")
```

常用空安全语法：

| 语法 | 含义 | Android 场景 |
|---|---|---|
| `String?` | 字符串可能为空 | Intent 参数、网络返回字段 |
| `?.` | 安全调用 | `binding?.textView?.text` |
| `?:` | Elvis 默认值 | 网络字段为空时给默认显示 |
| `let` | 非空时执行代码块 | 只有 URI 不为空时加载图片 |

示例：

```kotlin
val displayName = userName ?: "Guest"
imagePath?.let { path ->
    println("Load image from $path")
}
```

应避免滥用 `!!`。`!!` 会强制断言非空，一旦判断错误仍会抛出空指针异常。更好的做法是用安全调用、默认值或提前返回。

## 7. if 与 when

Kotlin 的 `if` 可以作为表达式返回值：

```kotlin
val message = if (results.isEmpty()) {
    "No object detected"
} else {
    "Detected ${results.size} object(s)"
}
```

`when` 适合表达多分支状态：

```kotlin
val level = when {
    confidence >= 0.90f -> "high"
    confidence >= 0.75f -> "medium"
    confidence >= 0.60f -> "low"
    else -> "ignored"
}
```

Android 中，`when` 常用于 UI 状态、网络状态、权限结果、识别置信度分级。

## 8. 循环与区间

Kotlin 常用区间写法：

```kotlin
for (i in 1..5) println(i)              // 闭区间，包含 5
for (i in 0 until 3) println(i)         // 左闭右开，输出 0,1,2
for (i in 5 downTo 1 step 2) println(i) // 倒序步进
```

Android 中更多时候会遍历集合：

```kotlin
results.forEach { result ->
    println(result.label)
}
```

## 9. 函数、默认参数与命名参数

函数定义：

```kotlin
fun formatResult(label: String, confidence: Float): String {
    return "$label: $confidence"
}
```

表达式函数：

```kotlin
fun double(x: Int) = x * 2
```

默认参数和命名参数可以减少重载，提高调用点可读性：

```kotlin
fun predict(imagePath: String, threshold: Float = 0.6f, verbose: Boolean = false) {
    // run model
}

predict(imagePath = "sample.jpg", threshold = 0.75f)
```

## 10. Lambda 与高阶函数

Lambda 是可以当作值传递的函数：

```kotlin
val mapper: (String) -> Int = { input -> input.length }
```

接收函数作为参数的函数称为高阶函数：

```kotlin
fun renderResults(results: List<RecognitionResult>, renderer: (RecognitionResult) -> String) {
    results.forEach { println(renderer(it)) }
}
```

Android 常见对应关系：

- 按钮点击：`button.setOnClickListener { ... }`
- 回调：模型推理完成后调用 `onResult(results)`
- Compose 事件：`onClick = { viewModel.predict() }`
- 集合处理：`results.filter { it.confidence > 0.6f }`

## 11. 集合：List、Set、Map

| 集合 | 特点 | Android 场景 |
|---|---|---|
| `List` | 有序，可重复 | 识别结果列表、RecyclerView/Compose 列表 |
| `Set` | 去重 | 已识别标签集合、权限集合 |
| `Map` | 键值映射 | 标签英文到中文、状态码到文案 |

示例：

```kotlin
val labels = listOf("cat", "dog", "cat")
val uniqueLabels = labels.toSet()
val labelMap = mapOf("cat" to "Cat", "dog" to "Dog")
```

## 12. 集合操作：filter、map、forEach、groupBy

- `filter`：筛选元素，元素类型不变。
- `map`：转换元素，返回新列表。
- `forEach`：逐个处理元素，常用于打印、绑定 UI。
- `groupBy`：按条件分组。

```kotlin
val accepted = results.filter { it.confidence >= 0.6f }
val displayLabels = accepted.map { it.label.uppercase() }
accepted.forEach { println(it) }
val grouped = accepted.groupBy { it.label }
```

LiteRT 场景中，`filter` 用于过滤低置信度结果，`map` 用于把模型结果转成 UI 文案，`groupBy` 可用于按标签或置信度等级分组展示。

## 13. 类与对象

普通类用于描述状态和行为：

```kotlin
class ModelRunner(val modelName: String) {
    fun run(imagePath: String) {
        println("Run $modelName on $imagePath")
    }
}
```

Android 中 Activity、ViewModel、Repository、Adapter 都是类的典型应用。

## 14. data class

`data class` 适合纯数据建模，Kotlin 会自动生成 `toString`、`equals`、`hashCode`、`copy` 等方法：

```kotlin
data class RecognitionResult(
    val label: String,
    val confidence: Float
)

val result = RecognitionResult("cat", 0.94f)
val updated = result.copy(confidence = 0.96f)
```

Android 场景：

- UI 状态：`UiState`
- 网络返回：`ApiResponse`
- 数据库实体：`Entity`
- 模型输出：`RecognitionResult`

## 15. object

`object` 用于定义单例对象：

```kotlin
object AppConfig {
    const val MODEL_NAME = "mobilenet_v1_litert.tflite"
}
```

Android 中常用于全局配置、工具类、常量容器、单例管理器。

## 16. Kotlin 语法与 Android 开发场景对应关系

| Kotlin 语法 | Android / LiteRT 场景 |
|---|---|
| `val` | 保存模型文件名、固定阈值、一次推理结果 |
| `var` | 记录加载状态、调试计数 |
| `String?` | Intent 参数、网络字段、文件路径可能为空 |
| `?.` / `?:` | 处理 ViewBinding、接口返回、图片 URI |
| `if` / `when` | UI 状态切换、权限结果、置信度分级 |
| `for` / ranges | 批量处理帧、调试序号输出 |
| 默认参数 | 推理函数默认阈值、日志开关 |
| Lambda | 点击事件、异步回调、Compose 事件 |
| `List` / `filter` / `map` | 筛选识别结果并转换为 UI 数据 |
| `groupBy` | 按标签或置信度分组 |
| `data class` | 表示 `UiState`、识别结果、网络模型 |
| `object` | 保存 LiteRT 模型配置 |
| `copy` | 不直接修改 UI 状态，而是返回新状态 |

## 17. 初学者常见错误总结

| 常见错误 | 问题 | 建议 |
|---|---|---|
| 滥用 `var` | 状态变化过多，难调试 | 优先 `val` |
| 滥用 `!!` | 仍可能空指针崩溃 | 用 `?.`、`?:`、`let` |
| 分不清 `filter` 和 `map` | 筛选与转换混淆 | `filter` 保留元素，`map` 改造元素 |
| 忽略命名参数 | 调用点难读 | 参数多时使用 `name = value` |
| 只背语法不结合场景 | 写不出实际 Android 代码 | 用 UI 状态、模型结果、回调来练习 |
| 在 data class 中放大量业务逻辑 | 数据模型职责过重 | 复杂逻辑放到函数、Repository 或 ViewModel |

## 18. 本实验理解总结

Kotlin 的核心价值不只是“语法短”，而是让 Android 业务逻辑更安全、更清晰。空安全能减少崩溃，data class 让模型数据和 UI 状态更容易表达，集合函数让 LiteRT 识别结果筛选更自然，Lambda 和高阶函数则对应 Android 中大量事件与回调。掌握这些语法后，后续学习 Android + LiteRT 时，可以把重点放在模型推理流程和 UI 交互上，而不是被基础语言细节卡住。
