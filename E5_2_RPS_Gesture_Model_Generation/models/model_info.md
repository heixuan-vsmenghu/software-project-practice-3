# 模型说明

| 项目 | 内容 |
|---|---|
| 模型名称 | `rps_classifier` |
| 任务类型 | 石头剪刀布手势图像分类 |
| 类别 | `rock`, `paper`, `scissors` |
| 实际标签顺序 | `paper, rock, scissors`，以 `labels.txt` 为准 |
| 输入尺寸 | 150 x 150 x 3 |
| 模型结构 | Keras Sequential CNN |
| 训练方式 | 监督学习 |
| 训练数据 | `rps.zip` |
| 测试数据 | `rps-test-set.zip` |
| 训练轮数 | 5 |
| 测试集准确率 | 1.0000 |
| 测试集损失 | 0.0191 |
| Python 端 TFLite 验证 | 成功，见 `outputs/tflite_inference_results.csv` |

## 输出文件

- `rps_classifier.keras`
- `saved_model/`
- `rps_classifier.tflite`
- `rps_classifier_quant.tflite`
- `labels.txt`

## 模型文件大小

- `rps_classifier.keras`: 21.20 MB
- `labels.txt`: 0.00 MB
- `rps_classifier.tflite`: 7.05 MB
- `rps_classifier_quant.tflite`: 1.78 MB

## Python TFLite 样例推理

- `testpaper01-00.png`: paper -> paper (0.8651)
- `testpaper01-01.png`: paper -> paper (0.8676)
- `testpaper01-02.png`: paper -> paper (0.8788)
- `testrock01-00.png`: rock -> rock (1.0000)
- `testrock01-01.png`: rock -> rock (1.0000)
- `testrock01-02.png`: rock -> rock (1.0000)

## 当前限制

- 数据集背景比较单一，真实手机摄像头环境下可能受到光照、角度、背景影响。
- 本地训练使用 CPU，为保证课堂实验闭环，训练轮数控制为 5 轮。
- 后续需要结合 CameraX 或 Android App 进行实时手势识别验证。
