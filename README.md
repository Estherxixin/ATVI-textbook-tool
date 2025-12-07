# ATVI-textbook-tool
对齐式文本差异指数工具（ATVI 工具，Python 版）  
**Aligned Textual Variation Index for Textbook Comparison**

本仓库提供一个基于 Python 的小工具，用于分析多本语料在**同一对齐位置**上的用词差异。 
下载脚本后，运行，程序会自动弹出文件选择窗口，请选择你整理好的 CSV 文件即可。

主要功能包括：
- 计算每一行（语义点 / 句法位置）的**词汇变异度（Variation Index）**
- 计算每两本教材（或其他平行文本）之间的**相似度（Text Similarity）**
- 绘制：
  - 变异度最高的若干语义点条形图
  - 文本相似度热力图

适用于：  
- 多版本教材比较  
- 历时语言演变研究  
- 翻译教材 vs 本土教材对比  
- 语体差异（如社评、消息、通讯等）的定量分析入门

---

## 1. 环境要求与安装
### 1.1 Python 版本

建议使用：

- Python 3.8 及以上

### 1.2 安装所需库
pandas
matplotlib
numpy

## 2. 致谢与引用建议
如果你在论文或研究中使用了本工具，建议在方法部分引用：如需引用本工具，请使用以下格式：Wang, E. (2025). *ATVI-textbook-tool: A Python implementation of the Aligned Textual Variation Index for textbook comparison* [Computer software]. GitHub. https://github.com/Estherxixin/ATVI-textbook-tool
