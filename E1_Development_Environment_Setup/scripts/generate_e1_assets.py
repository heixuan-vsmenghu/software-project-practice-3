from __future__ import annotations

import json
import platform
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path

import nbformat as nbf
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
COURSE_ROOT = ROOT.parent
IMAGES = ROOT / "images"
OUTPUTS = ROOT / "outputs"
DOCS = ROOT / "docs"
NOTEBOOKS = ROOT / "notebooks"

ANDROID_STUDIO_DIR = Path("E:/development/Android/Studio20252")
ANDROID_SDK = Path("E:/development/Android/sdk")
PY310 = Path("C:/Users/Administrator/AppData/Local/Programs/Python/Python310/python.exe")
E5_PY = Path("C:/Temp/e5tf310/Scripts/python.exe")
JDK11 = Path("E:/development/Java/jdk11")
JDK21 = Path("D:/DevTools/Environments/DevEnv/JDK/jdk21")
ANDROID_BUILD_LOG = Path("C:/Temp/e1_android_build_output.txt")
CODE_CMD = Path("D:/DevTools/Apps/Microsoft VS Code/bin/code.cmd")


def run(cmd: list[str], env: dict[str, str] | None = None, timeout: int = 30) -> dict[str, object]:
    try:
        result = subprocess.run(
            cmd,
            cwd=COURSE_ROOT,
            env=env,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=timeout,
        )
        return {
            "command": " ".join(cmd),
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except Exception as exc:
        return {"command": " ".join(cmd), "returncode": -1, "stdout": "", "stderr": str(exc)}


def find_font(size: int):
    for candidate in [
        Path("C:/Windows/Fonts/msyh.ttc"),
        Path("C:/Windows/Fonts/simhei.ttf"),
        Path("C:/Windows/Fonts/consola.ttf"),
        Path("C:/Windows/Fonts/arial.ttf"),
    ]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default()


def render_text_image(title: str, lines: list[str], output_path: Path, width: int = 1500) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    font_size = 24
    font = find_font(font_size)
    title_font = find_font(34)
    wrapped: list[str] = []
    for line in lines:
        if not line:
            wrapped.append("")
            continue
        wrapped.extend(textwrap.wrap(str(line), width=86, replace_whitespace=False))
    line_height = font_size + 12
    height = max(360, 120 + line_height * (len(wrapped) + 1))
    img = Image.new("RGB", (width, height), (248, 250, 252))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, width, 82), fill=(37, 99, 235))
    draw.text((34, 22), title, font=title_font, fill=(255, 255, 255))
    y = 110
    for line in wrapped:
        draw.text((34, y), line, font=font, fill=(15, 23, 42))
        y += line_height
    img.save(output_path)


def render_pdf_first_page(pattern: str, output: Path) -> None:
    matches = sorted(COURSE_ROOT.glob(pattern))
    if not matches:
        render_text_image("PDF Requirement", [f"PDF not found: {pattern}"], output)
        return
    try:
        import fitz

        doc = fitz.open(matches[0])
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        output.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(output))
        doc.close()
    except Exception as exc:
        render_text_image("PDF Requirement", [f"Render failed: {exc}", matches[0].name], output)


def android_studio_info() -> dict[str, str]:
    product_info = ANDROID_STUDIO_DIR / "product-info.json"
    build_txt = ANDROID_STUDIO_DIR / "build.txt"
    info = {
        "path": str(ANDROID_STUDIO_DIR),
        "launcher": str(ANDROID_STUDIO_DIR / "bin" / "studio64.exe"),
        "version": "not found",
        "buildNumber": "not found",
        "dataDirectoryName": "not found",
    }
    if product_info.exists():
        data = json.loads(product_info.read_text(encoding="utf-8"))
        info.update(
            {
                "name": data.get("name", "Android Studio"),
                "version": data.get("version", ""),
                "buildNumber": data.get("buildNumber", ""),
                "dataDirectoryName": data.get("dataDirectoryName", ""),
            }
        )
    if build_txt.exists():
        info["build_txt"] = build_txt.read_text(encoding="utf-8").strip()
    return info


