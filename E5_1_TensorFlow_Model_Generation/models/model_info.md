# 模型说明

| 项目 | 内容 |
|---|---|
| 模型名称 | `flower_classifier` |
| 任务类型 | 花卉图像分类 |
| 类别 | `daisy, dandelion, roses, sunflowers, tulips` |
| 输入尺寸 | 224 x 224 x 3 |
| 模型结构 | MobileNetV2 alpha=0.35 + GlobalAveragePooling + Dropout + Dense softmax |
| 训练方式 | 迁移学习，冻结 ImageNet 预训练 MobileNetV2，训练分类头 |
| 训练数据 | TensorFlow 官方 `flower_photos` |
| 训练轮数 | 5 |
| 验证准确率 | 0.8815 |
| 验证损失 | 0.3588 |
| Python 端 TFLite 验证 | 成功 |
| E4 Android 接入 | 见 `android_integration/` 记录 |

## 输出文件大小

- `flower_classifier.keras`: 1.88 MB
- `labels.txt`: 0.00 MB
- `flower_classifier.tflite`: 1.55 MB
- `flower_classifier_quant.tflite`: 0.54 MB
- `FlowerModel_E5.tflite`: 1.55 MB

## Python TFLite 样例推理

- `100080576_f52e8ee070_n.jpg`: daisy -> daisy (0.8554)
- `10140303196_b88d3d6cec.jpg`: daisy -> daisy (0.9192)
- `10043234166_e6dd915111_n.jpg`: dandelion -> dandelion (0.9944)
- `10200780773_c6051a7d71_n.jpg`: dandelion -> daisy (0.6729)
- `10090824183_d02c613f10_m.jpg`: roses -> roses (0.8741)

## 当前限制

- 本地环境未检测到 GPU，训练在 CPU 上完成。
- 为保证实验闭环，使用冻结 MobileNetV2 特征提取并训练轻量分类头。
- Android 端效果会受摄像头画面、光照和模型 metadata 差异影响。
