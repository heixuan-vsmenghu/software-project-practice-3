# E5 模型接入 E4 Android App 指南

## 1. E4 原始 App

E4 Android 工程路径：

```text
E4_Intelligent_Image_Classification_App/TFLClassify/
```

本次接入使用已经完成的 `start` 模块：

```text
E4_Intelligent_Image_Classification_App/TFLClassify/start/
```

E4 原始模型位于：

```text
E4_Intelligent_Image_Classification_App/TFLClassify/start/src/main/ml/FlowerModel.tflite
```

## 2. E5 生成模型

E5 训练与转换后生成：

```text
E5_1_TensorFlow_Model_Generation/models/FlowerModel_E5.tflite
E5_1_TensorFlow_Model_Generation/models/labels.txt
```

标签顺序为：

```text
daisy
dandelion
roses
sunflowers
tulips
```

## 3. 备份与替换

原始 E4 模型已备份到：

```text
E5_1_TensorFlow_Model_Generation/android_integration/backup/FlowerModel_E4_original.tflite
```

E5 模型已复制并替换为：

```text
E4_Intelligent_Image_Classification_App/TFLClassify/start/src/main/ml/FlowerModel.tflite
```

`labels.txt` 已复制到：

```text
E4_Intelligent_Image_Classification_App/TFLClassify/start/src/main/assets/labels.txt
```

## 4. 为什么改用 Interpreter

E4 原始代码使用 ML Model Binding：

```kotlin
FlowerModel.process(tfImage).probabilityAsCategoryList
```

E5 自训练模型没有原始示例模型的 metadata，继续依赖 `probabilityAsCategoryList` 可能导致生成类结构变化或构建失败。因此本次 Android 侧改为：

1. 从 asset 加载 `FlowerModel.tflite`。
2. 从 `assets/labels.txt` 读取标签。
3. 将 CameraX 图像缩放为 `224 x 224`。
4. 按 float RGB 写入 `ByteBuffer`。
5. 使用 `Interpreter.run(input, output)` 执行推理。
6. 手动将 softmax 输出映射成 `Recognition(label, score)`。
7. 按 score 降序取 Top-3 显示。

## 5. 构建命令

```powershell
cd E4_Intelligent_Image_Classification_App/TFLClassify
$env:JAVA_HOME='E:\development\Java\jdk11'
$env:Path="$env:JAVA_HOME\bin;$env:Path"
$env:ANDROID_SDK_HOME='C:\Temp\codex-android-home'
$env:ANDROID_USER_HOME='C:\Temp\codex-android-home\.android'
.\gradlew.bat --no-daemon :start:assembleDebug
```

构建结果：成功。

APK 路径：

```text
E4_Intelligent_Image_Classification_App/TFLClassify/start/build/outputs/apk/debug/start-debug.apk
```

## 6. Android 验证

已使用 `Pixel_8` 模拟器安装并启动 App。模拟器 CameraX 预览正常，Logcat 中持续输出 E5 模型的 Top-3 推理结果，例如：

```text
roses / 40.9%, daisy / 40.8%, tulips / 13.1%
daisy / 49.0%, roses / 30.0%, tulips / 14.8%
```

由于模拟器摄像头画面不是真实花卉图片，本次 Android 截图用于证明 App 启动、CameraX 预览和模型推理链路工作；真实花卉实拍效果仍建议连接真机后补充。
