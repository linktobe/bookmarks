---
title: PaddleOCR
repo: PaddlePaddle/PaddleOCR
license: Apache-2.0
language: Python
gh_stars: 93280
pushed: 2026-09-16
added: 2026-11-26
met: 开箱即用, 维护活跃, 文档充分, 版本规范, 有示例
why_runs: pip 装好框架与 paddleocr，一条 paddleocr ocr -i 就能把图片读成带坐标的文字
why_alive: 最近一次提交于 2026-09-16
why_docs: 安装页给出可直接复制的 pip 命令，快速开始页从单图识别写到版面与表格
why_release: 当前版本 3.7.0，三段式版本号，逐版发布正式版
why_demo: api_sdk 下有 Go 与 TypeScript 的 examples，deploy 里有可运行的 android_demo 与 avh 演示脚本
one_liner: 把图片与 PDF 读成带坐标的结构化文字，一百多种语言、版面与表格解析都在同一套接口下。
tags: OCR, 文档解析, 中文识别
---
## 解决的问题

扫描件与截图里的文字无法检索；PDF 若是图片，进了检索库就是空文本；拍照的表格要重敲一遍。通用 OCR 常常只回一行行文字，标题、段落、表格的层级丢失，表格还原成错位的文本流。

PaddleOCR 把流程拆成可组合的几段：检测文本框、识别文字，再按需接版面分析与表格结构化，输出带坐标与层级的结果。3.x 把 PP-OCR、PP-StructureV3 与 PaddleOCR-VL 收进同一套命令行与 Python 接口，中英混排、竖排、手写体各有对应模型，文档解析可以直接转成 Markdown。

## 评分依据

- **开箱即用**：`python -m pip install paddleocr` 装好后，`paddleocr ocr -i 图片` 即输出文字与坐标框。
- **维护活跃**：最近一次提交于 2026-09-16。
- **文档充分**：安装页给出可直接复制的 pip 命令，快速开始页从单图识别写到版面与表格。
- **版本规范**：当前版本 3.7.0，三段式版本号，逐版发布正式版。
- **有示例**：api_sdk 下 Go 与 TypeScript 的 examples、deploy 里的 android_demo 与 avh 演示脚本均可运行。

## 注意事项

框架本体不小：paddlepaddle 的 CPU 轮子有数百 MB，`paddleocr[all]` 还要更多，首次运行另外下载模型权重。

框架与模型版本要配套，文档把 paddlepaddle 锁在 3.2.0 上；版本错配是最常见的第一处报错。

CPU 可以跑，速度随分辨率与批大小变化；长文档、高分辨率扫描件建议用 GPU。

识别质量对倾斜、模糊、低对比度敏感，必要时先做纠偏与二值化。

README 现在只给入口，真正的操作步骤在文档站（中英双语），克隆下来并不等于能立刻跑通。

## 不适用场景

- 只识别零星几张图，不愿为此装数百 MB 依赖。
- 需要精确还原手写公式、乐谱一类特殊符号。
- 运行环境内存很小，又只能离线部署。
