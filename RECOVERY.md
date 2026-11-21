# 换机与灾难恢复

本文说明：当更换设备、重装系统，或当前设备损坏时，如何重新取得本仓库的控制权并继续发布。

**核心结论**：仓库内容已托管在 GitHub，不会因设备损坏而丢失。需要重建的只有**访问凭据**与**本地工作副本**。

---

## 一、需要重新准备的东西

| 项目 | 是否随设备丢失 | 说明 |
|---|---|---|
| 仓库代码与条目 | 否 | 托管在 GitHub，随时可克隆 |
| 发布流水线 | 否 | 定义在 `.github/workflows/publish.yml`，随仓库保留 |
| Pages 配置 | 否 | 属于仓库设置，存在 GitHub 服务端 |
| SSH 私钥 | **是** | 需重新生成并重新登记公钥 |
| 本地访问令牌（PAT） | **是** | 仅用于提升本地 API 配额，可按需重新生成 |
| `Dev/.secrets/` 目录 | **是** | 本地文件，从未进入版本库 |

---

## 二、新设备上的恢复步骤

### 1. 准备 git

安装 git 后确认可用：

```bash
git --version
```

### 2. 生成新的 SSH 密钥

```bash
ssh-keygen -t ed25519 -f ~/.ssh/gh_ed25519 -N "" -C "bookmarks"
```

若系统不允许写入 `~/.ssh`（受限账户、沙箱环境等），可改存到任意可写目录，后续用 `core.sshCommand` 指向该路径即可。

### 3. 登记公钥

1. 复制 `gh_ed25519.pub` 的全部内容
2. 打开 https://github.com/settings/ssh/new
3. Title 填 `新设备`，粘贴公钥，保存

> 若旧设备已损坏，建议先在 https://github.com/settings/keys 删除其中对应的旧公钥。

### 4. 克隆仓库

```bash
git clone git@github.com:linktobe/bookmarks.git
cd bookmarks
```

### 5. 配置提交身份

```bash
git config user.name  "bookmarks"
git config user.email "bookmarks@users.noreply.github.com"
```

### 6. 若密钥不在默认位置，指定 SSH 命令

```bash
git config core.sshCommand "ssh -i <私钥路径> -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile=<known_hosts路径>"
```

### 7. 验证

```bash
python src/build.py          # 本地生成站点，确认代码可运行
git push                     # 验证推送权限（无改动时可用 git push -u origin main）
```

---

## 三、常见环境问题

### git 无法通过 HTTPS 访问

部分 Windows 环境中，git 使用 schannel 后端会报：

```
schannel: AcquireCredentialsHandle failed: SEC_E_NO_CREDENTIALS (0x8009030e)
```

该版本 git 未编译 OpenSSL 后端，无法切换。**改用 SSH 即可**，本仓库已按此方式配置。

### 无法写入 `~/.ssh`

受限账户或沙箱环境下，`ssh-keygen` 可能无法在 `~/.ssh` 创建文件。处理方式：

- 将密钥生成到其他可写目录
- 用 `core.sshCommand` 指定私钥与 `known_hosts` 路径

### 本地 API 配额不足

`scripts/` 下的脚本调用 GitHub API。未认证时上限为 60 次/小时并按 IP 计算。配置只读令牌后提升至 5000 次/小时：

1. 打开 https://github.com/settings/tokens/new
2. Note 填 `bookmarks local readonly`，有效期按需选择
3. **不勾选任何 scope**（读取公开仓库无需权限）
4. 生成后保存到 `.secrets/github_token.txt`（位于仓库之外，无换行以外的多余字符）

脚本按以下顺序读取：环境变量 `GITHUB_TOKEN` / `GH_TOKEN` → 上述文件。

---

## 四、发布链路是否受影响

不受影响。Pages 的 Source 为 **GitHub Actions**，属于仓库设置；只要推送成功，流水线会自动构建并部署。

新设备上可做一次验证：在仓库 **Actions → 发布收藏夹 → Run workflow** 手动触发，确认运行成功。

---

## 五、极端情况

| 情况 | 处理方式 |
|---|---|
| 私钥丢失但设备可用 | 生成新密钥并登记，删除旧公钥即可 |
| 本地副本损坏 | 直接重新克隆；`public/` 为构建产物，无需保留 |
| 令牌泄露 | 在 https://github.com/settings/tokens 立即撤销并重新生成 |
| GitHub 账号无法登录 | 属于账号层面问题，需走 GitHub 账号恢复流程，仓库本身不受影响 |

---

## 六、日常维护提示

- 私钥与令牌**不得**放入仓库或提交记录
- 提交前可执行 `git status` 确认无误加入的敏感文件
- 每周一流水线会自动复查条目对应仓库的状态（失效、迁移、归档），无需人工干预
