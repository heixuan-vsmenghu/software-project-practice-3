# 实验 1 环境检查记录

## 工具版本

| 工具 | 检查结果 |
|---|---|
| Android Studio | `AI-252.25557.131.2521.14344949`，路径 `E:\development\Android\Studio20252` |
| Android SDK | `E:\development\Android\sdk` |
| SDK Platforms | `android-30, android-36` |
| Build Tools | `29.0.2, 35.0.0, 36.1.0` |
| AVD | `Pixel_8` |
| adb | `Android Debug Bridge version 1.0.41` |
| Python | `Python 3.10.2` |
| Jupyter Notebook | `notebook 6.5.7`，完整版本见 `outputs/environment_check.txt` |
| VS Code | `1.117.0` |
| Git | `git version 2.51.0.windows.1` |
| JDK | 系统 JDK 21，另保留 JDK 11 用于旧 Gradle 项目 |

## Android 编译验证

- 验证工程：`E2_2_Compose_Layout/ComposeAiDemo`
- 构建命令：`gradlew.bat --no-daemon :app:assembleDebug --console=plain`
- 构建结果：`BUILD SUCCESSFUL`
- APK：`H:\福建师范大学\大三下\软件实践研发（3）\E2_2_Compose_Layout\ComposeAiDemo\app\build\outputs\apk\debug\app-debug.apk`

## VS Code 插件说明

已检测到 Python、Pylance、debugpy、Jupyter Keymap 等扩展。尝试自动安装 `ms-toolsai.jupyter` 时遇到网络 TLS 连接中断，因此 README 中如实记录；Jupyter 本体已通过 Python 环境验证可用。
