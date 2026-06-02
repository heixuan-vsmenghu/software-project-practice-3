# E4 模型替换记录

| 项目 | 内容 |
|---|---|
| 替换时间 | 2026-06-03 01:28 |
| E4 工程 | `E4_Intelligent_Image_Classification_App/TFLClassify/start` |
| 原始模型路径 | `E4_Intelligent_Image_Classification_App/TFLClassify/start/src/main/ml/FlowerModel.tflite` |
| 原始模型大小 | 13,508,269 bytes |
| 原始模型备份 | `E5_1_TensorFlow_Model_Generation/android_integration/backup/FlowerModel_E4_original.tflite` |
| E5 新模型 | `E5_1_TensorFlow_Model_Generation/models/FlowerModel_E5.tflite` |
| E5 新模型大小 | 1,628,420 bytes |
| E4 替换后模型 | `E4_Intelligent_Image_Classification_App/TFLClassify/start/src/main/ml/FlowerModel.tflite` |
| 标签文件 | `E4_Intelligent_Image_Classification_App/TFLClassify/start/src/main/assets/labels.txt` |
| 是否修改 E4 推理代码 | 是 |
| 是否修改标签读取逻辑 | 是 |
| 构建结果 | `:start:assembleDebug` 成功 |
| APK | `E4_Intelligent_Image_Classification_App/TFLClassify/start/build/outputs/apk/debug/start-debug.apk` |
| Android 验证 | Pixel_8 模拟器启动、CameraX 预览、Logcat 推理成功 |
| 验证截图 | `images/e4_android_model_verification.png`, `images/e4_self_trained_model_result.png` |
| 推理日志 | `images/e4_logcat_inference_result.txt` |

## 修改说明

原始 E4 使用 ML Model Binding 读取带 metadata 的示例模型。E5 自训练模型没有相同 metadata，因此本次改为 TensorFlow Lite `Interpreter`：

```text
CameraX ImageProxy
  -> Bitmap
  -> 224 x 224 RGB Float ByteBuffer
  -> Interpreter.run()
  -> FloatArray softmax
  -> labels.txt 映射
  -> Recognition(label, score)
  -> RecyclerView / Logcat
```
