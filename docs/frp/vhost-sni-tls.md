# frp vhost：基于 Host / SNI 的内网穿透

用 frp 把内网的 HTTP(S) 服务发布到公网 80/443，靠的是 frps 的 `vhostHTTPPort` 和 `vhostHTTPSPort`。

## 最反直觉的一点：HTTPS 是 SNI 透传，不是 TLS 终止

frp 作者 fatedier 在 [issue #4558](https://github.com/fatedier/frp/issues/4558) 里说得最清楚：

> **"`https` 这个代理类型名字有点误导 —— 它做的是基于 SNI 的 TLS 透传，不是 HTTPS 终止。真正的 TLS 握手发生在你的后端服务器上。"**

官方文档口径一致：

> **"frp 的 https 代理需要本地服务是 HTTPS 服务，frps 端不会做 TLS 终止。"**

推论：

| 问题 | 答案 |
| --- | --- |
| 证书装在哪 | **后端**（Nginx / Caddy / OpenResty） |
| frps 需要证书吗 | **不需要** |
| 后端只会 HTTP 怎么办 | 用 `https2http` 插件，证书配在 **frpc** 侧 |
| 是端到端加密吗 | 是，frps 只转发加密流、不解密 |

## 路由依据

| 公网端口 | 配置项 | 靠什么路由 |
| --- | --- | --- |
| 80 | `vhostHTTPPort` | **Host 头** |
| 443 | `vhostHTTPSPort` | **SNI**（TLS ClientHello 中的服务器名） |

**纯 IP 访问走不通 HTTPS vhost** —— IP 访问**不带 SNI**，路由不过去（[issue #3385](https://github.com/fatedier/frp/issues/3385) 有实证）。要按 IP 访问只能用 `type = "tcp"`。

## 最小可用配置

**frps.toml**

```toml
bindPort = 7000
auth.method = "token"
auth.token = "<强随机值>"

vhostHTTPPort  = 80
vhostHTTPSPort = 443
```

**frpc.toml**

```toml
serverAddr = "x.x.x.x"
serverPort = 7000

[[proxies]]
name = "web-http"
type = "http"
localIP = "127.0.0.1"
localPort = 8080
customDomains = ["example.com"]

[[proxies]]
name = "web-https"
type = "https"
localIP = "127.0.0.1"
localPort = 8443
customDomains = ["example.com"]
```

链路：

```
外网 → frps:80/443 ──(Host / SNI 路由)──→ frpc ──→ 后端 127.0.0.1:8080|8443
```

## 六个真会绊人的坑

### 1. frp 不改写 Host

透传时**后端看到的 Host 仍是公网域名**。所以后端 vhost 的 `server_name` 必须写公网域名，写 `127.0.0.1` 或内网名匹配不上。

实证见 [issue #1764](https://github.com/fatedier/frp/issues/1764)：有人让 frpc 的 `local_ip` 指向 `domain1.com`，后端仍然收到 `Host: domain2.com`。

### 2. 真实客户端 IP 默认全丢

不开 PROXY protocol 时，后端看到的客户端**永远是 `127.0.0.1`** —— WAF、限速、访问日志、防爬**全部失效**。

要开 `transport.proxyProtocolVersion = "v2"`，**并且后端 `listen` 必须同时加 `proxy_protocol`**：

```nginx
listen 8443 ssl proxy_protocol;
```

**两边不同时配会直接 `ERR_SSL_PROTOCOL_ERROR`**（issue #1764 里踩过）。

### 3. ACME 续期会被自己的 301 吃掉

证书在后端、后端在 frps 后面时，HTTP-01 挑战的路径是：

```
Let's Encrypt → frps:80 ─(Host 路由)→ frpc → 后端:8080
```

**能走通**，因为 vhost 按 Host 路由、不需要证书，没有循环依赖。

但前提是 `/.well-known/acme-challenge/` 那条 location 没被 301 跳转或鉴权规则拦掉 —— **这是续期失败最常见的原因**。想彻底省心用 **DNS-01**（acme.sh / Caddy 的 DNS provider），完全不依赖 80 端口。

### 4. HTTP/3 必须关掉

frp 的 vhost **只走 TCP**。后端开 QUIC/UDP 443 的话那部分流量 frps 根本不转发，客户端会静默降级或超时。要么关 h3，要么另配 frp 的 udp 代理（和 vhost 端口不是一回事）。

### 5. `customDomains` 是全局唯一的

同一个 frps 上，**域名先注册先得**。任何拿到 token 的人只要注册了你的域名，**你自己的 proxy 就注册不上**（frp 拒绝重复域名）—— 抢不走流量，但能让你上不了线。

所以 **`bindPort` 的 token 是整个入口的唯一门禁**：
- 强烈随机，定期轮换
- 安全组里把 `bindPort` 只对 frpc 来源 IP 放行（最有效的一刀）
- 确认隧道加密开启（frpc→frps 默认走 TLS）

### 6. vhost 端口与 TCP 代理会抢端口

`vhostHTTPPort = 80` 时，就不能再有 `type = "tcp"` + `remotePort = 80` 的 proxy —— 会冲突。二选一。

## 端口复用

frps 的 `vhostHTTPPort` / `vhostHTTPSPort` **可以和 `bindPort` 是同一个端口**，frps 会自己嗅探连接协议再分流。

注意：要把 `vhostHTTPSPort` 和 `bindPort` 配成同一个端口，需要先设 `transport.tls.disableCustomTLSFirstByte = false`。

## 多台机器共用一个公网入口

frps 有个**服务端 HTTP 插件**（`httpPlugins`）机制：frps 可以回调一个 HTTP 接口，在路由前做鉴权/改写/重定向等决策。适合需要统一入口策略的场景。

更常见的多租户做法就是：每台后端机器各跑一个 frpc，各自注册自己的 `customDomains`，frps 按 Host/SNI 分流。

## 什么时候不该用 frp

如果**后端服务和 frps 在同一台机器上**，且只有这一个站点要发布 —— frp 这一层就是多余的。

链路会变成：

```
外网 → frps:80 → frpc → 后端 → (后端再次按域名/路径路由)
```

同一个活干两遍。这时直接让 Nginx/Caddy 绑 80/443 更干净：少两个进程、少一跳、证书日志配置全在一处、上面前四个坑全部消失。

**保留 frp 的正当理由**：后续要让**别的机器**也把服务发布到这个 IP 的 80/443 上。
