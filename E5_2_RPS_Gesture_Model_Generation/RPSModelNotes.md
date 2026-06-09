# RPS 模型学习笔记

## 1. 什么是石头剪刀布手势识别

石头剪刀布手势识别是一个三分类图像识别任务。输入是一张手势图片，模型输出它属于 `rock`、`paper`、`scissors` 中哪一类。本实验把它作为后续 Android 端实时识别的模型生成练习。

## 2. 什么是图像分类

图像分类是让模型从图片中提取特征，再判断图片属于哪个类别。本实验中，一张图片经过 resize、归一化和 CNN 特征提取后，最后由 softmax 输出三个类别的概率。

## 3. TensorFlow 与 Keras

TensorFlow 是深度学习框架，负责张量计算、模型训练、保存和 TFLite 转换。Keras 是 TensorFlow 中常用的高层 API，可以用更简洁的方式定义模型、编译模型和调用 `fit` 训练。

## 4. Sequential

Sequential 是 Keras 中按顺序堆叠网络层的模型写法。本实验的模型从 `InputLayer` 开始，依次经过多组 `Conv2D`、`MaxPooling2D`，再通过 `Flatten`、`Dropout`、`Dense` 输出分类结果。

## 5. CNN

CNN 是卷积神经网络，适合处理图片。卷积层会在图片局部区域中寻找边缘、纹理、手掌形状等特征；越靠后的层通常能组合出更抽象的手势结构。

## 6. Conv2D

`Conv2D` 是二维卷积层。本实验用它学习手势图片中的局部视觉特征，例如手指边缘、轮廓和背景差异。

## 7. MaxPooling2D

`MaxPooling2D` 用于缩小特征图尺寸，保留局部区域中最明显的特征。这样可以减少计算量，也让模型对小范围位置变化更稳定。

## 8. Flatten

`Flatten` 把卷积层输出的多维特征图拉平成一维向量，方便后面的全连接 `Dense` 层做分类。

## 9. Dense

`Dense` 是全连接层。本实验中，第一个 Dense 层综合前面提取出的图像特征，最后一个 Dense 层输出 3 个类别的概率。

## 10. Dropout

`Dropout` 会在训练时随机丢弃一部分神经元输出，降低模型死记训练集的风险。本实验使用 `Dropout(0.5)` 来缓解过拟合。

## 11. softmax

`softmax` 会把最后一层输出转换为概率分布，三个概率之和为 1。概率最高的类别就是模型预测结果。

## 12. 图片预处理

本实验对图片执行 `resize` 到 150 x 150、`rescale=1/255` 归一化，并对训练集进行旋转、平移、缩放、水平翻转等数据增强。

## 13. 训练集、验证集、测试集

训练集用于更新模型参数；验证集用于训练过程中观察效果；测试集用于训练结束后的最终评估。本实验使用 `rps.zip` 的 80% 作为训练集、20% 作为验证集，使用 `rps-test-set.zip` 作为测试集。

## 14. compile

`compile` 用于设置训练规则。本实验使用 `optimizer="adam"`、`loss="categorical_crossentropy"`、`metrics=["accuracy"]`。

## 15. loss

loss 表示模型预测和真实标签之间的差距。本实验是多分类任务，所以使用 categorical crossentropy。

## 16. accuracy

accuracy 表示分类正确率。本实验在训练、验证和测试集上都记录 accuracy，用于判断模型是否真的学到了有效特征。

## 17. fit

`fit` 是 Keras 的训练入口。本实验中 `model.fit(train_generator, epochs=5, validation_data=validation_generator)` 会按批次读取图片并更新模型参数。

## 18. 混淆矩阵

混淆矩阵展示真实类别和预测类别之间的对应关系，可以看出模型容易把哪两类手势混淆。比如如果 `paper` 经常被预测成 `rock`，矩阵对应位置会有较大数值。

## 19. TFLite / LiteRT

TFLite / LiteRT 是面向移动端和边缘设备的轻量模型格式。本实验把 Keras / SavedModel 模型转换为 `.tflite`，并用 Python 的 TFLite Interpreter 验证推理。

## 20. 和后续 Android 手势识别 App 的关系

本实验生成的 `rps_classifier.tflite`、`rps_classifier_quant.tflite` 和 `labels.txt` 可以作为后续 Android CameraX 手势识别 App 的模型资产。Android 端需要保持输入尺寸、归一化方式和标签顺序与本实验一致。
