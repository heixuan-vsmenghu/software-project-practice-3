# 实验 3：Jupyter Notebook 基础实践

## 一、实验目标

本实验围绕 Jupyter Notebook 基础实践展开，目标包括：

- 熟悉 Jupyter Notebook 的基本开发流程。
- 理解 Cell、Markdown Cell、Code Cell、Edit 模式、Command 模式和 Kernel 的作用。
- 复习 Python 变量、列表、循环、条件判断、函数和字符串格式化。
- 实现选择排序算法 `selection_sort`，并编写测试函数验证结果。
- 使用 Pandas 读取 Fortune 500 数据集，完成数据预览、列属性检查、异常值处理、过滤查询和分组统计。
- 使用 Matplotlib 分别绘制利润、收入趋势图，并在一张图中同时展示利润和收入。
- 将 Notebook、HTML、数据、脚本、输出图表、截图和文档整理到 GitHub 仓库中，便于老师审查。

## 二、实验环境

本机 PATH 中的 `python` 是 Python 3.14.3，但该环境没有安装 Jupyter、pandas 和 matplotlib。实验一安装的 Anaconda 位于 `D:\DevTools\Runtimes\Anaconda3`，其中已包含本实验需要的依赖，因此本实验实际使用 Anaconda 环境运行 Notebook。

| 项目 | 版本 |
|---|---|
| Python | 3.13.9 |
| Jupyter Notebook | 7.4.5 |
| JupyterLab | 4.4.7 |
| nbconvert | 7.16.6 |
| pandas | 2.3.3 |
| matplotlib | 3.10.6 |
| numpy | 2.3.5 |

环境检查命令：

```powershell
D:\DevTools\Runtimes\Anaconda3\python.exe --version
D:\DevTools\Runtimes\Anaconda3\Scripts\jupyter.exe --version
D:\DevTools\Runtimes\Anaconda3\python.exe -m pip show pandas
D:\DevTools\Runtimes\Anaconda3\python.exe -m pip show matplotlib
```

## 三、实验内容与完成情况

| 老师要求 | 本项目完成情况 |
|---|---|
| 安装 Jupyter Notebook 和 Python 环境 | 已使用本机 Anaconda Python / Jupyter 环境完成实验 |
| 掌握 Notebook 基本原理 | 已在 NotebookNotes 和 Notebook 中总结 Cell、Kernel、快捷键 |
| 熟悉 Python 基本语法 | 已完成变量、列表、循环、函数等练习 |
| 编写选择排序算法 | 已实现 selection_sort 函数 |
| 定义 test 函数进行测试 | 已实现 test_selection_sort 并保留输出 |
| 完成数据输入、排序和输出 | 已使用模拟输入完成排序流程 |
| 使用 Pandas 分析 Fortune 500 数据 | 已完成读取、预览、列属性检查、过滤、查询 |
| 删除 profit 异常值 | 已删除 profit 为 N.A. 的数据行并转换数值类型 |
| 使用 Matplotlib 绘图 | 已分别绘制利润和收入趋势图 |
| 一张图同时画利润和收入 | 已完成 revenue_profit_combined 图 |
| GitHub 共享 Notebook | 已整理 ipynb、HTML、README、数据、输出图表和截图，提交后可在 GitHub 审查 |

## 四、项目结构

```text
E3_Notebook_Basics/
├── README.md
├── NotebookNotes.md
├── requirements.txt
├── environment.yml
├── notebooks/
│   ├── E3_Notebook_Basics_Practice.ipynb
│   └── E3_Notebook_Basics_Practice.html
├── data/
│   ├── fortune500.csv
│   └── data_source.md
├── src/
│   ├── selection_sort.py
│   └── generate_fortune500_sample.py
├── outputs/
│   ├── profit_trend.png
│   ├── revenue_trend.png
│   ├── revenue_profit_combined.png
│   ├── revenue_profit_normalized.png
│   └── cleaned_fortune500_preview.csv
└── images/
    └── 实验截图
```

## 五、Notebook 基本概念

