# 在受限网络下部署 Hermes（中国大陆场景）

一次完整的踩坑记录：在 Debian 12 上部署 Hermes Agent + Web dashboard，全程尽量走国内镜像，并绕过 GitHub 的**按 IP 黑洞**。

> 文中所有主机地址、端口、路径均为占位符。

## 结论速查

| 环节 | 用什么 | 为什么 |
| --- | --- | --- |
| PyPI 包 | `UV_DEFAULT_INDEX=https://mirrors.aliyun.com/pypi/simple/` | 实测阿里云 **9.8 MB/s**，清华 1.9 MB/s |
| Python 解释器 | `UV_PYTHON_INSTALL_MIRROR=https://registry.npmmirror.com/-/binary/python-build-standalone/` | uv 官方支持的国内镜像 |
| npm | `NPM_CONFIG_REGISTRY=https://registry.npmmirror.com` | |
| 源码仓库 | `HERMES_REPO_URL=git@github.com:NousResearch/hermes-agent.git` | SSH 与 HTTPS 都实测可用；吞吐随时段波动极大（见坑三/坑五），用哪条要现测 |
| 其余产物 | **不动** | 走 `hermes-assets.nousresearch.com`（Nous 自家 CDN，国内可达且不慢） |

---

## 坑一：安装器会屏蔽 uv / pip 的配置文件

`install.sh` 开头就执行了：

```bash
export UV_NO_CONFIG=1
```

**后果**：写 `~/.config/uv/uv.toml`、`~/.config/pip/pip.conf` 对**安装过程完全无效**。镜像只能通过**环境变量**传入：

```
UV_DEFAULT_INDEX            # uv 的主索引
PIP_INDEX_URL               # pip
UV_PYTHON_INSTALL_MIRROR    # uv 管理的 Python 解释器
```

配置文件**仍然值得写** —— 安装完成后 `hermes` 内部调用 pip/uv 时会读（`pm/environment.py` 里有专门的 pip-mirror 桥接逻辑）。

**TOML 顺序坑**：写 `uv.toml` 时顶层键必须放在 `[[index]]` **之前**，否则会被解析成上一个 table 的键：

```toml
python-install-mirror = "https://registry.npmmirror.com/-/binary/python-build-standalone/"

[[index]]
url = "https://mirrors.aliyun.com/pypi/simple/"
default = true
```

## 坑二：`HERMES_REPO_URL` 可以换掉克隆地址

`install.sh` 里是：

```bash
REPO_URL="${HERMES_REPO_URL:-https://github.com/NousResearch/hermes-agent.git}"
```

→ 设这个环境变量即可把克隆导向 SSH 或镜像。

顺带了解安装器的克隆行为：它是 **blobless 部分克隆**

```bash
git clone --filter=blob:none --branch main "$REPO_URL" <staged>/tree
```

即拉全部提交和树、文件内容按需取。失败重试 3 次，再失败退化为「只拉历史、不检出」。**卡住 90% 是在检出阶段**（按需拉 blob 时被杀）。

## 坑三：第三方 GitHub 镜像 —— 要测真实克隆，而且必须测对模式

| 镜像 | `git ls-remote` | 真实 `git clone --depth 1` |
| --- | --- | --- |
| `gitclone.com` | ✅ 0.74s | ❌ **两次独立测试都是 60s 零字节** |
| `gh-proxy.com` | ✅ 1.81s | ✅ 350MB / **8s** —— 可以很快，但波动大 |
| `ghproxy.net` | ✅ 但**慢到 28.7s**（连轻量协议都这样） | 未测，光延迟就不值得 |
| `kkgithub.com` / `bgithub.xyz` / `github.moeyy.xyz` / `ghfast.top` / `hub.nuaa.cf` | ❌ 不可达 | — |

**教训一**：`ls-remote` 只走轻量协议，**完全不能代表能否克隆**。要跑真实 `git clone` 计时。

**教训二（最隐蔽，也是最贵的一条）**：**必须用和安装器相同的克隆模式去测。**
同一台机器、同一时段实测：

| 模式 | 结果 |
| --- | --- |
| `--depth 1`（浅克隆） | ✅ **11 秒**完成，350 MB |
| 完整克隆（≈ 安装器行为） | ❌ **60 秒超时，零字节** |

