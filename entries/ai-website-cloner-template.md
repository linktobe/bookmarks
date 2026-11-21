---
title: AI Website Cloner Template
repo: JCodesMore/ai-website-cloner-template
license: MIT
language: TypeScript
gh_stars: 39578
pushed: 2026-11-10
added: 2026-11-21
met: 维护活跃, 文档充分, 版本规范
why_runs: 未通过：需 Node.js 24 以上，并配合具备浏览器访问能力的编码 Agent 使用
why_alive: 最近一次提交于 2026-11-10
why_docs: README 说明支持的 Agent、安装步骤与两种使用方式
why_release: 当前版本 v0.6.1，以仓库模板形式分发，需 Node.js 24 以上环境
why_demo: 未通过：以模板形式提供，未附带独立示例工程
one_liner: 把网址交给编码 Agent，按模板重新实现为可维护的 Next.js 应用的起始项目。
tags: Agent, 前端, 模板
---
## 解决的问题

参照某个站点重做页面时，人工提取结构、还原样式、整理组件往往耗时数小时。该模板把这件事交给编码 Agent：给出 URL，Agent 按既有目录约定分析页面并生成 Next.js 代码，产物是干净、可继续维护的工程，而不是直接照搬的 HTML。

README 标明推荐 Claude Code 配合 Opus 系列模型，同时支持 Codex、Cursor 与 OpenCode。

## 评分依据

- **开箱即用**：未通过。需 Node.js 24 以上，并配合具备浏览器访问能力的编码 Agent。
- **维护活跃**：最近一次提交于 2026-11-10。
- **文档充分**：README 说明支持的 Agent、安装步骤与两种使用方式。
- **版本规范**：当前版本 v0.6.1，以仓库模板形式分发。
- **有示例**：未通过。以模板形式提供，未附带独立示例工程。

## 注意事项

复刻他人站点涉及视觉设计与内容版权，用于商业项目前应确认授权与合规性；该模板适合作为结构参考与内部原型起点。

## 不适用场景

- 没有支持浏览器的编码 Agent 时，流程无法完整跑通。
- 需要像素级还原设计稿时，仍应由设计到前端的人工流程主导。