Notebook 是一种交互式文档，可以把 Markdown 说明、Python 代码、运行输出、表格和图表放在同一个文件中。它适合实验记录，因为每一步代码和结果都能被保留下来。

Cell 是 Notebook 的基本单元。Markdown Cell 用来写标题、说明和总结；Code Cell 用来写代码并显示运行输出。

Edit 模式用于编辑 Cell 内容，Command 模式用于操作整个 Cell。Kernel 是真正执行代码的 Python 进程，负责保存变量状态、运行代码并返回输出。常用操作包括 Restart、Interrupt 和 Run All。

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

详细笔记见 [NotebookNotes.md](NotebookNotes.md)。

## 六、Python 选择排序实验

选择排序的思想是：每一轮从未排序部分找出最小值，把它放到当前最前面的位置。本实验在 Notebook 和 [src/selection_sort.py](src/selection_sort.py) 中都实现了 `selection_sort(data)`。

同时实现了：

- `parse_numbers(text)`：支持空格或逗号分隔的数字字符串。
- `test_selection_sort()`：覆盖普通列表、逆序列表、有序列表、重复元素、空列表、单元素列表和负数列表。
- 模拟用户输入 `"64 25 12 22 11"`，完成解析、排序和输出。

运行命令：

```powershell
cd E3_Notebook_Basics
python src\selection_sort.py
```

## 七、Pandas 数据分析

本实验使用公开 Fortune 500 历史 CSV 数据，字段包括年份、排名、公司、收入和利润。原始列名统一为：

```text
year, rank, company, revenue, profit
```

Notebook 中完成了：

- `pd.read_csv()` 读取数据。
- `df.head()` 和 `df.tail()` 预览数据。
- `df.info()` 检查列属性和非空数量。
- `df.describe(include="all")` 查看统计摘要。
- 展示 `profit` 中包含 `N.A.` 的异常行。
- 删除 `profit` 为 `N.A.` 的行，并将数值列转换为数字类型。
- 查询 1955 年排名前 10 公司。
- 查询收入最高和利润最高的记录。
- 按年份统计平均收入、平均利润和公司数量。

清洗后的预览保存为 [outputs/cleaned_fortune500_preview.csv](outputs/cleaned_fortune500_preview.csv)。

数据来源说明见 [data/data_source.md](data/data_source.md)。

## 八、Matplotlib 数据可视化

本实验完成 4 个图表输出：

- [outputs/profit_trend.png](outputs/profit_trend.png)：年度平均利润趋势图。
- [outputs/revenue_trend.png](outputs/revenue_trend.png)：年度平均收入趋势图。
- [outputs/revenue_profit_combined.png](outputs/revenue_profit_combined.png)：双 y 轴同时展示收入和利润。
- [outputs/revenue_profit_normalized.png](outputs/revenue_profit_normalized.png)：归一化后同轴比较收入和利润。

由于收入和利润的数值量级差距较大，同图展示时使用了双 y 轴和归一化两种方式，让两条曲线都能清晰观察。

## 九、运行与复现方法

如果 Jupyter 已在 PATH 中，可以直接运行：

```powershell
cd E3_Notebook_Basics
jupyter nbconvert --execute --inplace notebooks\E3_Notebook_Basics_Practice.ipynb
jupyter nbconvert --to html notebooks\E3_Notebook_Basics_Practice.ipynb
```

本机实际使用 Anaconda 路径运行：

```powershell
cd E3_Notebook_Basics
D:\DevTools\Runtimes\Anaconda3\Scripts\jupyter.exe nbconvert --execute --inplace notebooks\E3_Notebook_Basics_Practice.ipynb
D:\DevTools\Runtimes\Anaconda3\Scripts\jupyter.exe nbconvert --to html notebooks\E3_Notebook_Basics_Practice.ipynb
```

可选启动图形界面：

```powershell
cd E3_Notebook_Basics
D:\DevTools\Runtimes\Anaconda3\Scripts\jupyter.exe notebook
```

## 十、运行结果截图

