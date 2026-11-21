---
title: Agent-Reach
repo: Panniantong/Agent-Reach
license: MIT
language: Python
gh_stars: 113608
pushed: 2026-11-08
added: 2026-11-21
met: 维护活跃, 文档充分, 版本规范
why_runs: 未通过：需安装 uv 与专用浏览器栈，部分平台另需登录
why_alive: 最近一次提交于 2026-11-08
why_docs: SKILL.md 提供命令列表与统一返回结构说明
why_release: 当前版本 v1.6.1；以 Python 包分发，需 Python 3.10+ 与 uv，无独立安装包
why_demo: 未通过：仓库无示例工程，用法以命令示例写在文档中
one_liner: 整合十余个平台的读取与搜索能力，以单一命令行接口对外提供，无需支付 API 费用。
tags: 抓取, 自动化
---
## 解决的问题

Agent 获取互联网内容通常需要接入多套 API 并分别适配。该项目将哔哩哔哩、知乎、Reddit、YouTube、小红书、X 等平台的访问方式收敛为同一组命令：

```bash
agent-reach channels
agent-reach read <任意链接>
agent-reach bilibili search "大模型"
```

输出统一为同一 JSON 结构，错误亦统一为一套错误码（`NEED_LOGIN`、`UPSTREAM_BROKEN`、`RATE_LIMITED` 等）。

## 评分依据

- **开箱即用**：未通过。文档所列安装链路包含 uv、专用浏览器栈与若干平台登录，未达到开箱即用的标准。
- **维护活跃**：最近一次提交于 2026-11-08。
- **文档充分**：SKILL.md 提供命令列表与统一返回结构说明。
- **版本规范**：当前版本 v1.6.1，遵循语义化版本。

其设计价值高于渠道价值，两点尤可借鉴：其一，一个动作绑定一条有序的后备工具链，主方案失效时自动降级；其二，将反爬验证页与正文严格区分，判定需同时命中页面结构与反爬标记。

## 不适用场景

- 仅需读取公开网页时，单一阅读接口即可满足，无需引入整套方案。
- 不具备多平台账号与登录维护条件时，渠道维护成本将高于代码本身。
