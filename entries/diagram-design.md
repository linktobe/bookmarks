---
title: diagram-design
repo: cathrynlavery/diagram-design
license: MIT
language: HTML
gh_stars: 69400
pushed: 2026-11-19
added: 2026-11-21
met: 维护活跃, 文档充分
why_runs: 未通过：该项目为 Skill 形态，需装入支持 Skill 的客户端方可使用
why_alive: 最近一次提交于 2026-11-19
why_docs: README 提供完整规范说明与自检脚本用法
why_release: 未通过：无 release，仅提供源码与设计规范（单文件 HTML 与内联 SVG），无安装包
one_liner: 面向 Agent 的图表设计规范，产出为单文件 HTML 与内联 SVG，覆盖架构图、流程图、时序图等 45 类图型。
tags: 设计, 图表
---
## 解决的问题

Agent 生成图表通常只有两种结果：Mermaid 一类的通用样式（圆角框、灰底），或纯文本示意。该规范提供第三种选择——编辑排版风格的手绘图形：单一强调色、1 像素描边、4 像素网格、无阴影。

产出为自包含 HTML，图形以内联 SVG 手写，不依赖任何图表库。

## 评分依据

- **开箱即用**：未通过。该项目为 Skill 形态，需装入 Claude Code、Codex 等支持 Skill 的客户端，单独打开仓库无法看到成品。
- **维护活跃**：最近一次提交于 2026-11-19。
- **文档充分**：README 提供完整规范说明与自检脚本用法。
- **版本规范**：未通过。仓库无 release，仅提供源码与设计规范。

## 不适用场景

- 内部讨论需要快速对齐思路时，随手绘制示意即可，套用规范反而降低效率。
- 需要图形可被他人再次编辑时，该规范输出静态 HTML 与 SVG，不同于 draw.io、Figma 一类可交互源文件。
