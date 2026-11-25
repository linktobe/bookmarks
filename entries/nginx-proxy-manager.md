---
title: Nginx Proxy Manager
repo: NginxProxyManager/nginx-proxy-manager
license: MIT
language: JavaScript
gh_stars: 34875
pushed: 2026-11-23
added: 2026-11-25
met: 开箱即用, 维护活跃, 文档充分, 版本规范
why_runs: docker compose 起来，用默认账号进 81 端口就能加第一个反代
why_alive: 最近一次提交于 2026-11-23
why_docs: 文档站分安装、代理主机、SSL、访问控制与故障排查
why_release: 当前版本 v2.17.1，遵循语义化版本并按特性发布
why_demo: 未通过：仓库内是完整程序，docs 为文档而非示例
one_liner: 给 Nginx 加一个网页管理面板，反代、证书、访问控制点几下配完。
tags: 反向代理, 自托管, Nginx
---
## 解决的问题

给自建服务配 Nginx 反代，要写 server 块、配 upstream、申请证书、设重定向，改一次配置就 `nginx -t` 再 reload。忘了一行分号，站点就 502。

这个项目把 Nginx 包进一个容器，前面加一层网页面板：添加代理主机填域名与内网地址即可，SSL 证书一键申请（Let's Encrypt，自动续期），访问列表、重定向、404 主机、TCP/UDP 转发都在界面上配。配置落成 Nginx 的 conf 文件，仍可以直接改。

## 评分依据

- **开箱即用**：docker compose 起来，用默认账号进 81 端口就能加第一个反代。
- **维护活跃**：最近一次提交于 2026-11-23。
- **文档充分**：文档站分安装、代理主机、SSL、访问控制与故障排查。
- **版本规范**：当前版本 v2.17.1，遵循语义化版本并按特性发布。
- **有示例**：未通过。仓库内是完整程序，docs 为文档而非示例。

## 注意事项

默认管理员账号是 `admin@example.com` 与 `changeme`，暴露到公网前必须先改，否则等于把管理面板送人。

它是反向代理，不是防火墙：访问控制只到 IP 白名单一层，要认证得另配。面板本身支持基本认证与 TOTP，建议两者都开。

升级走镜像 tag，跨大版本先看发布说明与数据库迁移；配置文件与数据库都在挂载卷里，迁移前备份整个 volume。前端是 React，后端是 Node 与 Nginx，资源占用比裸 Nginx 高。

## 不适用场景

- 需要 Lua 扩展与复杂流量编排的网关场景。
- 要求配置完全版本化、由代码管理的部署。
- 低配设备上跑多个实例。
