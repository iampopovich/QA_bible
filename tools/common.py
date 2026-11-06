"""Общие функции для скриптов проверки QA_bible (только стандартная библиотека Python 3.8+)."""
from __future__ import annotations

import os
import re
import subprocess
import sys
import urllib.parse
from typing import Dict, Iterable, List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Служебные файлы, которые не являются страницами книги.
SERVICE_FILES = {
    "SUMMARY.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "AGENTS.md",
}
# Каталоги, которые не входят в книгу.
SERVICE_DIRS = {"docs", "tools", "node_modules"}

LINK_RE = re.compile(r"!?\[([^\]]*)\]\(<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\)")
HTML_REF_RE = re.compile(r"(?:src|href)=\"([^\"]+)\"")
FENCE_RE = re.compile(r"^```.*?^```[ \t]*$", re.S | re.M)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def rel(path: str) -> str:
    return os.path.relpath(os.path.abspath(path), ROOT).replace(os.sep, "/")


def book_pages() -> List[str]:
    """Все .md-страницы книги (относительные пути), без служебных файлов и каталогов."""
    out = []
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(
            x for x in dirs if not x.startswith(".") and not (d == ROOT and x in SERVICE_DIRS)
        )
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            r = rel(os.path.join(d, f))
            if r in SERVICE_FILES:
                continue
            out.append(r)
    return out


def read(path: str) -> str:
    with open(os.path.join(ROOT, path), encoding="utf-8") as fh:
        return fh.read()


def strip_code(text: str) -> str:
    """Заменяет блоки кода пустыми строками (номера строк сохраняются)."""
    return FENCE_RE.sub(lambda m: "\n" * m.group(0).count("\n"), text)


def unescape_target(target: str) -> str:
    """GitBook экранирует '_' как '\\_' и может кодировать URL."""
    return urllib.parse.unquote(target.replace("\\_", "_"))


def is_external(target: str) -> bool:
    return bool(re.match(r"^(https?:)?//", target))


def summary_entries() -> List[Tuple[int, str, str, int]]:
    """Строки SUMMARY.md: (номер строки, заголовок, путь, уровень вложенности)."""
    out = []
    for i, line in enumerate(read("SUMMARY.md").splitlines(), 1):
        m = re.match(r"^(\s*)\* \[(.*)\]\(([^)]+)\)", line)
        if m:
            out.append((i, m.group(2), unescape_target(m.group(3)).split("#")[0], len(m.group(1)) // 2))
    return out


def links_in(text: str) -> Iterable[Tuple[int, str]]:
    """(номер строки, цель) для всех markdown- и html-ссылок вне блоков кода."""
    for i, line in enumerate(strip_code(text).splitlines(), 1):
        line = INLINE_CODE_RE.sub("", line)
        for m in LINK_RE.finditer(line):
            yield i, m.group(2)
        for m in HTML_REF_RE.finditer(line):
            yield i, m.group(1)


def resolve(page: str, target: str) -> str:
    """Путь цели относительно корня репозитория."""
    t = unescape_target(target).split("#")[0]
    return os.path.normpath(os.path.join(os.path.dirname(page), t)).replace(os.sep, "/")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout


def changed_pages(base: Optional[str]) -> List[str]:
    """Страницы, изменённые относительно base (по умолчанию upstream/master или origin/master)."""
    if not base:
        for cand in ("upstream/master", "origin/master", "master"):
            if git("rev-parse", "--verify", "--quiet", cand).strip():
                base = cand
                break
    files = set()
    if base:
        files.update(git("diff", "--name-only", "--diff-filter=AMR", f"{base}...HEAD").split())
    files.update(git("diff", "--name-only", "--diff-filter=AMR", "HEAD").split())
    files.update(git("ls-files", "--others", "--exclude-standard").split())
    pages = set(book_pages())
    return sorted(f for f in files if f in pages)


def print_table(rows: List[Tuple], headers: Tuple) -> None:
    widths = [max(len(str(x)) for x in col) for col in zip(headers, *rows)] if rows else [len(h) for h in headers]
    print("  ".join(str(h).ljust(w) for h, w in zip(headers, widths)))
    for r in rows:
        print("  ".join(str(x).ljust(w) for x, w in zip(r, widths)))


def ensure_py38() -> None:
    if sys.version_info < (3, 8):
        sys.exit("Нужен Python 3.8+")


Report = Dict[str, List[Tuple[str, int, str]]]
