# 问题与解决方法

## 本次真实遇到的问题

| 问题 | 原因 | 解决方法 |
|---|---|---|
| JDK 21 构建失败，提示 `Unsupported class file major version 65` | 项目使用 Gradle 6.5，无法在当前 JDK 21 下正常解析 Groovy/Gradle 脚本 | 构建命令中临时切换到 JDK 11 |
| Windows 中文路径被旧 AGP 拦截 | Android Gradle Plugin 4.1 默认拒绝非 ASCII 项目路径 | 按提示在 `gradle.properties` 加入 `android.overridePathCheck=true` |
| `tensorflow-lite-support:0.1.0-rc1` 解析失败 | Maven Central 中没有该 support rc 版本 | 增加 `mavenCentral()`，并把 support/metadata 改为可解析的 `0.1.0` |
| Debug keystore 读取失败 | 旧 JDK 11 无法读取由较新 JDK 算法生成的 debug keystore | 使用临时 `ANDROID_SDK_HOME` / `ANDROID_USER_HOME` 让构建生成兼容 debug keystore |
| 当前环境没有 Android 真机 | `adb devices -l` 未列出物理设备 | 使用 Pixel_8 模拟器补充验证，真机运行等待连接设备后完成 |

## 新解析 PPT 排查表

| 问题 | 可能原因 | 解决方法 |
|---|---|---|
| 权限弹窗未授权 | Manifest 或运行时权限未正确处理 | 检查 CAMERA 权限，必要时到真机设置中重新开启 |
| FlowerModel 找不到 | `.tflite` 未导入 start 模块或 `mlModelBinding` 未开启 | 把 `FlowerModel.tflite` 放到 start 模块 `ml` 目录，开启 `mlModelBinding` 并 Sync |
| 预览有画面但结果不变 | ImageAnalysis 未绑定或 `imageProxy.close()` 缺失 | 检查 `bindToLifecycle` 和 `analyze()` 的 `finally close` |
| 运行卡顿或发热 | 分析分辨率过高、帧处理太频繁、GPU 不兼容 | 降低分辨率，减少 Top-K，使用 CPU fallback 或 GPU delegate |
| 列表闪烁 | RecyclerView 高频刷新 | 关闭 `itemAnimator` 或降低 UI 更新频率 |

## 仍需人工完成的验证

老师要求优先真机运行。当前自动环境只有 Pixel_8 模拟器，没有连接物理 Android 设备。本项目已经完成代码、模型导入、构建和模拟器运行验证；真机花卉实拍截图需要连接手机后补充。
