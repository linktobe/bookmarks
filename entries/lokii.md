---
title: Lokii
repo: huangy7/lokii
license: MIT
language: Rust
gh_stars: 172
pushed: 2026-11-25
added: 2026-11-25
met: 开箱即用, 维护活跃, 文档充分, 版本规范
why_runs: 提供 Homebrew cask 与两种架构的 dmg，装完授予磁盘权限即可搜
why_alive: 最近一次提交于 2026-11-25
why_docs: README 覆盖安装、命令行用法、与 Spotlight 及启动器的对比
why_release: 当前版本 v0.2.0，遵循语义化版本并附发布说明
why_demo: 未通过：tests 下为测试代码，不计为示例
one_liner: 在 macOS 上重建 Everything 式的即时文件名搜索，Rust 索引配原生 AppKit 界面。
tags: macOS, 搜索, Rust
---
## 解决的问题

Windows 上的 Everything 靠 NTFS 主文件表建索引，输入即出结果。macOS 没有对应物：Spotlight 面向全量元数据，索引隐藏目录、构建产物与 node_modules 时常跳过或延迟；Raycast 与 Alfred 的文件搜索又复用 Spotlight 那套索引，Spotlight 慢，它们一起慢。

Lokii 自己建一套索引：Rust 写的内存倒排索引，经 UniFFI 桥到 Swift 与 AppKit 的原生界面，用 FSEvents 做文件系统的增量同步，启动时重放离线期间的差异而不重扫磁盘。五十万文件下查询在亚毫秒级，常驻内存不到一百 MB。

查询不只支持子串：通配符、正则、模糊匹配、路径段（src/main.rs）、目录过滤（结尾加斜杠）、in: 限定范围；中文支持拼音首字母与全拼，简繁双向互通。

另有一个命令行工具走本地 Unix socket 直连运行中的应用，共享同一份索引，可输出 JSON 供脚本消费，也可接 Alfred。窗口用 ⌘⇧Space 唤起，空格 Quick Look，回车在访达中显示。

## 评分依据

- **开箱即用**：提供 Homebrew cask 与两种架构的 dmg，装完授予磁盘权限即可搜。
- **维护活跃**：最近一次提交于 2026-11-25。
- **文档充分**：README 覆盖安装、命令行用法、与 Spotlight 及启动器的对比。
- **版本规范**：当前版本 v0.2.0，遵循语义化版本并附发布说明。
- **有示例**：未通过。tests 下为测试代码，不计为示例。

## 注意事项

仅 macOS 13 以上，分 Apple Silicon 与 Intel 两个包。首次启动要授予完全磁盘访问权限，没授全索引会缺目录，表现是搜不到某些文件夹。

README 里标注的亚毫秒与十毫秒级数据是核心进程测量，作者自己写明整机表现仍待验证。

版本 0.2.0，设置项与索引格式还可能调整。

无遥测、无联网，文件名与查询不出本机。

## 不适用场景

- Windows 或 Linux 桌面，那边已有成熟方案。
- 需要按文件内容而非文件名检索。
