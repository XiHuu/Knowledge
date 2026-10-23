#!/usr/bin/env python3
"""把「最近更新」列表写进首页。

数据源是 git 历史（docs/ 下的 Markdown 增改），因此不需要人工维护。
CI 在 mkdocs build 之前跑一次，保证线上首页永远是最新的。

用法：
    python scripts/gen_updates.py          # 就地更新 docs/index.md
    python scripts/gen_updates.py --check  # 只检查是否需要更新（非 0 退出即为过期）
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
INDEX = DOCS / "index.md"

START = "<!-- UPDATES:START -->"
END = "<!-- UPDATES:END -->"

MAX_ROWS = 40          # 列表最多保留多少行
MAX_PAGES_PER_ROW = 2  # 一次提交改了多页时，最多列出几个链接

PREFIX = re.compile(
    r"^(feat|fix|docs|chore|refactor|style|test|revert|perf|build|ci)"
    r"(\([^)]*\))?:\s*",
    re.IGNORECASE,
)


def git(*args: str) -> str:
    out = subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    )
    return out.stdout


def page_title(rel: str) -> str | None:
    """取页面的一级标题；文件不存在（已删除）则返回 None。"""
    path = DOCS / rel
    if not path.is_file():
        return None
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        return None
    return None


def tidy(subject: str) -> str:
    """去掉 conventional-commit 前缀，并把结尾句号清掉。"""
    text = PREFIX.sub("", subject).strip().rstrip("。.")
    return text or subject.strip()


def collect() -> list[tuple[str, str, list[tuple[str, str]]]]:
    """返回 [(日期, 变更说明, [(相对路径, 标题), ...]), ...]，新→旧。"""
    raw = git(
        "log",
        "--no-merges",
        "--date=short",
        "--pretty=format:\x01%h\x1f%ad\x1f%s",
        "--name-only",
        "--diff-filter=AM",
        "--",
        "docs/",
    )

    rows: list[tuple[str, str, list[tuple[str, str]]]] = []
    for chunk in raw.split("\x01"):
        if not chunk.strip():
            continue
        lines = [ln for ln in chunk.splitlines() if ln.strip()]
        if not lines:
            continue
        try:
            sha, date, subject = lines[0].split("\x1f", 2)
        except ValueError:
            continue

        pages: list[tuple[str, str]] = []
        for rel in lines[1:]:
            rel = rel.strip()
            if not rel.endswith(".md") or rel == "docs/index.md":
                continue
            title = page_title(rel[len("docs/"):])
            if title:
                pages.append((rel[len("docs/"):], title))
        if not pages:
            continue
        rows.append((date, tidy(subject), pages))

    return rows[:MAX_ROWS]


def render(rows: list[tuple[str, str, list[tuple[str, str]]]]) -> str:
    if not rows:
        return (
            f"{START}\n\n## 最近更新\n\n"
            "_还没有记录。推送到 `main` 后这里会自动出现。_\n\n"
            f"{END}"
        )

    out = [
        START,
        "",
        "## 最近更新",
        "",
        "_按提交时间从新到旧，自动生成。想看全部改动就翻 "
        "[commit 历史](https://github.com/XiHuu/Knowledge/commits/main)。_",
        "",
        "| 日期 | 页面 | 变更 |",
        "| --- | --- | --- |",
    ]
    for date, subject, pages in rows:
        links = " · ".join(f"[{title}]({rel})" for rel, title in pages[:MAX_PAGES_PER_ROW])
        if len(pages) > MAX_PAGES_PER_ROW:
            links += f" · 等 {len(pages)} 页"
        out.append(f"| {date} | {links} | {subject} |")
    out.append("")
    out.append(END)
    return "\n".join(out)


def main() -> int:
    check_only = "--check" in sys.argv[1:]
    text = INDEX.read_text(encoding="utf-8")

    if START not in text or END not in text:
        print(
            f"错误：{INDEX} 里找不到标记 {START} / {END}，无法注入。",
            file=sys.stderr,
        )
        return 2

    block = render(collect())
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    new_text = f"{head}{block}{tail}"

    if new_text == text:
        print("首页「最近更新」已是最新。")
        return 0

    if check_only:
        print("首页「最近更新」已过期，需要重新生成。", file=sys.stderr)
        return 1

    INDEX.write_text(new_text, encoding="utf-8")
    print(f"已更新 {INDEX.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