安装器用的是 **blobless 部分克隆**（`--filter=blob:none`：拉全部提交和树、文件内容按需取），
它的重量级**接近"完整克隆"而不是浅克隆**。用 `--depth 1` 测出来的漂亮数字
**完全不能代表安装时的真实体验** —— 这就是"测速很漂亮、实际安装卡死"的根源。
（参考：该仓库体积约 **1229 MB**。）

**教训三**：**单次测速不可信。** 同一条 HTTPS 通路的 `--depth 1` 克隆，不同时刻分别测到过
**350MB/8s、/11s、/24s、/40s** —— 限速是**突发式**的。下结论前至少测两轮，
并且**顺序**测（并发会互相污染）。

## 坑四：GitHub 是「按 IP 黑洞」，不是整站封禁

同一台机器上同时存在：

```
github.com                      → 20.205.243.166   ← TCP 443 握手都完不成
api.github.com                  → 20.205.243.168   ← 通
codeload.github.com             → 20.205.243.165   ← 通
objects.githubusercontent.com   → 185.199.108-111  ← 通
140.82.112.3 / 113.3 / 121.3-6  → 全部通
```

**症状识别**：`ss -tnp` 里看到 `SYN-SENT` 到某个 GitHub IP 长期不进入 `ESTAB`，而且反复重试超时 —— 这就是按 IP 黑洞，**不是限速**。

**修法**（先备份 `/etc/hosts`）：

```bash
cp /etc/hosts /etc/hosts.bak-$(date +%Y%m%d)

# 逐个候选 IP 测，挑返回 200 的
for ip in 140.82.121.6 140.82.112.3 140.82.113.3 140.82.121.3; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 \
         --resolve github.com:443:$ip https://github.com/)
  echo "$ip -> $code"
done

# 钉一个可用的
echo "140.82.112.3 github.com" >> /etc/hosts
getent hosts github.com
```

恢复：`cp /etc/hosts.bak-<日期> /etc/hosts`

## 坑五：HTTPS 与 SSH 要实测，别猜

干净环境、**顺序**测（同时跑会互相污染），用 `--progress` 看瞬时值、用总字节÷总耗时看平均：

```bash
timeout -s KILL 60 git clone --depth 1 --progress <url> /tmp/mm > /tmp/mm.log 2>&1
du -sm /tmp/mm            # SIGKILL 让 git 来不及清理，残片可用于计量
tr '\r' '\n' < /tmp/mm.log | grep -E "MiB/s" | tail -2
```

某次实测：

| 通路 | 用时 | 平均吞吐 |
| --- | --- | --- |
| SSH `git@github.com:22` | 22s | **≈15.9 MB/s** |
| HTTPS `github.com:443` | 40s | ≈8.75 MB/s |

**两个陷阱**：

- `--progress` 报的是**瞬时**速率，接近 100% 时会突刺，别拿它当平均值。
- `codeload.github.com` 上的 Range 请求速率**完全不能代表** `git clone` 速率 —— 是不同的服务路径，实测差几十倍。

用 SSH 需要一把**已注册到 GitHub 账号**的密钥（公开仓库也要鉴权）：

```bash
ssh-keygen -t ed25519 -C "deploy" -f ~/.ssh/deploy_key -N ""
# 公钥加到 GitHub 后：
ssh -T git@github.com     # 期望 Hi <user>! You've successfully authenticated
```

想全局兜底，可让所有漏网的 HTTPS GitHub 地址都走 SSH：

```bash
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

## 坑六：`systemd-run` 起的任务没有 HOME / PATH

用 `systemd-run` 把长任务脱离 ssh 会话（比 `nohup ... &` 干净，也能绕开某些工具对前台 `&` 的限制）：

```bash
systemd-run --unit=myjob --description="long job" \
  --setenv=HOME=/root --setenv=USER=root --setenv=LOGNAME=root \
  --setenv=PATH=/root/.local/bin:/usr/local/bin:/usr/bin:/bin \
  bash /path/to/job.sh
