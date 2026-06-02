# Android Patch Notes

## 修改文件

```text
E4_Intelligent_Image_Classification_App/TFLClassify/start/build.gradle
E4_Intelligent_Image_Classification_App/TFLClassify/start/src/main/java/org/tensorflow/lite/examples/classification/MainActivity.kt
E4_Intelligent_Image_Classification_App/TFLClassify/start/src/main/ml/FlowerModel.tflite
E4_Intelligent_Image_Classification_App/TFLClassify/start/src/main/assets/labels.txt
```

## 代码改动

- 增加 `org.tensorflow:tensorflow-lite:2.3.0` 直接依赖。
- 移除对生成类 `FlowerModel`、`TensorImage` 和 ML Model Binding category 输出的依赖。
- 增加 `Interpreter` 加载逻辑。
- 增加 `labels.txt` 读取逻辑。
- 增加 `Bitmap -> ByteBuffer` 输入转换逻辑。
- 手动将输出概率数组映射为 `Recognition(label, confidence)`。
- 保留原有 CameraX、ViewModel、LiveData、RecyclerView 展示链路。

## 构建问题与处理

第一次构建时同时在 `src/main/ml/FlowerModel.tflite` 和 `src/main/assets/FlowerModel.tflite` 放置同名模型，AGP 自动将 `ml` 模型合并到 assets，导致 `Duplicate resources`。处理方式：

```text
删除 start/src/main/assets/FlowerModel.tflite
保留 start/src/main/ml/FlowerModel.tflite
保留 start/src/main/assets/labels.txt
```

随后执行：

```powershell
.\gradlew.bat --no-daemon :start:assembleDebug
```

构建成功。

## 验证结果

Pixel_8 模拟器已安装并启动 App。Logcat 显示 E5 标签推理结果：

```text
Inference time: 1269ms; results: roses / 40.9%, daisy / 40.8%, tulips / 13.1%
Inference time: 1537ms; results: daisy / 49.0%, roses / 30.0%, tulips / 14.8%
```

说明 E5 自训练 TFLite 模型已被 Android 端加载并执行推理。
