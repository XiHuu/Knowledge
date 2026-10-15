# Knowledge

个人知识库，基于 [MkDocs](https://www.mkdocs.org/) + [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) 构建。

## 快速开始

```bash
# 1. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. 安装依赖（国内建议先换源，见下）
pip install -r requirements.txt

# 3. 本地预览（默认 http://127.0.0.1:8000，改文件自动热重载）
mkdocs serve

# 4. 构建静态站点到 public/（目录名由 mkdocs.yml 的 site_dir 决定）
mkdocs build
```

### 国内加速

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

或写入 `~/.config/pip/pip.conf`：

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
```

## 目录结构

```
Knowledge/
├── mkdocs.yml              # 站点配置（主题、导航、扩展、插件、site_dir）
├── requirements.txt        # Python 依赖
├── docs/                   # Markdown 源文件（写在这里）
│   ├── index.md
│   └── assets/
│       ├── logo.svg
│       ├── favicon.svg
│       └── extra.css
├── public/                 # 构建产物（自动生成，已 gitignore）
└── .github/workflows/
    └── ci.yml              # 构建 + 部署流水线
```

## 写作约定

- 新增页面放在 `docs/` 下，然后在 `mkdocs.yml` 的 `nav:` 里登记，否则不会出现在侧边栏
- 图片等静态资源放在 `docs/assets/`
- 支持 Mermaid 图表、代码高亮、提示框（admonition）、标签页、任务列表等

### 常用语法

````markdown
!!! note "标题"
    这是提示框。可用类型：note / tip / warning / danger / info / example

```mermaid
graph LR
  A[想法] --> B[笔记] --> C[知识库]
```
````

## 部署

推送到 `main` 后，`.github/workflows/ci.yml` 自动执行三步：

1. **构建** —— `mkdocs build --strict`，产物在 `public/`
2. **部署到 Deploy 分支** —— `JamesIves/github-pages-deploy-action@v4` 把 `public/` 推到 `deploy` 分支
3. **发布到服务器** —— `easingthemes/ssh-deploy@main` 用 rsync 把 `public/` 同步到目标服务器

> `--strict` 会把警告当错误，任何一条 `WARNING` 都会中断流水线、不部署。
> 想放宽就把 `Build site` 那步改成 `mkdocs build`。

### 必需的仓库 Secrets

`Settings → Secrets and variables → Actions → New repository secret`

| Secret | 用途 | 示例值 |
| --- | --- | --- |
| `PRIVATE_KEY` | 部署用 SSH **私钥**全文，含首尾 `-----BEGIN/END-----` 标记行，**不要设 passphrase** | `-----BEGIN OPENSSH PRIVATE KEY-----` … |
| `REMOTE_HOST` | 目标服务器地址 | `1.2.3.4` 或 `example.com` |
| `REMOTE_USER` | 登录用户名 | `ubuntu` |
| `REMOTE_PORT` | SSH 端口 | `22` |
| `SITE_ADDR` | **目标服务器上的绝对路径**（rsync 落点） | `/var/www/knowledge` |

对应公钥需提前写入目标服务器 `~/.ssh/authorized_keys`。

> ⚠️ **`ARGS` 里带了 `--delete`**：`SITE_ADDR` 目录中凡是不存在于 `public/` 的文件都会被**删除**。
> 请确认 `SITE_ADDR` 是一个**该站点独占的目录**，绝不要指向服务器根目录或与其他站点共用的目录。

### GitHub Pages

`Settings → Pages → Build and deployment → Source` 选 **Deploy from a branch**，
分支选 **`deploy`**、目录 **`/ (root)`**。

站点地址：https://xihuu.github.io/Knowledge/

## 授权

个人知识库，未附授权协议。
