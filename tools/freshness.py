#!/usr/bin/env python3
"""Контроль актуальности статей QA_bible.

Использование:
    python3 tools/freshness.py                 # просроченные страницы (по классам устаревания)
    python3 tools/freshness.py --all           # все страницы с датой проверки и сроком
    python3 tools/freshness.py --markers       # «временные» формулировки и версии в тексте (кандидаты на устаревание)
    python3 tools/freshness.py --page PATH     # статус и маркеры одной страницы
    python3 tools/freshness.py --today 2027-01-01

Данные:
    docs/contributing/freshness-rules.tsv  шаблон пути → класс → срок в месяцах (первое совпадение сверху)
    docs/contributing/reviewed.tsv         журнал проверок: путь, дата (YYYY-MM-DD), кто, заметка
Если страницы нет в журнале, датой считается последний коммит, менявший файл (помечается «git»).
Правила — docs/contributing/freshness.md.
"""
from __future__ import annotations

import datetime as dt
import fnmatch
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, book_pages, ensure_py38, git, read, strip_code  # noqa: E402

RULES = os.path.join(ROOT, "docs", "contributing", "freshness-rules.tsv")
REVIEWED = os.path.join(ROOT, "docs", "contributing", "reviewed.tsv")

MARKERS = [
    ("год", r"\b(в|к|с|до|на)\s+20[12]\d\s*(году|г\.|год)"),
    ("версия", r"(?i)\bv\d+(\.\d+)+\b|\b(верси[яиюей]|version|android|ios|node\.js|python|java|kotlin|xcode|"
               r"playwright|selenium|appium|cypress|chrome|firefox|gradle|api level)\s+\d+(\.\d+)*\b"),
    ("«сейчас»", r"(?i)\b(сейчас|на сегодня(шний день)?|в настоящее время|на данный момент|в этом году|последн(яя|ей|юю) верси)"),
    ("дата-метка", r"\(на \d{2}\.\d{4}\)"),
    ("модель AI", r"(?i)\b(gpt-?\d[\w.-]*|claude \w+ ?\d[\d.]*|gemini \d[\d.]*|sonnet ?\d[\d.]*|opus ?\d[\d.]*|qwen\d[\d.]*|llama ?\d[\d.]*)"),
    ("цена", r"(?i)\$\s?\d+|\d+\s?(\$|usd|руб\.?|₽)\b"),
]


def load_tsv(path):
    rows = []
    if os.path.exists(path):
        for line in open(path, encoding="utf-8"):
            if line.strip() and not line.startswith("#"):
                rows.append([c.strip() for c in line.rstrip("\n").split("\t")])
    return rows


def classify(page, rules):
    for row in rules:
        if fnmatch.fnmatch(page, row[0]):
            return row[1], int(row[2])
    return "C", 36


def reviewed_dates():
    out = {}
    for row in load_tsv(REVIEWED):
        if len(row) >= 2:
            d = dt.date.fromisoformat(row[1])
            if row[0] not in out or out[row[0]] < d:
                out[row[0]] = d
    return out


FORMAT_ONLY = re.compile(r"^(Оформление|style)\b", re.I)


def git_date(page):
    """Дата последнего коммита по содержанию: коммиты «Оформление: …» (только форматирование) пропускаются."""
    for line in git("log", "--format=%cs %s", "--", page).splitlines():
        date, _, subject = line.partition(" ")
        if not FORMAT_ONLY.match(subject):
            return dt.date.fromisoformat(date)
    return None


def add_months(d, m):
    y, mo = divmod(d.month - 1 + m, 12)
    return dt.date(d.year + y, mo + 1, min(d.day, 28))


def markers(page):
    out = []
    text = strip_code(read(page))
    for i, line in enumerate(text.splitlines(), 1):
        plain = re.sub(r"\]\([^)]*\)|<[^>]+>", "]", line)
        for name, rx in MARKERS:
            for m in re.finditer(rx, plain):
                out.append((i, name, m.group(0)))
    return out


def main():
    ensure_py38()
    argv = sys.argv[1:]
    today = dt.date.fromisoformat(argv[argv.index("--today") + 1]) if "--today" in argv else dt.date.today()
    rules = load_tsv(RULES)
    rev = reviewed_dates()

    if "--page" in argv:
        pages = [os.path.relpath(os.path.abspath(argv[argv.index("--page") + 1]), ROOT).replace(os.sep, "/")]
    else:
        pages = book_pages()

    rows = []
    for p in pages:
        cls, months = classify(p, rules)
        src = "журнал" if p in rev else "git"
        last = rev.get(p) or git_date(p)
        due = add_months(last, months) if last else today
        rows.append((p, cls, months, last, src, due, (today - due).days))

    if "--markers" in argv:
        total = 0
        for p, cls, *_ in sorted(rows, key=lambda r: r[1]):
            ms = markers(p)
            if ms:
                total += len(ms)
                print(f"[{cls}] {p}")
                for i, name, frag in ms[:20]:
                    print(f"      {i:4d}  {name:10}  {frag}")
                if len(ms) > 20:
                    print(f"      … ещё {len(ms) - 20}")
        print(f"\nМаркеров: {total}")
        return 0

    show = rows if ("--all" in argv or "--page" in argv) else [r for r in rows if r[6] > 0]
    show.sort(key=lambda r: (-r[6], r[0]))
    print(f"{'просрочка':>9}  кл  срок  проверено   источник  путь")
    for p, cls, months, last, src, due, over in show:
        print(f"{over:>8}д  {cls:2}  {months:3}м  {last}  {src:8}  {p}")
    if "--page" in argv:
        for i, name, frag in markers(pages[0]):
            print(f"      {i:4d}  {name:10}  {frag}")
    overdue = [r for r in rows if r[6] > 0]
    by_cls = {}
    for r in overdue:
        by_cls[r[1]] = by_cls.get(r[1], 0) + 1
    print(f"\nСтраниц: {len(rows)}, просрочено: {len(overdue)} " + str(dict(sorted(by_cls.items()))) + f", на дату {today}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
