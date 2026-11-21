---
title: guizang-ppt-skill
repo: op7418/guizang-ppt-skill
license: AGPL-3.0
language: HTML
gh_stars: 30200
pushed: 2026-10-30
added: 2026-11-21
met: 解决问题, 维护活跃, 文档充分, 版本规范
why_runs: 未通过：属 Skill 形态，需装入支持 Skill 的 Agent 客户端
why_real: 生成可直接放映的网页幻灯片，排版质感与演讲者支持往往需反复调校
why_alive: 最近一次提交于 2026-10-30
why_docs: README 给出安装命令、模板说明与校验脚本用法
why_release: 当前版本 v1.1.0；以 Agent Skill 形式分发，需在支持 Skill 的客户端中安装，无独立安装包
one_liner: 面向 Agent 的幻灯片生成技能，输出自带演讲者视图的单文件 HTML 演示文稿。
tags: 演示文稿, Skill
---
## 解决的问题

用 AI 生成幻灯片时，常见结果是排版粗糙、无法直接放映。该技能提供杂志风与瑞士版式两套模板，产出为单文件 HTML，内置演讲者视图与观众屏，且校验脚本可检查放映模式是否可用。

## 评分依据

- **开箱即用**：未通过。该项目为 Skill 形态，需装入 Claude Code、Cursor 等支持 Skill 的客户端。
- **解决问题**：通过。
- **维护活跃**：最近一次提交于 2026-10-30。
- **文档充分**：README 给出安装命令、模板说明与校验脚本用法。
- **版本规范**：当前版本 v1.1.0，以 Agent Skill 形式分发，需在支持 Skill 的客户端中安装，无独立安装包。
## 注意事项

许可证为 AGPL-3.0。个人使用无碍；若将产出的服务能力对外提供，需依条款开放源代码。

## 不适用场景

- 需要 PowerPoint 或 Keynote 源文件时，该技能输出的是网页而非可编辑演示文档。
- 客户端不支持 Skill 时，需改为手动拷贝模板与脚本。
