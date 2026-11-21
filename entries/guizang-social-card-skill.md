---
title: guizang-social-card-skill
repo: op7418/guizang-social-card-skill
license: AGPL-3.0
language: HTML
gh_stars: 8206
pushed: 2026-10-30
added: 2026-11-21
met: 维护活跃, 文档充分
why_runs: 未通过：属 Skill 形态，且渲染需 Node 与 Playwright
why_alive: 最近一次提交于 2026-10-30
why_docs: README 给出安装方式、模板与版式说明、渲染脚本用法
why_release: 未通过：仓库无 release，仅提供 Skill 源文件与渲染脚本
one_liner: 生成小红书图文与公众号封面套图的技能，内置杂志风与瑞士版式共 28 种布局。
tags: 设计, 图文, Skill
---
## 解决的问题

社交平台的图文内容通常需要成套排版：小红书长图要求节奏统一，公众号封面要求横竖两版成对。逐张制作耗时，且风格容易走样。该技能以版式系统的方式解决：单文件 HTML 编排，经 Playwright 渲染为 PNG，不需要前端构建链。

## 评分依据

- **开箱即用**：未通过。该项目为 Skill 形态，需装入支持 Skill 的客户端；出图另需 Node 与 Playwright。
- **维护活跃**：最近一次提交于 2026-10-30。
- **文档充分**：README 给出安装方式、模板与版式说明、渲染脚本用法。
- **版本规范**：未通过。仓库无 release，仅提供 Skill 源文件与渲染脚本。

## 注意事项

许可证为 AGPL-3.0。个人使用无碍；若将相关能力封装为对外服务，需依条款开放源代码。

## 不适用场景

- 需要精修摄影或真实测评类图片时，该技能提供的是版式与文字结构，图片仍依赖外部来源。
- 需要可继续编辑的设计源文件时，产物为 HTML 与 PNG，不同于 Figma 一类可协作文件。
