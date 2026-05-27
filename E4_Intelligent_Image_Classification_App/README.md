# 实验 4：实现智能图像分类 APP

## 一、实验目标

本实验基于 `hoitab/TFLClassify` 教程工程，在 `start` 模块中补全 TensorFlow Lite 花卉图像分类应用。目标是让 Android App 通过 CameraX 获取实时画面，用 `FlowerModel.tflite` 执行端侧推理，并把 Top-K 分类结果显示到 RecyclerView。

## 二、实验环境

| 项目 | 实际情况 |
|---|---|
| 课程仓库 | `software-project-practice-3` |
| 实验目录 | `E4_Intelligent_Image_Classification_App/` |
| Android 工程 | `E4_Intelligent_Image_Classification_App/TFLClassify/` |
| 主要语言 | Kotlin |
| 核心技术 | CameraX、TensorFlow Lite / LiteRT、ML Model Binding、ViewModel、LiveData、RecyclerView、Data Binding |
| 构建验证 | Windows PowerShell + Gradle Wrapper |
| JDK | JDK 11 用于旧 Gradle/AGP 构建 |
| 运行验证 | 当前自动环境无 Android 真机，已用 Pixel_8 模拟器验证权限、预览、推理与结果显示 |

## 三、实验内容与完成情况

| 老师要求 | 本项目完成情况 |
|---|---|
| 构建基于 TensorFlow Lite 的 Android 花卉识别应用 | 已基于 TFLClassify `start` 模块完成花卉识别 App |
| 查看代码框架 | 已分析 CameraX、ImageAnalyzer、ViewModel、LiveData、Adapter |
| 注意 CameraX 库使用 | 已说明 `androidx.camera.*` 在预览和图像分析中的作用 |
| 注意数据视图模型使用 | 已说明 RecognitionViewModel / LiveData 如何驱动 UI |
| 下载代码或 git clone | 已 clone TFLClassify 并纳入 E4 实验目录，已移除内层 `.git` |
| 完成 TODO 代码项 | 已完成 TODO 1-6 并删除 Fake label 占位结果 |
| 导入 FlowerModel.tflite | 已从 `finish/src/main/ml` 导入到 `start/src/main/ml` 并开启模型绑定 |
| 真机运行花卉识别应用 | 当前自动环境无真机；已在 Pixel_8 模拟器完成权限、预览、推理、Top-K 显示验证，真机验证待连接设备 |
| 上传 GitHub | 本轮完成后提交并 push 到课程仓库 |
| 撰写详细 README | 已完成，并补充新解析课件内容 |

## 四、项目结构

```text
E4_Intelligent_Image_Classification_App/
├── README.md
├── TFLiteImageClassificationNotes.md
├── docs/
│   ├── architecture_analysis.md
│   ├── code_flow.md
│   ├── model_info.md
│   ├── new_ppt_analysis.md
│   ├── problems_and_solutions.md
│   └── todo_implementation.md
├── images/
└── TFLClassify/
    ├── start/
    └── finish/
```

## 五、核心知识点

- CameraX `Preview` 只负责把摄像头画面显示到 `PreviewView`。
- CameraX `ImageAnalysis` 才负责拿到每一帧 `ImageProxy` 并触发模型推理。
- `YuvToRgbConverter` / `toBitmap()` 将相机帧从 YUV 转为 Bitmap，并处理旋转方向。
- `TensorImage.fromBitmap(...)` 将 Bitmap 包装成 TFLite Support Library 可处理的模型输入。
- `FlowerModel.process(tfImage)` 调用 ML Model Binding 生成的模型类完成推理。
- `probabilityAsCategoryList` 输出 label 与 score，按 score 降序排序后取 Top-K。
- `RecognitionViewModel` 通过 LiveData 保存识别结果，UI 观察数据变化。
- `RecognitionAdapter` 使用 RecyclerView + Data Binding 将 label 和 confidence 显示在屏幕上。

## 六、TFLClassify 项目说明

