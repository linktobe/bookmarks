---
title: CLI-Anything
repo: HKUDS/CLI-Anything
license: Apache-2.0
language: Python
gh_stars: 64802
pushed: 2026-11-20
added: 2026-11-25
met: 开箱即用, 维护活跃, 文档充分, 版本规范, 有示例
why_runs: pip 安装 cli-anything-hub 后一条命令装好现成 CLI 即可调用
why_alive: 最近一次提交于 2026-11-20
why_docs: README 分两条路径写全安装、生成与 refine 流程，各宿主另有专门章节
why_release: 当前版本 v0.4.0，遵循语义化版本并附发布说明
why_demo: 每个软件目录下都留有成套生成的 CLI 与测试，可直接读或跑
one_liner: 给桌面软件补一层命令行，让智能体不必靠截图与坐标去操作它们。
tags: Agent, 命令行, 工具链
---
## 解决的问题

智能体操作软件，眼下两条路都不顺：一是让它看截图点坐标，界面一改就失效；二是为每个软件单写一套接口，写不完。

CLI-Anything 的判断是给软件补一层命令行——命令行天然可组合、输出可解析、状态可回滚，正是智能体擅长的形状。它给两条使用路径。

一条是现成的：pip 装 cli-anything-hub，从注册表挑一个别人写好的 CLI，装完即用。注册表覆盖七十余款软件，从 Blender、GIMP、Krita、Inkscape、FreeCAD、QGIS 到 LibreOffice、Godot、OBS、Zotero、Joplin。

另一条是生成：把插件装进编码智能体，对着一个软件或代码库跑七阶段流水线——分析源码把界面动作映射到 API、设计命令组与状态模型、用 Click 实现带 REPL 与 JSON 输出及撤销重做的 CLI、写测试计划、补测试、写文档、打包装进 PATH。之后可再跑 refine，按能力缺口迭代加命令。

仓库另附技术报告与两千余条通过的测试，生成的 CLI 各自带一份技能说明。

## 评分依据

- **开箱即用**：pip 安装 cli-anything-hub 后一条命令装好现成 CLI 即可调用。
- **维护活跃**：最近一次提交于 2026-11-20。
- **文档充分**：README 分两条路径写全安装、生成与 refine 流程，各宿主另有专门章节。
- **版本规范**：当前版本 v0.4.0，遵循语义化版本并附发布说明。
- **有示例**：每个软件目录下都留有成套生成的 CLI 与测试，可直接读或跑。

## 注意事项

生成的 CLI 只是外壳，上游软件本体要自己安装。Windows 上的 Claude Code 走 bash，需装 Git for Windows（含 cygpath）或改用 WSL，否则会报 cygpath 找不到。

插件在不同编码智能体里的安装方式不同：Claude Code 走插件市场，命令要带命名空间前缀；Codex 用 $ 形式；其余多数走 npx skills。命令不生效时先确认插件是否已加载，再考虑换写法。

注册表里的第三方 CLI 质量不一，安装前先看它自己的测试与维护状态。生成的命令覆盖面取决于分析阶段读到多少源码，闭源软件只能靠文档与反复试错。

## 不适用场景

- 只有一次性的简单操作，写 CLI 的成本高于手动点几下。
- 目标软件本身已提供完整的命令行接口。
