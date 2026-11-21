---
title: OpenMotion
repo: nexu-io/openmotion
license: Apache-2.0
language: TypeScript
gh_stars: 14244
pushed: 2026-11-21
added: 2026-11-21
met: 维护活跃, 文档充分, 版本规范, 有示例
why_runs: 未通过：需 Node.js 22 及以上与 npm 安装，或经由 ChatGPT 与 Agent Skill 接入
why_alive: 最近一次提交于 2026-11-21
why_docs: README 提供三种接入方式、安装命令与导出说明，另有 Motion.md 指南
why_release: 当前版本 v0.2.0；以 npm 应用与 Agent Skill 形式分发，支持 macOS 与 Windows
why_demo: docs 下的示例与模板目录提供可直接套用的成品
one_liner: 开源动态图形工作室，可将参考视频转为可编辑动效，并导出为各平台竖屏或横屏视频。
tags: 视频, 动效, Agent
---
## 解决的问题

制作动态图形通常依赖商业软件，参考视频中的动效难以拆解复用，品牌元素也难以批量套用。该项目以「参考视频 → 可编辑动效 → 导出成片」为链路，内置品牌套件与数百份动效指南，并提供面向 Agent 的使用方式。

## 评分依据

- **开箱即用**：未通过。需 Node.js 22 及以上并使用 npm 安装，亦可经 ChatGPT 或 Agent Skill 接入，但仍需前置环境。
- **维护活跃**：最近一次提交于 2026-11-21。
- **文档充分**：README 提供三种接入方式、安装命令与导出说明，另有动效指南库。
- **版本规范**：当前版本 v0.2.0，以 npm 应用与 Agent Skill 形式分发，安装脚本覆盖 macOS 与 Windows。
## 不适用场景

- 仅需剪辑而不涉及动效设计时，宜直接使用常规剪辑工具。
- 团队不接受 Node.js 工具链时，接入成本较高。
