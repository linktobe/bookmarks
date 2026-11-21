---
title: DS Bot
repo: Fei2411/DS-Bot
license: Apache-2.0
language: JavaScript
gh_stars: 8592
pushed: 2026-11-21
added: 2026-11-21
met: 维护活跃, 文档充分, 版本规范
why_runs: 未通过：需先安装 DeepSeek Harness 并配置至少一个模型
why_alive: 最近一次提交于 2026-11-21
why_docs: 中英文 README 与部署文档，覆盖桌面端、Web 端与 Docker
why_release: 当前版本 v0.3.8；提供 Windows / macOS / Linux 桌面应用，另有 Web 与 Docker 部署方式
why_demo: 未通过：无独立示例工程
one_liner: 运行在 DeepSeek Harness 上的多机器人协作套件，支持主机器人、机器人间消息与群聊。
tags: Agent, 机器人, 协作
---
## 解决的问题

单个机器人难以承担长期、多角色的协作：分工、消息路由与群组上下文都需要自行搭建。该项目在 DeepSeek Harness 之上提供一套机器人团队：主机器人负责调度，机器人之间可以互相发消息，也可以加入群聊分别应答。

## 评分依据

- **开箱即用**：未通过。需先安装 DeepSeek Harness 并配置至少一个模型。
- **维护活跃**：最近一次提交于 2026-11-21。
- **文档充分**：中英文 README 与部署文档，覆盖桌面端、Web 端与 Docker。
- **版本规范**：当前版本 v0.3.8；提供 Windows、macOS 与 Linux 桌面应用，另有 Web 与 Docker 两种部署方式。
- **有示例**：未通过。无独立示例工程。

## 不适用场景

- 只需要单个对话机器人时，直接使用 Harness 自带能力即可。
- 未部署 DeepSeek Harness 时，该项目无法独立运行。