![Jupyter Notebook 启动](images/jupyter_launch.png)

![Notebook 创建成功](images/notebook_created.png)

![Markdown Cell 示例](images/notebook_markdown_cell.png)

![Code Cell 示例](images/notebook_code_cell.png)

![Edit 和 Command 模式](images/edit_command_mode.png)

![Kernel 运行状态](images/kernel_running.png)

![选择排序运行结果](images/python_selection_sort_result.png)

![Pandas 数据预览](images/pandas_data_preview.png)

![Pandas 列属性检查](images/pandas_column_info.png)

![profit 异常值清洗前](images/profit_na_before_cleaning.png)

![profit 异常值清洗后](images/profit_cleaned_after.png)

![利润和收入分别绘制](images/profit_revenue_separate_charts.png)

![一张图同时画利润和收入](images/revenue_profit_combined_chart.png)

![Notebook 全部运行成功](images/notebook_run_all_success.png)

![GitHub 渲染 Notebook](images/github_notebook_render.png)

![GitHub 提交记录](images/github_commit_history.png)

## 十一、遇到的问题与解决方法

1. `python --version` 指向 Python 3.14.3，但该环境缺少 Jupyter、pandas 和 matplotlib。
   解决方法：改用实验一安装的 Anaconda 环境完成 Notebook 执行和 HTML 导出。

2. 使用 pip 安装依赖时，本机代理配置不可用，导致无法从包索引安装。
   解决方法：不新建复杂环境，直接使用本机 Anaconda 中已有的稳定依赖。

3. Notebook 最初通过 PowerShell 管道生成时出现中文乱码。
   解决方法：重新用 UTF-8 源文件生成 Notebook，并重新执行、重新导出 HTML。

4. Notebook 中不能使用阻塞式 `input()`。
   解决方法：使用字符串模拟用户输入，保证 Run All 可以一次执行成功。

5. 原始 Fortune 500 数据中 `profit` 包含 `N.A.`。
   解决方法：先展示异常行，再删除这些行，并将 `profit`、`revenue`、`year`、`rank` 转换为数值类型。

6. `git pull` 时 GitHub 代理端口 `127.0.0.1:7897` 不可用。
   解决方法：保留当前本地仓库状态继续实验，后续提交和推送时单独处理网络问题。

## 十二、与后续 LiteRT / 移动 AI 项目的关系

本次实验不是直接训练模型，也不是直接接入 Android App。它的作用是为后续移动 AI 实验打基础。

未来 E5 训练 LiteRT 模型时，通常需要先在 Notebook 中完成数据读取、数据清洗、模型训练、指标可视化和模型导出。E2-3 的 CameraX 可以提供移动端图像输入，E3 的 Notebook 可以负责离线数据分析和模型实验，后续 E4/E5 再把模型能力接回 Android App。

因此，本实验重点训练的是数据分析、实验记录和可视化能力，不虚假声称已经完成 LiteRT 模型训练或 Android 端推理。

## 十三、实验总结

通过本实验，我掌握了 Jupyter Notebook 的基本使用方式，理解了 Cell、Edit 模式、Command 模式和 Kernel 的作用；通过 `selection_sort` 练习了 Python 函数、循环和测试；通过 Pandas 完成了 Fortune 500 数据读取、清洗、过滤和分组统计；通过 Matplotlib 绘制了收入和利润趋势图，并完成了一张图同时展示收入和利润的扩展任务。

Notebook 是后续机器学习和移动 AI 实验的重要工作台。本实验为后续 LiteRT 模型训练、数据预处理、指标可视化和 Android App 推理能力接入打下基础。

## 十四、参考资料

- Jupyter Notebook 官方文档：<https://docs.jupyter.org/>
- pandas 官方文档：<https://pandas.pydata.org/docs/>
- Matplotlib 官方文档：<https://matplotlib.org/stable/>
- Fortune 500 CSV 数据来源：<https://gist.githubusercontent.com/applesash/df7bf7f31127d7f2a7a3caa71a10528c/raw/fortune500.csv>