```

**不注入 `HOME` 的后果**：

- 任何 `set -u` 且引用 `$HOME` 的安装脚本**立刻死**：`HOME: unbound variable`
- `ssh` / `git` 找不到 `~/.ssh/*` → **SSH 鉴权静默失败**（表现为"能连 GitHub 但鉴权不过"，极易误判成网络问题）

**双保险**：脚本自己也兜一层 —— `export HOME="${HOME:-/root}"`。

**另一个坑**：`systemd-run` 的 `--collect` **不接受参数**。写成 `--collect=no` 会直接报 `option '--collect' doesn't allow an argument` 并且**任务根本不启动**（很容易以为它跑了）。

## 坑七：`set -o pipefail` + `ssh -T ... | grep` 判断恒为失败

```bash
set -o pipefail
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "鉴权 OK"
else
    echo "回落慢通路"        # ← 永远走这里
fi
```

`ssh -T` 到 GitHub **成功时也返回 1**（GitHub 不提供 shell）。配合 `pipefail`，管道退出码取最右的**非零**状态 → 判断**恒为失败**，白白回落到慢通路，而且日志上看不出任何异常。

正确写法 —— 先把输出取出来，再用 `|| true` 兜住退出码：

```bash
out="$(ssh -T -o BatchMode=yes git@github.com 2>&1 || true)"
case "$out" in
  *"successfully authenticated"*) echo "✓ SSH 鉴权正常" ;;
  *) echo "✗ 回落 HTTPS"; printf '%s\n' "$out" ;;
esac
```

## 坑八：Hermes 的 Web UI 构建是 npm workspace

从源码里挖到的官方提示（`hermes_cli/main_dashboard.py`）：

```python
_PRE_BUILD_HINT = "  Pre-build first:  npm install --workspace web && npm run build -w web"
```

→ 必须在**仓库根目录**执行，不是 `cd web && npm run build`。
→ 产物落在 **`hermes_cli/web_dist/`**，不是 `web/dist/`。
→ `hermes dashboard --skip-build` 就是直接吃这个 dist。

## 坑九：pm 装的 node / npm 不在 PATH 上

Hermes 的包管理器（`pm`）把工具装在自己的目录：

```
$HERMES_HOME/tools/node-<version>-linux-x64/bin/
```

构建 web UI 前必须加进 PATH，否则直接 `npm: command not found`。

## Dashboard 的认证硬门槛

`hermes dashboard` 默认绑 `127.0.0.1:9119`。**非回环绑定必须有 auth provider**，而 `--insecure` 自 2026 年 6 月加固后已是 **no-op**：

> a public bind always requires an auth provider (password or OAuth).
> Bind 127.0.0.1 + tunnel to keep it local.

而配置用户名/密码**需要真实 TTY**（`getpass` 交互），从脚本/CI/非 PTY 环境里根本调不动。

→ **推荐做法**：绑 loopback + SSH 本地端口转发，零配置、零暴露面：

```bash
ssh -N -L 9119:127.0.0.1:9119 <user>@<host> -p <port>
# 本地浏览器打开 http://127.0.0.1:9119
```

**不要把 dashboard 挂到公网反向代理下** —— 它是一个能执行任意命令的入口。

## systemd 单元模板

```ini
[Unit]
Description=Hermes Agent Web Dashboard
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
Group=root

# 必须显式给 HOME —— systemd 服务默认没有
Environment=HOME=/root
Environment=USER=root
Environment=LOGNAME=root
Environment=PATH=/root/.hermes/tools/node-<version>-linux-x64/bin:/root/.local/bin:/usr/local/bin:/usr/bin:/bin

WorkingDirectory=/root
ExecStart=/root/.local/bin/hermes dashboard --host 127.0.0.1 --port 9119 --no-open --skip-build

Restart=always
RestartSec=5s
TimeoutStartSec=180

[Install]
WantedBy=multi-user.target
```

## 验证清单（别只看 `active (running)`）

| 断言 | 探针 |
| --- | --- |
| 真的绑定了端口 | `ss -tlnp \| grep :9119` |
| 页面真的能出 | `curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:9119/` → 200 |
| 开机自启 | `systemctl is-enabled <svc>` |
| 崩溃自愈有效 | `kill -9 $(systemctl show -p MainPID --value <svc>)`，`sleep 10` 后比对 PID |
| 没搞坏原有服务 | `systemctl is-active` 逐个查；确认 80/443 的占用者（nginx/openresty 等）仍在 |
| 部署健康度 | `hermes doctor` |

## 关于那个 `hermes` 更新锁

安装完成后 `$HERMES_HOME/.hermes-update-in-progress.lock` 可能残留（0 字节）。**不用手动删**：

`hermes_cli/update_lock.py` 的判定规则是 *"An owner is live while its pid is alive and its creation time still matches: **never by age**"* —— 持有它的 PID 早已退出，因此它不会被当成有效锁；无创建时间的旧格式标记还有 **20 分钟**上限自动老化。
