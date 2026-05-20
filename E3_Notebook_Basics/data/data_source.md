# Fortune 500 数据来源说明

## 数据集名称

Fortune 500 historical ranking dataset, 1955-2005。

## 数据来源

本实验使用公开 Gist 中的 `fortune500.csv`：

<https://gist.githubusercontent.com/applesash/df7bf7f31127d7f2a7a3caa71a10528c/raw/fortune500.csv>

该文件字段结构与课程 PPT 中 Fortune 500 数据分析示例一致，包含 1955 年至 2005 年的财富 500 强排名记录。由于老师资料目录中没有找到单独提供的 `fortune500.csv`，本实验采用这个公开 CSV 文件完成 Pandas 读取、异常值处理和 Matplotlib 绘图练习。

## 字段说明

| 原始字段 | 本实验统一字段 | 含义 |
|---|---|---|
| Year | year | 排名年份 |
| Rank | rank | 当年财富 500 强排名 |
| Company | company | 公司名称 |
| Revenue (in millions) | revenue | 收入，单位为百万美元 |
| Profit (in millions) | profit | 利润，单位为百万美元 |

## 数据真实性说明

本数据来自公开网络 CSV，不是本仓库自行伪造的数据，也不是我手工编写的样例表。本仓库同时保留 `src/generate_fortune500_sample.py`，仅作为无法联网时的备用课程复现实验样例生成工具；当前提交的 `data/fortune500.csv` 使用的是公开 Fortune 500 历史数据文件。

## profit 中为什么有 N.A.

部分公司在某些年份没有公开、完整或可直接使用的利润数值，因此 `Profit (in millions)` 字段中会出现 `N.A.`。这些值不是可直接参与均值统计和绘图的数字，如果不处理，会导致数值转换和图表分析出错。

## 本实验如何处理异常值

Notebook 会先展示 `profit` 中包含 `N.A.` 的行数和样例行，然后删除这些行，再将 `profit`、`revenue`、`year`、`rank` 转换为数值类型。清洗后的前 20 行保存到：

`E3_Notebook_Basics/outputs/cleaned_fortune500_preview.csv`

## 使用目的

该数据仅用于课程学习、Notebook 基础实践、Pandas 数据分析和 Matplotlib 可视化练习。
