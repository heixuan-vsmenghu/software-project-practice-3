# TODO 实现记录

| TODO | 位置 | 实现内容 | 作用 | 截图 |
|---|---|---|---|---|
| TODO 1 | `MainActivity.kt` / `ImageAnalyzer` | 添加 `FlowerModel` 对象，使用 lazy 初始化 | 让 App 能调用模型 | `images/todo_1_model_variable.png` |
| TODO 2 | `analyze()` | `ImageProxy -> Bitmap -> TensorImage` | 把摄像头画面变成模型输入 | `images/todo_2_tensor_image.png` |
| TODO 3 | `analyze()` | `process + sortByDescending + take(MAX_RESULT_DISPLAY)` | 得到概率最高的识别结果 | `images/todo_3_process_sort_topk.png` |
| TODO 4 | `analyze()` | 输出转 `Recognition` | 让 UI 能显示结果 | `images/todo_4_recognition_mapping.png` |
| TODO 5 | `start/build.gradle` | 添加 TFLite GPU delegate 依赖 | 支持可选硬件加速 | `images/todo_5_gpu_dependency.png` |
| TODO 6 | `ImageAnalyzer` | GPU delegate / CPU fallback | 提高推理速度并保证兼容 | `images/todo_6_gpu_delegate.png` |

## Fake label 删除

原始 `start` 模块中的占位代码会添加 `Recognition("Fake label $i", Random.nextFloat())`。本实验已删除该逻辑，当前界面数据来自 `FlowerModel.process(tfImage)` 的模型输出。

## imageProxy.close()

`imageProxy.close()` 已放入 `finally`，确保成功推理、空图像、异常场景都会释放当前帧。
