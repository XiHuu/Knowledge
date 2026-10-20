# 用「自己的 Telegram 账号」订阅群消息并推 webhook：可选项目调研

调研时间 2026-10。需求：以**个人账号**（MTProto，非 Bot API）登录，群组有新消息时
推送到 HTTP endpoint。

## 为什么 Bot API 不行（这是需求的前提）

| | Bot API | 用户账号（MTProto） |
| --- | --- | --- |
| 能看到什么 | 机器人被拉进的群/频道 | **你账号已加入的全部**群组/频道 |
| 进群方式 | 需管理员拉入，通常还要管理员权限 | 不需要，你本来就在里面 |
| 历史消息 | 拿不到 | 能翻 |
| 成员列表 | 受限 | 能取 |
| 隐私模式 | 默认只收 `/` 命令与 @ 消息 | 无此限制 |

所以「机器人转 RSS / n8n 的 Telegram Trigger / Huginn / RSSHub 的 telegram 路由」
这一整类**都不满足需求** —— 它们全是 Bot API。

## 现成的「账号 + webhook」项目

### tlgrm —— 功能最对口，但项目状态是红灯

- PyPI `tlgrm`，源码 `github.com/ali-commits/tlgrm`，MIT，基于 Telethon
- 能力：`tlgrm login`（支持 QR）、`tlgrm listen --webhook-url URL` 实时推 JSON、
  `tlgrm daemon install` 装成 systemd 服务、媒体自动下载、可选本地 Whisper 转写
- 体检：**1 star / 0 fork / 2026-06-14 建库 / 2026-06-17 最后提交 /
  全部版本（0.1.3 → 0.3.2）在三天内发完**
- 判断：**架构和 CLI 设计正好是这个需求**，适合当参考实现读；但把它装上去、
  喂真账号 session，等于把账号控制权交给一个四个月没动的单人项目

### telegram-userbot-cli

- PyPI `telegram-userbot-cli` v0.6.0，Telethon userbot CLI，Apache-2.0
- 能力：登录（含 QR）、收发消息、群管、历史检索、会话名模糊匹配
- 代理：内置 `TELEGRAM_PROXY_TYPE` / `TELEGRAM_PROXY_HOST` / `TELEGRAM_PROXY_PORT`，
  README 明确写 "required when Telegram is unreachable directly"
- 缺：**没有 webhook daemon**，只做 CLI

### mtproto-cli

- `github.com/Call-me-Boris-The-Razor/mtproto-cli`
- 定位「给 AI agent 用的 MTProto 工具包」：CLI + **HTTP API** + Node.js 编程接口
- 能力：join、读讨论、搜消息、发消息
- 适合：要的是「本地起个 HTTP 服务，别的系统来问它」这个方向

## 底层库（自己写几十行）

| 库 | 语言 | 状态 | 备注 |
| --- | --- | --- | --- |
| **Telethon** | Python | v1.45.0，活跃 | 社区最大、文档最全、内置 python-socks 代理；`events.NewMessage` 直接够用 |
| **TDLib** | C++（多语言绑定） | 官方维护 | Telegram 自家客户端库，最「官方」，但集成重 |
| **Kurigram** | Python | v2.2.26，活跃 | **Pyrogram 的 fork** |
| **MadelineProto** | PHP | 活跃 | 老牌 userbot 常用 |

⚠️ **原版 Pyrogram 已停止维护** —— 社区在 Telethon 的 issue 里明确指出
"Pyrogram is no longer maintained"。要选 Pyrogram 请用 Kurigram。

## 三类风险

1. **账号风控**：第三方客户端本身 Telegram 是允许的（Telethon / TDLib 都是正规
   协议实现）。但两点是真的：新设备登录要验证码，官方 App 会收到「新设备登录」
   提醒；用账号做**批量加群 / 群发**极易被限流或封号。
   → **只读监听（从不发送）风险最低。**
2. **session 泄露 = 账号被完全接管**。session 文件等价于登录态：权限 600、
   绝不进 git、绝不传给第三方托管的服务。
3. **api_id / api_hash** 要在 `my.telegram.org/apps` 申请 —— 该站国内也连不上。

## 网络前提（中国大陆）

实测某台国内腾讯云机器（2026-10）：

| 目标 | 结果 |
| --- | --- |
| Telegram DC1–DC5 共 6 个 IP × 端口 443 / 5222 | **全部超时** |
| `example.com:443`、`github.com:443` | 正常 |

→ 是**针对 Telegram 的定向阻断**，不是整体断网。所以用户账号方案在国内自建，
必须过一层代理：

| 做法 | 需要什么 |
| --- | --- |
| 本地跑 + 你已有的代理（socks5） | 一台常开的机器 |
| 服务器跑 + socks5 跳到境外 | 一台境外跳板 |
| 自建 MTProxy | 一台境外机器（Telegram 官方代理协议） |
| 直接在境外 VPS 上跑 | 最省事 |

Telethon 的 `proxy=` 参数吃 `python_socks` 元组，`rdns=True` 时域名交给代理解析，
可规避本地 DNS 污染。

## 选型建议

| 你的诉求 | 看这个 |
| --- | --- |
| 想直接能跑、能接受先读代码 | `tlgrm`（当参考实现，别直接喂真号） |
| 要 CLI 管理账号、webhook 自己接 | `telegram-userbot-cli` |
| 要一个本地 HTTP 服务给别的系统调 | `mtproto-cli` |
| 要长期稳定、完全可控 | **Telethon 自己写**，核心就三件：登录 / `events.NewMessage(chats=...)` / POST |
