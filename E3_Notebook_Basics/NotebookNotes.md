# Notebook 基础实践笔记

## 什么是 Jupyter Notebook

Jupyter Notebook 是一种把文字说明、代码、运行输出和图表放在同一个页面里的开发工具。它不像普通 `.py` 文件那样只能看到代码，而是可以一边写解释，一边运行代码，一边保留结果。对于课程实验、数据分析和机器学习原型验证来说，这种形式很适合记录思路和过程。

## Notebook 为什么适合实验记录

本实验既有 Python 语法练习，又有选择排序测试，还有 Pandas 数据清洗和 Matplotlib 图表。如果全部写在一个脚本里，老师只能看到最终运行结果；放在 Notebook 里，则可以看到每一步做了什么、为什么这样做、运行后输出了什么。因此 Notebook 很适合做实验报告、数据分析记录和模型训练日志。

## 什么是 Cell

Cell 是 Notebook 的基本单元。一个 Notebook 由很多 Cell 组成，每个 Cell 可以单独运行、移动、删除或修改。实验中把“环境检查”“选择排序”“读取 CSV”“绘图”等内容拆成不同 Cell，便于逐步调试和复现。

## Markdown Cell 和 Code Cell 的区别

Markdown Cell 用来写说明文字、标题、表格和总结，例如本实验中的 Notebook 概念、选择排序原理和实验总结。

Code Cell 用来写 Python 代码。运行 Code Cell 后，Notebook 会在 Cell 下方显示输出结果，例如 `selection_sort` 的测试输出、Pandas 表格预览和 Matplotlib 图表。

## Edit 模式和 Command 模式

Notebook 有两种常见模式：

- Edit 模式：正在编辑某个 Cell 的内容，通常按 `Enter` 进入。
- Command 模式：正在操作整个 Cell，例如新增、删除、切换类型，通常按 `Esc` 进入。

理解这两种模式很重要，因为同一个按键在不同模式下含义不同。例如在 Command 模式下按 `M` 会把 Cell 转成 Markdown Cell，在 Edit 模式下按 `M` 只是输入一个字母。

## 常用快捷键

| 快捷键 | 作用 |
|---|---|
| Enter | 进入 Edit 模式 |
| Esc | 进入 Command 模式 |
| Shift + Enter | 运行当前 Cell 并跳到下一个 |
| Ctrl + Enter | 运行当前 Cell |
| A | 在上方插入 Cell |
| B | 在下方插入 Cell |
| M | 转为 Markdown Cell |
| Y | 转为 Code Cell |
| DD | 删除 Cell |

## Kernel 是什么

Kernel 是真正执行代码的 Python 运行环境。Notebook 页面负责展示和编辑，Kernel 负责运行代码、保存变量状态和返回输出。本实验中，`df_clean`、`annual_summary` 等变量都保存在当前 Kernel 中。

## Kernel Restart / Interrupt / Run All 的作用

- Restart：重启 Kernel，清空当前变量状态，适合从头验证 Notebook 是否完整。
- Interrupt：中断正在运行的代码，适合处理死循环或长时间无响应的 Cell。
- Run All：从上到下运行整个 Notebook。本实验要求 Notebook 能 Run All，所以主流程不能使用会阻塞的 `input()`。

## Python 基本语法复习

本项目 Notebook 复习了变量、列表、`for` 循环、`if` 判断、函数和字符串格式化。比如通过 `numbers = [64, 25, 12, 22, 11]` 创建列表，再用循环逐个判断数字是否大于 20。

## selection_sort 选择排序原理

选择排序的思想很直观：每一轮从还没有排好序的数据里找出最小值，把它放到当前最前面的位置。第一轮找全体最小值，第二轮从剩下的数据里找最小值，以此类推，直到列表有序。

本项目同时在 Notebook 和 `src/selection_sort.py` 中实现了：

- `selection_sort(data)`：返回排序后的新列表，不修改原列表。
- `parse_numbers(text)`：把空格或逗号分隔的字符串解析成整数列表。
- `test_selection_sort()`：使用多组测试数据验证算法正确性。

## Pandas 是什么

Pandas 是 Python 中常用的数据分析库，适合读取 CSV、查看表格、筛选数据、处理缺失值和做分组统计。本实验使用 Pandas 读取 Fortune 500 数据集，并完成数据预览、列属性检查、异常值删除和年度均值统计。

## DataFrame 是什么

DataFrame 是 Pandas 里最常用的二维表格结构，可以理解为 Python 中的“表格对象”。每一列有列名，每一行是一条记录。本实验中的 `df` 和 `df_clean` 都是 DataFrame。

## 如何读取 CSV

本实验使用：

```python
df = pd.read_csv(DATA_PATH)
```

为了保证从 `E3_Notebook_Basics` 目录和 `notebooks` 目录运行都能找到数据，Notebook 中设置了多个候选路径，例如 `../data/fortune500.csv`、`data/fortune500.csv` 和 `E3_Notebook_Basics/data/fortune500.csv`。

## 如何查看数据列属性

常用方法包括：

- `df.head()`：查看前几行。
- `df.tail()`：查看后几行。
- `df.info()`：查看列名、非空数量和数据类型。
- `df.describe(include="all")`：查看统计摘要。
- `list(df.columns)`：查看全部列名。

## 如何删除 profit 列中的异常值

原始数据的利润列中有 `N.A.`，这不是数字。Notebook 先使用字符串筛选找出异常行：

```python
abnormal_profit_rows = df[df["profit"].astype(str).str.contains("N.A.", na=False)]
```

然后删除这些行，并把数值列转换成数字类型：

```python
df_clean = df[~df["profit"].astype(str).str.contains("N.A.", na=False)].copy()
df_clean["profit"] = pd.to_numeric(df_clean["profit"], errors="coerce")
```

这样后续才能正确计算平均利润和绘制趋势图。

## Matplotlib 是什么

Matplotlib 是 Python 常用绘图库，可以把数据画成折线图、柱状图、散点图等。本实验用它绘制了 Fortune 500 年度平均利润趋势图、年度平均收入趋势图，以及收入和利润的组合图。

## 如何分别绘制利润和收入

本实验先按年份统计平均收入和平均利润，得到 `annual_summary`。然后分别使用 `plt.plot()` 绘制：

- `profit_trend.png`：年度平均利润折线图。
- `revenue_trend.png`：年度平均收入折线图。

## 如何在一张图中同时画利润和收入

收入和利润的数量级差距较大，如果直接放在同一个 y 轴上，利润曲线可能被压得很扁。因此本实验使用两种方式：

- 双 y 轴：收入用左侧 y 轴，利润用右侧 y 轴，保存为 `revenue_profit_combined.png`。
- 归一化：把收入和利润都缩放到相近范围后同轴比较，保存为 `revenue_profit_normalized.png`。

## Notebook 与后续 LiteRT / 移动 AI 项目的关系

本次实验没有训练 LiteRT 模型，也没有实现 Android 端推理。它的作用是为后续实验打基础：未来训练 LiteRT 模型时，通常需要先在 Notebook 中完成数据读取、数据清洗、模型训练、指标可视化和模型导出。E2-3 的 CameraX 可以提供移动端图像输入，E3 的 Notebook 可以负责离线数据分析和模型实验，后续 E4/E5 再把模型能力接回 Android App。
