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

# 4. 构建静态站点到 site/
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
├── mkdocs.yml              # 站点配置（主题、导航、扩展、插件）
├── requirements.txt        # Python 依赖
├── docs/                   # Markdown 源文件（写在这里）
│   ├── index.md
│   └── assets/
│       ├── logo.svg
│       ├── favicon.svg
│       └── extra.css
└── .github/workflows/      # GitHub Actions 自动部署
    └── ci.yml
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

推送到 `main` 分支后，GitHub Actions 会自动构建并发布到 GitHub Pages。

**首次使用需在仓库设置里手动开启：**
`Settings → Pages → Build and deployment → Source` 选择 **Deploy from a branch**，分支选 **`gh-pages`** / 目录 **`/ (root)`**。

站点地址：https://xihuu.github.io/Knowledge/

## 授权

个人知识库，未附授权协议。
