---
title: uv
repo: astral-sh/uv
license: Apache-2.0
language: Rust
gh_stars: 92474
pushed: 2026-11-21
added: 2026-11-21
met: 开箱即用, 维护活跃, 文档充分, 版本规范
why_runs: 单文件分发，无需预装 Python 环境，解压后即可执行
why_alive: 提交频率接近每日
why_docs: 官方文档为每条命令提供可直接复制的示例
why_release: 当前版本 0.13.9；提供 Windows / macOS / Linux 独立二进制，亦可经 pip 安装
one_liner: 以 Rust 实现的 Python 包管理器，单文件分发，依赖解析速度显著高于 pip。
tags: 工具链, Python
---
## 解决的问题

Python 的依赖安装与环境管理长期存在三项成本：解析缓慢、环境相互污染、多版本共存困难。该工具以单个可执行文件同时承担 pip、virtualenv、pip-tools 与 pyenv 的部分职能。

```bash
uv venv .venv
uv pip install fastapi
uv run script.py        # 使用环境运行脚本，无需先激活
```

## 评分依据

- **开箱即用**：单文件分发，不依赖既有 Python 环境。
- **维护活跃**：提交频率接近每日。
- **文档充分**：文档站为每条命令提供可直接复制的示例。
- **版本规范**：当前版本 0.13.9，遵循语义化版本，每次发布均附说明。

## 不适用场景

- 团队既有环境已统一于 conda 生态，迁移成本高于收益。
- 需兼容 Python 3.7 及以下版本时，其依赖解析的兼容性不及 pip。
