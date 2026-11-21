---
title: AutoClip
repo: zhouxiaoka/autoclip
license: MIT
language: Python
gh_stars: 12412
pushed: 2026-11-21
added: 2026-11-21
met: 维护活跃, 文档充分, 版本规范
why_runs: 未通过：需下载桌面版并配置模型服务或本地模型后方可出片
why_alive: 最近一次提交于 2026-11-21
why_docs: 提供安装指南、常见问题与 CLI / MCP 说明
why_release: 当前版本 v1.5.8；桌面版支持 macOS Apple Silicon 与 Windows x64，另有 Docker 与 CLI / MCP 两种接入方式
one_liner: 将播客、访谈与课程等长视频一键剪成短视频的桌面工具，含字幕、封面与发布文案。
tags: 视频, 剪辑, 桌面应用
---
## 解决的问题

长视频转短视频需要反复完成同一组动作：找选题、切片、上字幕、配封面、写发布文案。该项目把这条链路收进一个桌面工具：贴入链接或本地文件，选定目标平台，产出视频、封面与文案；剪辑与渲染在本机完成，分析模型可自选。

支持平台包括抖音、小红书、B 站、TikTok、Reels、YouTube Shorts 与 YouTube。

## 评分依据

- **开箱即用**：未通过。需下载桌面版并在设置中配置模型服务（或先在本地启动 Ollama、LM Studio），完成配置后才可出片。
- **维护活跃**：最近一次提交于 2026-11-21。
- **文档充分**：提供安装指南、常见问题与 CLI / MCP 说明。
- **版本规范**：当前版本 v1.5.8；桌面版支持 macOS Apple Silicon 与 Windows x64，Linux 与自建服务可走 Docker，批量处理与接入 Agent 可用 CLI / MCP（需 Python 3.10+ 与 FFmpeg）。

## 注意事项

软件本身免费，云端模型按量计费。若不愿产生调用费用，可改用本地模型服务。

## 不适用场景

- 需要精细到帧的剪辑决策时，仍需回到常规剪辑软件。
- 机器性能不足时，本地转写与渲染耗时较长。