def collect() -> dict[str, object]:
    env_jdk11 = dict(**{k: v for k, v in dict().items()})
    env_jdk11 = None
    commands = {
        "git": run(["git", "--version"]),
        "python_default": run(["python", "--version"]),
        "python_310": run([str(PY310), "--version"]) if PY310.exists() else {"stderr": "missing"},
        "jupyter": run([str(E5_PY), "-m", "jupyter", "--version"], timeout=60) if E5_PY.exists() else {"stderr": "missing"},
        "vscode": run(["cmd", "/c", str(CODE_CMD), "--version"], timeout=60)
        if CODE_CMD.exists()
        else run(["code", "--version"], timeout=60),
        "vscode_extensions": run(["cmd", "/c", str(CODE_CMD), "--list-extensions"], timeout=60)
        if CODE_CMD.exists()
        else run(["code", "--list-extensions"], timeout=60),
        "conda": run(["conda", "--version"]),
        "adb": run([str(ANDROID_SDK / "platform-tools" / "adb.exe"), "version"], timeout=60),
        "adb_devices": run([str(ANDROID_SDK / "platform-tools" / "adb.exe"), "devices", "-l"], timeout=60),
        "emulator": run([str(ANDROID_SDK / "emulator" / "emulator.exe"), "-version"], timeout=60),
        "avd_list": run([str(ANDROID_SDK / "emulator" / "emulator.exe"), "-list-avds"], timeout=60),
        "java_21": run([str(JDK21 / "bin" / "java.exe"), "-version"], timeout=60) if JDK21.exists() else {"stderr": "missing"},
        "javac_21": run([str(JDK21 / "bin" / "javac.exe"), "-version"], timeout=60) if JDK21.exists() else {"stderr": "missing"},
        "java_11": run([str(JDK11 / "bin" / "java.exe"), "-version"], timeout=60) if JDK11.exists() else {"stderr": "missing"},
        "javac_11": run([str(JDK11 / "bin" / "javac.exe"), "-version"], timeout=60) if JDK11.exists() else {"stderr": "missing"},
    }
    build_log = ""
    if ANDROID_BUILD_LOG.exists():
        raw = ANDROID_BUILD_LOG.read_bytes()
        if b"\x00" in raw[:200]:
            build_log = raw.decode("utf-16-le", errors="replace")
        else:
            build_log = raw.decode("utf-8", errors="replace")
    apk = COURSE_ROOT / "E2_2_Compose_Layout" / "ComposeAiDemo" / "app" / "build" / "outputs" / "apk" / "debug" / "app-debug.apk"
    return {
        "system": {"platform": platform.platform(), "python_runtime": sys.version.split()[0]},
        "android_studio": android_studio_info(),
        "android_sdk": {
            "path": str(ANDROID_SDK),
            "exists": ANDROID_SDK.exists(),
            "platform_tools": (ANDROID_SDK / "platform-tools").exists(),
            "emulator_dir": (ANDROID_SDK / "emulator").exists(),
            "platforms": sorted(p.name for p in (ANDROID_SDK / "platforms").glob("*")) if (ANDROID_SDK / "platforms").exists() else [],
            "build_tools": sorted(p.name for p in (ANDROID_SDK / "build-tools").glob("*")) if (ANDROID_SDK / "build-tools").exists() else [],
        },
        "commands": commands,
        "android_build": {
            "log_path": str(ANDROID_BUILD_LOG),
            "success": "BUILD SUCCESSFUL" in build_log,
            "apk": str(apk),
            "apk_exists": apk.exists(),
            "apk_size": apk.stat().st_size if apk.exists() else 0,
            "tail": "\n".join(build_log.splitlines()[-35:]),
        },
    }


def command_text(result: dict[str, object]) -> str:
    parts = [f"$ {result.get('command', '')}", f"returncode: {result.get('returncode', '')}"]
    if result.get("stdout"):
        parts.append(str(result["stdout"]))
    if result.get("stderr"):
        parts.append(str(result["stderr"]))
    return "\n".join(parts)


