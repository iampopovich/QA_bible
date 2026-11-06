#!/usr/bin/env python3
"""Проверка целостности книги QA_bible.

Использование:
    python3 tools/integrity.py            # отчёт; код выхода 1, если есть ошибки (ERROR)
    python3 tools/integrity.py --strict   # предупреждения (WARN) тоже дают код выхода 1
    python3 tools/integrity.py --json out.json
    python3 tools/integrity.py --write-known   # зафиксировать текущие ошибки как известные (tools/integrity-known.json)
    python3 tools/integrity.py --no-known      # показать известные ошибки как обычные

Известные ошибки (KNOWN) — долг, существовавший до появления проверок; на код выхода не влияют.
Новые ошибки (ERROR) — дают код выхода 1.
Проверки (ID используются в docs/contributing/*.md):
    I-01 ERROR  запись в SUMMARY.md ведёт на несуществующий файл
    I-02 ERROR  страница не внесена в SUMMARY.md (GitBook её не публикует)
    I-03 ERROR  страница внесена в SUMMARY.md больше одного раза
    I-04 ERROR  битая внутренняя ссылка (файл не существует, часто — забыт .md)
    I-05 ERROR  ссылка на несуществующую картинку/файл в .gitbook/assets
    I-06 WARN   картинка в .gitbook/assets ни на одной странице не используется
    I-07 WARN   страница без H1 или почти пустая (кроме README разделов)
    I-08 WARN   у каталога раздела нет README.md
    I-09 WARN   одинаковые H1 у разных страниц
    I-10 WARN   ссылка на якорь #..., которого нет среди заголовков целевой страницы
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import (  # noqa: E402
    ROOT,
    book_pages,
    ensure_py38,
    is_external,
    links_in,
    read,
    resolve,
    strip_code,
    summary_entries,
    unescape_target,
)

MIN_WORDS = 40
ERRORS = {"I-01", "I-02", "I-03", "I-04", "I-05"}
KNOWN = os.path.join(ROOT, "tools", "integrity-known.json")


TRANSLIT = dict(zip(
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    ["a", "b", "v", "g", "d", "e", "e", "zh", "z", "i", "i", "k", "l", "m", "n", "o", "p", "r", "s", "t",
     "u", "f", "kh", "c", "ch", "sh", "sh", "", "y", "", "e", "yu", "ya"],
))


def slugify(heading: str) -> str:
    """Приближение к якорям GitBook: транслит кириллицы, нижний регистр, без пунктуации, пробелы -> '-'."""
    h = re.sub(r"<[^>]+>|[*_`\\]", "", heading.strip().lower())
    h = "".join(TRANSLIT.get(ch, ch) for ch in h)
    h = re.sub(r"[^\w\s-]", "", h, flags=re.U)
    return re.sub(r"[\s-]+", "-", h).strip("-")


def anchors(text: str):
    body = strip_code(text)
    out = {slugify(m.group(1)) for m in re.finditer(r"^#{1,6} (.+?)\s*#*\s*$", body, re.M)}
    out |= {m.group(1) for m in re.finditer(r"\bid=\"([^\"]+)\"", body)}
    return out


def main() -> int:
    ensure_py38()
    strict = "--strict" in sys.argv
    issues = []  # (id, path, line, message)

    pages = book_pages()
    page_set = set(pages)
    texts = {p: read(p) for p in pages}

    # SUMMARY
    seen = defaultdict(list)
    for line, title, path, _lvl in summary_entries():
        seen[path].append(line)
        if not os.path.exists(os.path.join(ROOT, path)):
            issues.append(("I-01", "SUMMARY.md", line, f"нет файла {path} («{title}»)"))
    for path, lines in seen.items():
        if len(lines) > 1:
            issues.append(("I-03", "SUMMARY.md", lines[1], f"{path} встречается {len(lines)} раза (строки {lines})"))
    for p in pages:
        if p not in seen:
            issues.append(("I-02", p, 0, "страница не внесена в SUMMARY.md и не публикуется"))

    # Ссылки
    used_assets = set()
    anchors_cache = {}
    for p, text in texts.items():
        for line, target in links_in(text):
            if is_external(target) or target.startswith(("mailto:", "tel:")):
                continue
            raw = unescape_target(target)
            if raw.startswith("#"):
                path, anchor = p, raw[1:]
            else:
                path = resolve(p, target)
                anchor = raw.split("#", 1)[1] if "#" in raw else ""
            if ".gitbook/assets/" in path:
                used_assets.add(os.path.basename(path))
                if not os.path.exists(os.path.join(ROOT, path)):
                    issues.append(("I-05", p, line, f"нет файла {target}"))
                continue
            if not raw.startswith("#") and not os.path.exists(os.path.join(ROOT, path)):
                hint = " (нет расширения .md?)" if os.path.exists(os.path.join(ROOT, path + ".md")) or not path.endswith(".md") else ""
                issues.append(("I-04", p, line, f"битая ссылка {target}{hint}"))
                continue
            if anchor and path in page_set:
                if path not in anchors_cache:
                    anchors_cache[path] = anchors(texts[path])
                if anchor not in anchors_cache[path] and slugify(anchor) not in anchors_cache[path]:
                    issues.append(("I-10", p, line, f"нет якоря #{anchor} в {path}"))

    assets_dir = os.path.join(ROOT, ".gitbook", "assets")
    if os.path.isdir(assets_dir):
        for a in sorted(os.listdir(assets_dir)):
            if a not in used_assets:
                issues.append(("I-06", ".gitbook/assets/" + a, 0, "файл нигде не используется"))

    # Страницы
    h1_index = defaultdict(list)
    for p, text in texts.items():
        body = strip_code(text)
        m = re.search(r"^# (.+)$", body, re.M)
        if m:
            h1_index[m.group(1).strip()].append(p)
        words = len(re.sub(r"[#*_>`\[\]()!|-]", " ", body).split())
        if not m:
            issues.append(("I-07", p, 1, "нет заголовка H1"))
        elif words < MIN_WORDS and not p.endswith("README.md"):
            issues.append(("I-07", p, 1, f"почти пустая страница ({words} слов)"))
    for title, ps in h1_index.items():
        if len(ps) > 1:
            issues.append(("I-09", ps[1], 1, f"H1 «{title}» совпадает с {', '.join(ps[:1] + ps[2:])}"))

    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if not x.startswith(".") and not (d == ROOT and x in ("docs", "tools"))]
        if d != ROOT and any(f.endswith(".md") for f in files) and "README.md" not in files:
            issues.append(("I-08", os.path.relpath(d, ROOT), 0, "нет README.md раздела"))

    issues.sort(key=lambda x: (x[0], x[1], x[2]))
    known = set()
    if os.path.exists(KNOWN) and "--no-known" not in sys.argv:
        known = {(k["id"], k["path"], k["message"]) for k in json.load(open(KNOWN, encoding="utf-8"))}
    if "--write-known" in sys.argv:
        with open(KNOWN, "w", encoding="utf-8") as fh:
            json.dump([{"id": i[0], "path": i[1], "message": i[3]} for i in issues if i[0] in ERRORS],
                      fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        print(f"Известные ошибки записаны: {os.path.relpath(KNOWN, ROOT)}")
        return 0
    errors = [i for i in issues if i[0] in ERRORS and (i[0], i[1], i[3]) not in known]
    old = [i for i in issues if i[0] in ERRORS and (i[0], i[1], i[3]) in known]
    warns = [i for i in issues if i[0] not in ERRORS]
    for rid, path, line, msg in issues:
        level = "WARN " if rid not in ERRORS else ("KNOWN" if (rid, path, msg) in known else "ERROR")
        loc = f"{path}:{line}" if line else path
        print(f"{level} {rid} {loc} — {msg}")
    print(f"\nСтраниц: {len(pages)}, записей SUMMARY: {sum(len(v) for v in seen.values())}, "
          f"новых ошибок: {len(errors)}, известных ошибок (tools/integrity-known.json): {len(old)}, "
          f"предупреждений: {len(warns)}")
    gone = len(known) - len(old)
    if gone > 0:
        print(f"Исправлено известных ошибок: {gone} — обновите список: python3 tools/integrity.py --write-known")

    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        with open(out, "w", encoding="utf-8") as fh:
            json.dump([dict(zip(("id", "path", "line", "message"), i)) for i in issues], fh, ensure_ascii=False, indent=1)
    return 1 if errors or (strict and warns) else 0


if __name__ == "__main__":
    sys.exit(main())