本实验使用的教程工程来自 [hoitab/TFLClassify](https://github.com/hoitab/TFLClassify)。工程包含两个模块：

| 模块 | 作用 |
|---|---|
| `start` | 实验起点，原始代码保留 TODO 和 Fake label，占位结果不能作为最终成果 |
| `finish` | 参考答案和模型来源，只用于对照阅读，最终运行目标是完成后的 `start` 模块 |

## 七、FlowerModel.tflite 模型说明

模型文件位于：

```text
TFLClassify/start/src/main/ml/FlowerModel.tflite
```

它来自：

```text
TFLClassify/finish/src/main/ml/FlowerModel.tflite
```

本实验没有重新训练模型，而是导入已有的 TensorFlow Lite 花卉分类模型，并通过 Android Studio ML Model Binding 生成 `FlowerModel` 调用类。

## 八、TODO 实现说明

| TODO | 位置 | 实现内容 | 作用 |
|---|---|---|---|
| TODO 1 | `MainActivity.kt` / `ImageAnalyzer` | 添加 `FlowerModel` 对象 | 让 App 能调用模型 |
| TODO 2 | `analyze()` | `ImageProxy -> Bitmap -> TensorImage` | 把摄像头画面变成模型输入 |
| TODO 3 | `analyze()` | `process + sortByDescending + take(MAX_RESULT_DISPLAY)` | 得到置信度最高的识别结果 |
| TODO 4 | `analyze()` | 输出转 `Recognition(label, score)` | 让 UI 能显示结果 |
| TODO 5 | `start/build.gradle` | 添加 TFLite GPU delegate 依赖 | 支持可选硬件加速 |
| TODO 6 | `ImageAnalyzer` | GPU delegate / CPU fallback | 兼顾推理速度与设备兼容 |

Fake label 占位代码已删除，运行结果来自 `FlowerModel.process(tfImage)` 的真实模型输出。

## 九、代码运行流程

```text
onCreate()
  ↓
申请 CAMERA 权限
  ↓
startCamera()
  ↓
Preview 显示摄像头画面
  ↓
ImageAnalysis 接收 ImageProxy
  ↓
YuvToRgbConverter / toBitmap()
  ↓
TensorImage.fromBitmap(...)
  ↓
FlowerModel.process(tfImage)
  ↓
probabilityAsCategoryList
  ↓
sortByDescending(score).take(MAX_RESULT_DISPLAY)
  ↓
Recognition(label, score)
  ↓
RecognitionViewModel / LiveData
  ↓
RecognitionAdapter / RecyclerView
  ↓
屏幕显示花卉识别结果
```

`imageProxy.close()` 已放在 `finally` 中，确保推理成功或失败都释放当前帧，避免 CameraX 后续帧阻塞。

## 十、运行与构建方法

旧教程项目使用 Gradle 6.5 和 Android Gradle Plugin 4.1.0-rc03。当前机器默认 JDK 21 与旧 Gradle 不兼容，因此命令行构建使用 JDK 11：

```powershell
cd E4_Intelligent_Image_Classification_App/TFLClassify
$env:JAVA_HOME='E:\development\Java\jdk11'
$env:Path="$env:JAVA_HOME\bin;$env:Path"
$env:ANDROID_SDK_HOME='C:\Temp\codex-android-home'
$env:ANDROID_USER_HOME='C:\Temp\codex-android-home\.android'
.\gradlew.bat --no-daemon :start:assembleDebug
```

构建结果：`BUILD SUCCESSFUL`，APK 生成于：

```text
TFLClassify/start/build/outputs/apk/debug/start-debug.apk
```

## 十一、运行结果截图

以下均为本次任务中真实获取的截图或输出渲染图；未获取到的真机花卉实拍截图不在 README 中引用。

![上游项目仓库](images/upstream_repository.png)

![项目克隆与目录检查](images/project_cloned.png)

![start 和 finish 模块](images/modules_start_finish.png)

![模型来源与导入](images/flower_model_imported.png)

![TODO 代码实现](images/todo_3_process_sort_topk.png)

![imageProxy.close 检查](images/image_proxy_close_checked.png)

![dataBinding 与 mlModelBinding 检查](images/databinding_mlmodelbinding_checked.png)

![ViewModel 与 LiveData 检查](images/viewmodel_livedata_checked.png)

![RecognitionAdapter 检查](images/recognition_adapter_checked.png)

![Gradle 配置与构建验证](images/gradle_sync_success.png)

![构建成功](images/build_success.png)

![设备检测](images/device_detected.png)

![摄像头权限请求](images/permission_request.png)

![CameraX 预览与推理结果](images/app_camera_preview.png)

![模拟器识别结果](images/flower_recognition_daisy_or_other.png)

![Logcat 推理结果](images/logcat_inference_result.png)

![App 最终效果](images/final_app_overview.png)

![GitHub 提交记录](images/github_commit_history.png)

## 新增解析课件补充说明

老师新发的 `10_TFLClassify_智能图像分类APP_解析.pdf` 是实验 4 的解析补充，不是新实验。本项目已根据新 PPT 补充 CameraX、TFLite、ViewModel、LiveData、RecyclerView 的运行链路说明，并检查了代码实现。

| 新解析 PPT 关注点 | 本项目落实情况 |
|---|---|
| 摄像头实时画面输入 | 已通过 CameraX Preview 显示 |
| CameraX 帧分析 | 已通过 ImageAnalysis 获取 ImageProxy |
| TensorImage 转换 | 已将 Bitmap 转为 TensorImage |
| TFLite 模型推理 | 已调用 `FlowerModel.process(tfImage)` |
| Top-3 分类结果 | 已按 score 降序取 `MAX_RESULT_DISPLAY` 个结果 |
| RecyclerView 展示 | 已通过 RecognitionAdapter 显示结果 |
| ViewModel / LiveData | 已通过 RecognitionViewModel 管理识别结果 |
| Data Binding | 已开启并用于结果项绑定 |
| ML Model Binding | 已开启并生成 FlowerModel 调用代码 |
| `imageProxy.close()` | 已在 `finally` 中确保释放 |

补充文档见 [docs/new_ppt_analysis.md](docs/new_ppt_analysis.md)。

![新解析 PPT 已纳入文档](images/new_ppt_added_to_docs.png)

![新 PPT 标准流水线](images/code_flow_from_new_ppt.png)

![问题排查表补充](images/troubleshooting_table_added.png)

## 十二、遇到的问题与解决方法

| 问题 | 原因 | 解决方法 |
|---|---|---|
| JDK 21 构建失败 | Gradle 6.5 / Groovy 不支持 Java 21 class file | 构建时切换到 JDK 11 |
| 中文路径被旧 AGP 拦截 | Android Gradle Plugin 4.1 在 Windows 上默认检查非 ASCII 路径 | 在 `gradle.properties` 增加 `android.overridePathCheck=true` |
| 找不到 TFLite support rc 依赖 | Maven 仓库中没有 `tensorflow-lite-support:0.1.0-rc1` | 增加 `mavenCentral()`，并使用可解析的 `0.1.0` |
| Debug keystore 读取失败 | 原 keystore 由较新 JDK 生成，JDK 11 无法读取 HmacPBESHA256 | 命令行构建使用临时 Android user home 生成兼容 debug keystore |
| 当前环境无真机 | `adb devices` 没有列出物理设备 | 使用 Pixel_8 模拟器补充验证，README 如实说明真机待验证 |

## 十三、与 E5 / 期末移动 AI 项目的关系

本实验重点是“已有 TFLite 模型在 Android 端如何接入和显示结果”。后续 E5 可以替换 `FlowerModel.tflite` 为自己训练或转换得到的 LiteRT/TensorFlow Lite 模型，Android 侧的 CameraX、TensorImage、ViewModel、LiveData 和 RecyclerView 流水线可以复用。

## 十四、实验总结

本实验完成了从相机实时画面到模型推理再到 UI 可视化的完整 Android 端图像分类链路。核心收获是区分 CameraX Preview 与 ImageAnalysis 的职责，理解 ML Model Binding 如何降低调用 `.tflite` 模型的复杂度，以及 ViewModel / LiveData / RecyclerView 如何让高频推理结果稳定显示到界面。

## 十五、参考资料

- [TFLClassify GitHub 仓库](https://github.com/hoitab/TFLClassify)
- `9_实验4_实现智能图像分类APP.pdf`
- `10_TFLClassify_智能图像分类APP_解析.pdf`
- Android CameraX、LiveData、Data Binding、TensorFlow Lite / LiteRT 官方文档
