#!/usr/bin/env python3
"""Единая проверка перед коммитом/PR.

Использование:
    python3 tools/check.py              # integrity + стиль изменённых страниц (без ухудшений) + сводка актуальности
    python3 tools/check.py --links      # дополнительно внешние ссылки изменённых страниц (сеть)
    python3 tools/check.py --strict     # изменённые страницы должны быть полностью чистыми по стилю
    python3 tools/check.py --base REF   # с чем сравнивать (по умолчанию upstream/master → origin/master → master)

Код выхода 1, если: есть ошибки целостности (I-01…I-05), изменённая страница стала хуже
tools/style-baseline.json (или не чиста при --strict), либо при --links найдены мёртвые ссылки.
"""
from __future__ import annotations

import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from common import changed_pages  # noqa: E402


def run(title, *args):
    print(f"\n=== {title} ===", flush=True)
    return subprocess.run([sys.executable, os.path.join(HERE, args[0]), *args[1:]], check=False).returncode


def main():
    argv = sys.argv[1:]
    base = argv[argv.index("--base") + 1] if "--base" in argv else None
    base_args = [base] if base else []
    pages = changed_pages(base)
    print("Изменённые страницы: " + (", ".join(pages) if pages else "нет"))

    failed = []
    if run("Целостность (tools/integrity.py)", "integrity.py") != 0:
        failed.append("integrity")
    if pages:
        mode = "--changed" if "--strict" in argv else "--regress"
        if run(f"Стиль изменённых страниц (style_lint.py {mode})", "style_lint.py", mode, *base_args) != 0:
            failed.append("style")
        print("\n=== Актуальность изменённых страниц ===", flush=True)
        for p in pages:
            subprocess.run([sys.executable, os.path.join(HERE, "freshness.py"), "--page", p], check=False)
        if "--links" in argv:
            if run("Внешние ссылки изменённых страниц (links.py)", "links.py", "--changed", *base_args) != 0:
                failed.append("links")
    print("\n" + ("ПРОВАЛ: " + ", ".join(failed) if failed else "ОК"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
