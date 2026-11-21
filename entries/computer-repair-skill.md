---
title: computer-repair-skill
repo: 88lin/computer-repair-skill
license: AGPL-3.0
language: Python
gh_stars: 669
pushed: 2026-11-16
added: 2026-11-21
met: 维护活跃, 文档充分, 版本规范
why_runs: 未通过：属于 Skill 形态，需装入支持 Skill 的客户端；其命令亦受运行账户权限限制
why_alive: 最近一次提交于 2026-11-16
why_docs: 随仓库提供 docs、tests、tools 目录及各平台 playbook
why_release: 当前版本 v1.3.0；Skill 包形式，覆盖 Windows / macOS / Linux
why_demo: 未通过：内容为 playbook 文档，无示例工程
one_liner: 覆盖 Windows、macOS 与 Linux 的系统维护技能包，以结构化 playbook 组织诊断、清理、迁移与故障排查。
tags: 系统维护, Skill
---
## 解决的问题

系统排障的常见做法是逐条试错，缺少可复用的判断顺序。该技能包将每类故障整理为 playbook：现象、检查项、处置方式与回滚路径，使排查过程具备可追溯性。

其覆盖面包括启动异常、性能下降、磁盘占用、驱动冲突、分区与数据恢复等。

## 评分依据

- **开箱即用**：未通过。该项目为 Skill 形态，需装入支持 Skill 的客户端；此外其命令（下载安装包、写入系统目录、修改注册表）受运行账户与文件沙箱限制，实际执行前需先确认前提。
- **维护活跃**：最近一次提交于 2026-11-16。
- **文档充分**：随仓库提供 docs、tests、tools 目录及各平台 playbook。
- **版本规范**：当前版本 v1.3.0，有正式 release。

## 注意事项

许可证为 AGPL-3.0。个人使用无碍；若将相关能力封装为对外服务，需依条款开放源代码。

## 不适用场景

- 运行环境不具备管理员权限时，涉及系统目录与注册表的步骤无法执行。
- 需要无人值守批量处置时，该项目的多数步骤仍要求人工确认。