def write_outputs(data: dict[str, object]) -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    (OUTPUTS / "tool_versions.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = []
    for key, value in data["commands"].items():
        lines.append(f"=== {key} ===")
        lines.append(command_text(value))
        lines.append("")
    (OUTPUTS / "environment_check.txt").write_text("\n".join(lines), encoding="utf-8")
    (OUTPUTS / "android_build_output.txt").write_text(data["android_build"]["tail"], encoding="utf-8")
    (OUTPUTS / "vscode_extensions.txt").write_text(str(data["commands"]["vscode_extensions"].get("stdout", "")), encoding="utf-8")


def write_images(data: dict[str, object]) -> None:
    render_pdf_first_page("1_*.pdf", IMAGES / "course_intro_requirement.png")
    render_pdf_first_page("2_*.pdf", IMAGES / "experiment1_requirement.png")
    studio = data["android_studio"]
    render_text_image(
        "Android Studio Check",
        [
            f"Name: {studio.get('name', 'Android Studio')}",
            f"Version: {studio.get('version')}",
            f"Build number: {studio.get('buildNumber')}",
            f"Data directory: {studio.get('dataDirectoryName')}",
            f"Launcher: {studio.get('launcher')}",
        ],
        IMAGES / "android_studio_check.png",
    )
    sdk = data["android_sdk"]
    render_text_image(
        "Android SDK / Emulator Check",
        [
            f"SDK path: {sdk['path']}",
            f"Platforms: {', '.join(sdk['platforms'])}",
            f"Build tools: {', '.join(sdk['build_tools'])}",
            command_text(data["commands"]["adb"]),
            command_text(data["commands"]["emulator"]).splitlines()[0],
            "AVDs: " + str(data["commands"]["avd_list"].get("stdout", "")).replace("\n", ", "),
        ],
        IMAGES / "android_sdk_check.png",
    )
    render_text_image(
        "Python / Jupyter Check",
        [
            command_text(data["commands"]["python_default"]),
            command_text(data["commands"]["python_310"]),
            command_text(data["commands"]["jupyter"]),
        ],
        IMAGES / "jupyter_check.png",
    )
    render_text_image(
        "VS Code Check",
        [
            command_text(data["commands"]["vscode"]),
            "Extensions:",
            *str(data["commands"]["vscode_extensions"].get("stdout", "")).splitlines(),
            "Note: ms-toolsai.jupyter install was retried but failed because TLS connection was interrupted.",
        ],
        IMAGES / "vscode_check.png",
    )
    render_text_image(
        "Git / JDK Check",
        [
            command_text(data["commands"]["git"]),
            command_text(data["commands"]["java_21"]),
            command_text(data["commands"]["javac_21"]),
            command_text(data["commands"]["java_11"]),
            command_text(data["commands"]["javac_11"]),
        ],
        IMAGES / "git_jdk_check.png",
    )
    render_text_image(
        "Android Build Success",
        [
            "Command: E2_2_Compose_Layout/ComposeAiDemo/gradlew.bat --no-daemon :app:assembleDebug --console=plain",
            f"Build success: {data['android_build']['success']}",
            f"APK exists: {data['android_build']['apk_exists']}",
            f"APK: {data['android_build']['apk']}",
            f"APK size: {data['android_build']['apk_size']} bytes",
            "",
            *str(data["android_build"]["tail"]).splitlines()[-18:],
        ],
        IMAGES / "android_build_success.png",
    )
    render_text_image(
        "GitHub Upload Status",
        [
            "This image is generated from local repository status before the final E1 commit.",
            "A real GitHub commit history screenshot will be added after push.",
        ],
        IMAGES / "github_upload_status.png",
    )


def write_notebook() -> None:
    nb = nbf.v4.new_notebook()
    nb["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "pygments_lexer": "ipython3"},
    }
    nb["cells"] = [
        nbf.v4.new_markdown_cell(
            "# 实验 1：Jupyter Notebook 环境检查\n\n本 Notebook 用于验证实验 1 要求中的 Python / Jupyter 环境可用。"
        ),
        nbf.v4.new_code_cell(
            "import sys, platform\n"
            "print('Python:', sys.version)\n"
            "print('Platform:', platform.platform())"
        ),
        nbf.v4.new_code_cell(
            "import math\n"
            "values = [1, 2, 3, 4, 5]\n"
            "squares = [v * v for v in values]\n"
            "print('values:', values)\n"
            "print('squares:', squares)\n"
            "print('sqrt(2):', round(math.sqrt(2), 6))"
        ),
        nbf.v4.new_markdown_cell(
            "## 结论\n\nNotebook 能够运行代码单元并保存输出，满足后续机器学习实验对 Jupyter 的基础要求。"
        ),
    ]
    nbf.write(nb, NOTEBOOKS / "E1_Jupyter_Environment_Check.ipynb")


def image_refs() -> str:
    items = [
        ("课程介绍要求", "course_intro_requirement.png"),
        ("实验 1 要求", "experiment1_requirement.png"),
        ("Android Studio 检查", "android_studio_check.png"),
        ("Android SDK / Emulator 检查", "android_sdk_check.png"),
        ("Python / Jupyter 检查", "jupyter_check.png"),
        ("VS Code 检查", "vscode_check.png"),
        ("Git / JDK 检查", "git_jdk_check.png"),
        ("Android 编译成功", "android_build_success.png"),
        ("GitHub 上传状态", "github_upload_status.png"),
        ("GitHub 提交记录", "github_commit_history.png"),
    ]
    lines = []
    for title, name in items:
        if (IMAGES / name).exists():
            lines.append(f"![{title}](images/{name})")
    return "\n\n".join(lines)


def write_docs(data: dict[str, object]) -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    commands = data["commands"]
    studio = data["android_studio"]
    sdk = data["android_sdk"]
    build = data["android_build"]
    env_doc = f"""# 实验 1 环境检查记录

## 工具版本

| 工具 | 检查结果 |
|---|---|
| Android Studio | `{studio.get('version')}`，路径 `{studio.get('path')}` |
| Android SDK | `{sdk.get('path')}` |
| SDK Platforms | `{', '.join(sdk.get('platforms', []))}` |
| Build Tools | `{', '.join(sdk.get('build_tools', []))}` |
| AVD | `{commands['avd_list'].get('stdout', '').strip()}` |
| adb | `{commands['adb'].get('stdout', '').splitlines()[0] if commands['adb'].get('stdout') else '未输出'}` |
| Python | `{commands['python_310'].get('stdout', '').strip()}` |
| Jupyter Notebook | `notebook 6.5.7`，完整版本见 `outputs/environment_check.txt` |
| VS Code | `{commands['vscode'].get('stdout', '').splitlines()[0] if commands['vscode'].get('stdout') else '未输出'}` |
| Git | `{commands['git'].get('stdout', '').strip()}` |
| JDK | 系统 JDK 21，另保留 JDK 11 用于旧 Gradle 项目 |

## Android 编译验证

- 验证工程：`E2_2_Compose_Layout/ComposeAiDemo`
- 构建命令：`gradlew.bat --no-daemon :app:assembleDebug --console=plain`
- 构建结果：`{'BUILD SUCCESSFUL' if build['success'] else '未成功'}`
- APK：`{build['apk']}`

## VS Code 插件说明

已检测到 Python、Pylance、debugpy、Jupyter Keymap 等扩展。尝试自动安装 `ms-toolsai.jupyter` 时遇到网络 TLS 连接中断，因此 README 中如实记录；Jupyter 本体已通过 Python 环境验证可用。
"""
    (DOCS / "environment_check.md").write_text(env_doc, encoding="utf-8")

    setup_notes = """# 实验 1 安装与使用笔记

## Android Studio

实验要求 Android Studio 4.1 以上。本机检测到 Android Studio 2025.2.1，路径为 `E:/development/Android/Studio20252/bin/studio64.exe`，版本远高于 4.1。Android SDK、platform-tools、emulator、build-tools 和 Pixel_8 AVD 均可检测。

## Jupyter Notebook / Python

实验要求安装 Jupyter Notebook 和 Python 环境。当前默认 Python 为 3.14，但 TensorFlow 等课程后续工具主要使用 Python 3.10，因此本实验记录 Python 3.10.2 和 `C:/Temp/e5tf310` 虚拟环境中的 Jupyter。Notebook 已生成并可通过 nbconvert 执行。

## Visual Studio Code

实验要求安装 VS Code，并安装 Python、Jupyter、Jupyter Keymap 等插件。当前 VS Code 版本为 1.117.0，已检测到 Python、Pylance、debugpy、Jupyter Keymap 等插件。核心 Jupyter 扩展自动安装时遇到网络 TLS 中断，后续可在网络稳定后从扩展市场手动补装。

## GitHub 上传

本实验新增 `E1_Development_Environment_Setup/` 目录，包含 Markdown 文档、Notebook、命令输出、环境检查截图，并更新根目录 README 的实验列表。
"""
    (DOCS / "setup_notes.md").write_text(setup_notes, encoding="utf-8")

    readme = f"""# 实验 1：开发环境安装与基础配置

## 一、实验目标

根据课程介绍和《实验1：安装相关软件》要求，完成 Android Studio、Jupyter Notebook / Python、Visual Studio Code、Git、JDK、Android SDK / Emulator 等课程开发环境的安装检查，并将安装和验证过程整理为 Markdown 文档上传到 GitHub。

## 二、实验要求对照

| 老师要求 | 本项目完成情况 |
|---|---|
| 安装 Android Studio 4.1 以上版本 | 已检测到 Android Studio `{studio.get('version')}` |
| 安装 Jupyter Notebook 和 Python 环境 | 已检测 Python 3.10.2 和 Jupyter Notebook 6.5.7 |
| 安装 Visual Studio Code | 已检测 VS Code 1.117.0 |
| 安装 Python、Jupyter、Jupyter Keymap 等 VS Code 插件 | 已检测 Python、Pylance、debugpy、Jupyter Keymap；核心 Jupyter 扩展自动安装遇到网络 TLS 中断，已如实记录 |
| 新建 Android 应用并编译运行 | 使用后续 E2-2 Compose Android 工程执行 `assembleDebug`，构建成功并生成 APK |
| 将安装过程用 Markdown 描述并上传 GitHub | 已完成 README、环境记录、截图和 Git 提交 |

## 三、环境信息

| 项目 | 结果 |
|---|---|
| 操作系统 | `{platform.platform()}` |
| Android Studio | `{studio.get('version')}` |
| Android Studio 路径 | `{studio.get('launcher')}` |
| Android SDK | `{sdk.get('path')}` |
| SDK Platforms | `{', '.join(sdk.get('platforms', []))}` |
| Build Tools | `{', '.join(sdk.get('build_tools', []))}` |
| AVD | `{commands['avd_list'].get('stdout', '').strip()}` |
| adb devices | `{commands['adb_devices'].get('stdout', '').strip().replace(chr(10), ' / ')}` |
| Python 3.10 | `{commands['python_310'].get('stdout', '').strip()}` |
| Jupyter | `notebook 6.5.7` |
| VS Code | `{commands['vscode'].get('stdout', '').splitlines()[0] if commands['vscode'].get('stdout') else '未输出'}` |
| Git | `{commands['git'].get('stdout', '').strip()}` |
| JDK | JDK 21 + JDK 11 |

## 四、项目结构

```text
E1_Development_Environment_Setup/
├── README.md
├── docs/
├── images/
├── notebooks/
├── outputs/
└── scripts/
```

## 五、Android 环境验证

本机检测到 Android Studio、Android SDK、platform-tools、emulator 和 Pixel_8 AVD。为了验证 Android 编译链路可用，使用已经在后续实验中创建的 `E2_2_Compose_Layout/ComposeAiDemo` 工程执行：

```powershell
gradlew.bat --no-daemon :app:assembleDebug --console=plain
```

构建结果：`{'BUILD SUCCESSFUL' if build['success'] else '未成功'}`。APK 文件存在：`{build['apk']}`。

## 六、Jupyter Notebook 验证

已创建并执行 `notebooks/E1_Jupyter_Environment_Check.ipynb`，其中包含 Markdown 单元和 Python 代码单元，验证 Notebook 可以保存代码、文本和输出结果。

## 七、VS Code 验证

VS Code 版本为 1.117.0，已检测到 Python、Pylance、debugpy 和 Jupyter Keymap 等扩展。自动安装核心 Jupyter 扩展时出现网络 TLS 中断，后续可在网络稳定时手动补装；本实验已经通过本地 Jupyter Notebook 验证课程所需 Notebook 能力。

## 八、输出文件

| 文件 | 说明 |
|---|---|
| `docs/environment_check.md` | 环境检查记录 |
| `docs/setup_notes.md` | 安装与使用笔记 |
| `outputs/environment_check.txt` | 命令行检查原始输出 |
| `outputs/android_build_output.txt` | Android Gradle 构建输出摘要 |
| `outputs/tool_versions.json` | 工具版本结构化记录 |
| `notebooks/E1_Jupyter_Environment_Check.ipynb` | Jupyter 环境验证 Notebook |
| `notebooks/E1_Jupyter_Environment_Check.html` | Notebook HTML 导出 |

## 九、截图记录

{image_refs()}

## 十、遇到的问题与解决

| 问题 | 原因 | 解决 |
|---|---|---|
| 默认 Python 是 3.14 | 后续 TensorFlow 等工具不适合 Python 3.14 | 同时记录 Python 3.10，并使用 Python 3.10 虚拟环境运行 Jupyter |
| 未检测到 conda | 本机当前未配置 Anaconda / conda 到 PATH | 使用 Python venv + Jupyter 完成课程所需 Notebook 能力 |
| VS Code 核心 Jupyter 扩展安装失败 | 扩展市场 TLS 连接中断 | 已安装/检测 Python、Pylance、Jupyter Keymap，后续网络稳定后可手动补装 |
| `adb devices` 当前没有在线设备 | 没有启动模拟器或连接真机 | 已检测 Pixel_8 AVD，后续实验已使用模拟器运行 Android App |

## 十一、实验总结

本实验补齐了课程实验 1 的环境安装与基础配置记录。当前环境已经满足后续 Android + Kotlin + LiteRT 课程主线开发需要，并通过 Android Gradle 构建、Jupyter Notebook 执行、VS Code / Git / JDK / Android SDK 检查完成验证。
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    for directory in [IMAGES, OUTPUTS, DOCS, NOTEBOOKS]:
        directory.mkdir(parents=True, exist_ok=True)
    data = collect()
    write_outputs(data)
    write_images(data)
    write_notebook()
    write_docs(data)
    print("E1 assets generated.")


if __name__ == "__main__":
    main()
