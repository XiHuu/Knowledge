# MkDocs Material × GitHub Actions：构建、推分支、rsync 到服务器

一套完整的文档站点流水线：推送 `main` → 构建 → 推一个部署分支 → rsync 到自己的服务器。

## 目录与产物

```
.
├── mkdocs.yml                 # 站点配置
├── requirements.txt           # 锁版本的依赖
├── docs/                      # Markdown 源文件
└── .github/workflows/ci.yml
```

**关键：产物目录要显式指定**，默认是 `site/`，但很多部署 action 默认按 `public/` 写：

```yaml
# mkdocs.yml
site_dir: public
```

改了 `site_dir` 就必须同步改 CI 里的 `folder:` 和 `SOURCE:` —— **三处必须一致**。

## 完整 workflow

```yaml
name: ci

on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: write          # 推部署分支需要

# 同一分支有旧任务在跑时取消旧的，避免两个 rsync 并发写同一目录
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Cache pip
        uses: actions/cache@v4
        with:
          key: pip-${{ hashFiles('requirements.txt') }}
          path: ~/.cache/pip

      - name: Cache mkdocs-material
        run: echo "cache_id=$(date --utc '+%V')" >> $GITHUB_ENV

      - uses: actions/cache@v4
        with:
          key: mkdocs-material-${{ env.cache_id }}
          path: .cache

      - run: pip install -r requirements.txt

      - name: Build
        run: mkdocs build --strict

      - name: 部署到分支
        uses: JamesIves/github-pages-deploy-action@v4
        with:
          branch: deploy
          folder: public

      - name: 发布到服务器
        uses: easingthemes/ssh-deploy@main
        env:
          SSH_PRIVATE_KEY: ${{ secrets.PRIVATE_KEY }}
          ARGS: "-rltgoDzvO --delete"
          EXCLUDE: "/.git/, /.github/, /README.md"
          SOURCE: "public"
          REMOTE_HOST: ${{ secrets.REMOTE_HOST }}
          REMOTE_USER: ${{ secrets.REMOTE_USER }}
          REMOTE_PORT: ${{ secrets.REMOTE_PORT }}
          TARGET: ${{ secrets.SITE_ADDR }}
```

## 坑一：`ssh-deploy` 到底该用 `env:` 还是 `with:`？

**两个都行。** 该仓库的 README 自相矛盾（正文写 "Pass configuration with `env` vars"，两个示例却全用 `with:`）。

**以源码为准。** `dist/index.js` 里的读取逻辑：

```js
t.forEach(e => {
  const o = process.env[e] || process.env[`INPUT_${e}`] || i[s];
  //            ↑ env: 提供的裸名   ↑ with: 提供的 INPUT_ 前缀
});
```

**先读裸名，再回退 `INPUT_*`** —— 所以：

| 写法 | 实际环境变量 | 是否有效 |
| --- | --- | --- |
| `env:` | `REMOTE_HOST` | ✅ |
| `with:` | `INPUT_REMOTE_HOST` | ✅ |

同类坑：**遇到 action 行为与文档不符时，直接读 `action.yml` 和 `dist/`**，比读 README 可靠。

```bash
curl -s https://raw.githubusercontent.com/<owner>/<repo>/main/action.yml
```

## 坑二：`--delete` 是破坏性的

`ARGS: "-rltgoDzvO --delete"` 会让 rsync **删除 `TARGET` 下所有不在 `SOURCE` 里的文件**。

如果 `TARGET` 指向服务器根目录、或与其他站点共用目录，会直接删掉别的东西。

**对策**：`TARGET` 必须是该站点**独占**的目录。宁可先不加 `--delete` 跑一次确认落点。

## 坑三：`EXCLUDE` 常写成空转

`SOURCE` 是构建产物（`public/`），里面本来就不存在 `.git`、`README.md`、`LICENSE` 这些。针对它们的 `EXCLUDE` 规则毫无作用。

真正需要排除的是**产物里可能混进去的东西**，比如编辑器临时文件、`*.map`、草稿目录。

## 坑四：`--strict` 的取舍

`mkdocs build --strict` 把 warning 当错误。好处是坏链接、`nav:` 里引用了不存在的文件会立刻让流水线红掉；坏处是任何一个无害警告都会阻断部署。

**约定**：新页面放进 `docs/` 后**必须在 `mkdocs.yml` 的 `nav:` 里登记**，否则 `--strict` 不报错但页面不进侧边栏；反过来 `nav:` 里写了不存在的文件，`--strict` 直接失败。

## 坑五：action 版本钉不钉

`uses: someone/action@main` 跟着主分支走，作者一改你的流水线可能无声挂掉。生产建议钉到 tag：

```yaml
uses: easingthemes/ssh-deploy@v6.0.3
```

（`ssh-deploy` 当前版本 `runs.using: node24`，旧的 node12/node16 版本会被 GitHub 弃用告警。）

## 坑六：部署 SSH 密钥

`PRIVATE_KEY` 需要的是**私钥全文**，且：

- **不要设 passphrase**（rsync over ssh 无法交互输密码）
- 必须包含首尾的 `-----BEGIN/END ...-----` 标记行
- 对应**公钥**要写进目标服务器的 `~/.ssh/authorized_keys`
- 建议用**专用密钥**，不要复用登录密钥，便于单独吊销

```bash
ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/deploy_key -N ""
```

如果报 `Permission denied (publickey,password)`，该 action 文档给了两个 workaround：加 `SCRIPT_BEFORE: ls`（会触发 `ssh-keyscan` 刷新 `known_hosts`），或改用 `ssh-keygen -m PEM -t rsa -b 4096` 生成 PEM 格式密钥。

## GitHub Pages 与 Private 仓库的取舍

**GitHub Free（个人账户）不能从 Private 仓库发布 Pages** —— 需要 Pro / Team / Enterprise。

但如果你像本文这样已经用 rsync 把产物推到自己服务器了，**就不依赖 Pages**。把仓库改成 Private 的代价只是失去那个部署分支的在线预览。

另外注意：即使在付费计划下，**Pages 站点默认也是公开可访问的**；Private 仓库隐藏的是**源码**，不是站点内容。真正需要保密的细节（IP、端口、凭证）请一律走 GitHub Secrets，不要写进仓库文件。

## 推送后验证（别只看 push 的回显）

```bash
# 远端 HEAD 与本地是否一致
curl -s https://api.github.com/repos/<owner>/<repo>/branches/main \
  | python3 -c "import sys,json;d=json.load(sys.stdin);print(d['commit']['sha'][:10])"
git rev-parse --short HEAD
```

CI 运行状态：

```bash
curl -s "https://api.github.com/repos/<owner>/<repo>/actions/runs?per_page=3"
```

注意：**job 日志接口需要登录态**，未认证请求返回 403，但 `/jobs` 的**分步状态**（每步 success/failure）是可以匿名读的 —— 定位失败步骤足够用。
