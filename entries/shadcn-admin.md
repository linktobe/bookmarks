---
title: shadcn-admin
repo: satnaing/shadcn-admin
license: MIT
language: TypeScript
gh_stars: 16930
pushed: 2026-09-10
added: 2026-11-21
met: 开箱即用, 维护活跃, 文档充分, 版本规范
why_runs: 克隆后执行 pnpm install 与 pnpm run dev 即可打开完整后台界面
why_alive: 最近一次提交于 2026-09-10
why_docs: README 列出功能清单与安装运行步骤，并附界面截图
why_release: 当前版本 v2.2.1；以源码模板分发，需 Node 与 pnpm 环境
why_demo: 未通过：仓库即模板应用本身，未附带独立示例工程
one_liner: 基于 shadcn/ui 与 Vite 的后台管理界面模板，内置响应式布局与可访问性处理。
tags: 前端, 模板, 后台
---
## 解决的问题

后台管理界面存在大量重复工作：侧边栏、表格、表单、主题切换、权限路由，每个项目都要重做一遍，且响应式与可访问性容易漏。该模板把这些整理成可复用的组件与页面，克隆后即可在既有结构上改业务逻辑。

## 评分依据

- **开箱即用**：通过。克隆后执行 `pnpm install` 与 `pnpm run dev` 即可打开完整界面。
- **维护活跃**：最近一次提交于 2026-09-10。
- **文档充分**：README 列出功能清单与安装运行步骤，并附界面截图。
- **版本规范**：当前版本 v2.2.1；以源码模板分发，需 Node 与 pnpm 环境。
- **有示例**：未通过。仓库即模板应用本身，未附带独立示例工程。

## 不适用场景

- 需要开箱即用的后端与数据库时，该模板只提供前端界面。
- 项目不使用 shadcn/ui 时，样式体系改造的成本可能高于自建。
