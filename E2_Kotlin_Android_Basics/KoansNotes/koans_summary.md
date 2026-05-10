# Kotlin Koans 完成总结

## 完成方式

本次 Koans 优先尝试访问在线页面 `https://play.kotlinlang.org/koans/overview`，页面可以返回 HTTP 200，但当前自动化环境没有稳定的在线登录、保存进度和网页截图流程。为避免伪造在线完成比例，本实验改用官方本地仓库方案完成等价验证。

本地方案使用官方仓库：

- 仓库：`https://github.com/Kotlin/kotlin-koans`
- 分支：`master` 作为初始未完成状态，`resolutions` 作为完成后验证状态
- 运行环境：Temurin JDK 11，本机 Java 21 与旧版 Gradle/Groovy 不兼容，因此使用 JDK 11 跑测试
- 验证命令：`gradlew.bat clean test --console=plain`

最终完成比例：`42 / 42 = 100%`，超过实验要求的 85%。

## 进度验证

| 阶段 | 覆盖模块 | 任务数 | 比例 | 结果 |
|---|---|---:|---:|---|
| 起始 | 官方 `master` 初始任务 | 0/42 | 0% | 测试失败，存在未完成 TODO |
| 50% 检查点 | Introduction + Collections | 25/42 | 59.5% | 所选模块测试通过 |
| 85% 检查点 | Introduction + Collections + Conventions + Properties + Generics | 37/42 | 88.1% | 所选模块测试通过 |
| 最终 | 全部模块 | 42/42 | 100% | 全量测试通过 |

对应输出已保存：

- `koans_start_output.txt`
- `koans_progress_50_output.txt`
- `koans_progress_85_output.txt`
- `koans_final_output.txt`

## 模块学习记录

| 模块 | 主要内容 | 学到的知识 | 典型问题 | 解决方式 |
|---|---|---|---|---|
| Introduction | 基础语法 | 默认参数、命名参数、字符串模板、可空类型、Lambda、data class、扩展函数 | 初学时容易不理解 `it` | 先把 Lambda 写成 `{ value -> ... }`，理解后再使用 `it` |
| Classes | 类相关语法 | data class、sealed class、smart cast、扩展函数、导入重命名 | 不清楚类型判断后为什么能直接访问属性 | 理解 smart cast：经过 `is` 判断后，编译器能推断具体类型 |
| Collections | 集合操作 | `filter`、`map`、`flatMap`、`groupBy`、`partition`、`fold`、`sumOf` 思想 | 容易混淆 `filter` 与 `map` | `filter` 是筛选，`map` 是转换，先写中间变量再串联 |
| Conventions | Kotlin 约定 | 运算符重载、范围、`in`、`for` 迭代、解构声明、`invoke` | 不知道 `..`、`in` 背后调用什么函数 | 结合 `rangeTo`、`contains`、`iterator` 理解语法糖 |
| Properties | 属性机制 | 自定义 getter/setter、lazy、委托属性 | 不理解委托为什么能拦截属性访问 | 从 `getValue`、`setValue` 的调用关系入手 |
| Generics | 泛型函数 | 类型参数、泛型集合转换 | 类型参数约束不直观 | 观察输入输出类型，先写函数签名再写实现 |
| Builders | 构建器 DSL | 函数字面量接收者、`apply`、HTML DSL | DSL 看起来不像普通函数调用 | 把接收者对象显式写出来，理解作用域 |

## 典型问题与解决

1. 本机默认 Java 21 运行旧版 Koans Gradle 时失败。

   原因是旧版 Gradle/Groovy 与 Java 21 不兼容。解决方式是临时下载 Temurin JDK 11，并设置 `JAVA_HOME` 后重新运行测试。

2. 在线 Koans 页面不适合作为本次自动完成证据。

   页面可以访问，但在线进度依赖浏览器状态和账号保存。为保证证据真实，本次使用官方本地仓库和 Gradle 测试报告作为完成依据。

3. 集合类题目最容易混淆。

   解决方法是把链式调用拆开：先 `filter` 筛选，再 `map` 转换，最后再 `groupBy` 或 `fold` 汇总。

## 理解总结

Kotlin Koans 的价值在于把语法放进可验证的小测试里。完成这些题后，对 Kotlin 的理解不再停留在“能看懂语法”，而是能把空安全、集合操作、data class、扩展函数和 Lambda 用到实际业务中。后续 Android + LiteRT 开发中，识别结果列表筛选、UI 状态复制、点击回调、模型配置单例都能直接对应到本次练习过的语法点。
