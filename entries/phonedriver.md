---
title: phonedriver
repo: hridaya423/phonedriver
license: AGPL-3.0
language: Rust
gh_stars: 385
pushed: 2026-11-25
added: 2026-11-26
met: 维护活跃, 文档充分, 版本规范
why_runs: 未通过：要先有 adb 能连上的模拟器或真机，空机器上装模拟器本身就超过十五分钟
why_alive: 最近一次提交于 2026-11-25
why_docs: README 给出注册 MCP 的命令与快照、点按示例，另有 docs、SKILL.md 与 llms.txt
why_release: v0.1.7，语义化三段式，附各平台预编译产物
why_demo: 未通过：演示以视频形式放在 .github/assets，仓库内没有可运行的示例工程
one_liner: 把手机界面读成带编号的文本快照交给 agent 操作，碰上付款这类按钮会先停下来问人。
tags: MCP, 手机自动化, Android
---
## 解决的问题

让 agent 操作手机，常见做法是截图交给视觉模型：一屏一张图，token 消耗大，坐标靠模型估，界面一变就失效。

phonedriver 改读无障碍树，把屏幕转成带编号的文本快照，agent 用 `@e24` 这样的引用点按，两次快照之间给出增加、消失、变化三类行。设备侧，Android 通过 adb 推一个 Java 助手过去读界面，iOS 在模拟器里跑一个 XCTest。作者在九个只靠手机才能完成的任务上对比三个 MCP 服务器，称 token 用量约为 mobile-mcp 的七分之一。

## 评分依据

- **开箱即用**：未通过。要先有 adb 能连上的 Android 模拟器、开了 USB 调试的真机，或 Mac 上的 iOS 模拟器；空机器上装模拟器本身就超过十五分钟。
- **维护活跃**：最近一次提交于 2026-11-25。
- **文档充分**：README 给出注册 MCP 的命令与 snapshot、tap 示例，另有 docs 目录、SKILL.md 与 llms.txt。
- **版本规范**：v0.1.7，语义化三段式，附各平台预编译产物。
- **有示例**：未通过。演示以视频形式放在 .github/assets，仓库内没有可运行的示例工程。

## 注意事项

设备是前置条件：Android 模拟器要 adb，真机要开 USB 调试，iOS 模拟器要 Mac 与 Xcode；没有设备时它会直接报出缺什么。

`npx -y phonedriver init` 会把自己写进本机找得到的 agent 配置（Claude Code、Codex、Cursor、VS Code、Gemini CLI），安装前先看清改了哪个文件。

点击落在 Pay、Buy now、Place order、Transfer 一类按钮上时会暂停等确认，识别按十一种语言的按钮文字做，这是设计的一部分而非故障。

2026 年 11 月建库，版本 0.1.x，命令与返回格式都还在变。

只读命令（snapshot、screenshot、wait、logs、network）不需要授权，其余动作要。

## 不适用场景

- 界面上没有无障碍树可读的场景（游戏、自绘 UI）。
- 需要逐帧精确坐标、模拟真人手势的测试。
- 手边没有任何能连上的设备或模拟器。
