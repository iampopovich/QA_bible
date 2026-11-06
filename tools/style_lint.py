#!/usr/bin/env python3
"""Линтер оформления статей QA_bible по docs/contributing/style-guide.md.

Использование:
    python3 tools/style_lint.py                    # сводка по всей книге (правила и разделы)
    python3 tools/style_lint.py --page PATH [...]  # нарушения на странице(ах) с номерами строк
    python3 tools/style_lint.py --changed [BASE]   # страницы, изменённые относительно BASE (по умолчанию upstream/master)
    python3 tools/style_lint.py --rule S-03        # страницы, нарушающие правило
    python3 tools/style_lint.py --worst 20         # страницы с наибольшим числом нарушенных правил
    python3 tools/style_lint.py --regress [BASE]   # изменённые страницы не должны стать хуже tools/style-baseline.json
    python3 tools/style_lint.py --write-baseline   # перезаписать базовую линию (после принятых правок)

Код выхода: 1 — если в режимах --page/--changed найдены нарушения или в --regress найдено ухудшение.
ID правил (S-xx) совпадают с ID в style-guide.md. Блоки кода из проверки текста исключаются.
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, book_pages, changed_pages, ensure_py38, read, resolve, strip_code, unescape_target  # noqa: E402

BASELINE = os.path.join(ROOT, "tools", "style-baseline.json")
RULES = {}


def rule(rid, title, readme=True):
    def deco(fn):
        RULES[rid] = (title, fn, readme)
        return fn
    return deco


def lines(text, rx):
    return [i for i, line in enumerate(text.splitlines(), 1) if re.search(rx, line)]


def no_inline(text):
    return re.sub(r"`[^`\n]*`", "", text)


@rule("S-01", "H1 ровно один и стоит первой строкой")
def s01(raw, t, path):
    h1 = lines(t, r"^# ")
    first = t.lstrip("\n").splitlines()[0] if t.strip() else ""
    return [] if len(h1) == 1 and first.startswith("# ") else (h1 or [1])


@rule("S-02", "После H1 — вводный абзац, а не список/заголовок/картинка/цитата")
def s02(raw, t, path):
    m = re.search(r"^# .+\n+(.+)", t, re.M)
    if not m:
        return [1]
    return [t[: m.start(1)].count("\n") + 1] if re.match(r"^(#|\* |- |\d+\. |\||!\[|<|\{%|>)", m.group(1)) else []


@rule("S-03", "Псевдозаголовок **жирным** отдельной строкой вместо ##/###")
def s03(raw, t, path):
    return lines(t, r"^\*\*[^*\n]{2,80}\*\*\s*[:.;]?\s*$")


@rule("S-04", "Заголовок глубже ### (####+)")
def s04(raw, t, path):
    return lines(t, r"^#{4,} ")


@rule("S-05", "Маркер списка '-' (нужен '*')")
def s05(raw, t, path):
    return lines(t, r"^\s*- (?!-)")


@rule("S-06", "Пункт списка заканчивается ';'")
def s06(raw, t, path):
    return lines(t, r"^\s*(\*|-|\d+\.) .*;\s*$")


@rule("S-07", "Дефис вместо тире между словами (' - ' → ' — ')")
def s07(raw, t, path):
    tt = re.sub(r"\]\([^)]*\)", "]()", no_inline(t))
    rows = tt.splitlines()
    return [i for i in lines(tt, r"[^\s|*-] - [^\s|-]") if not rows[i - 1].lstrip().startswith("|")]


@rule("S-08", "Кавычки не «ёлочки» (“…” или \"…\" вокруг русского текста)")
def s08(raw, t, path):
    tt = re.sub(r"\]\([^)]*\)|<[^>]+>|\{%[^%]*%\}", "", no_inline(t))
    return lines(tt, r"[“”]|\"[А-Яа-яЁё][^\"\n]{0,60}\"")


@rule("S-09", "Секция источников не по шаблону ('## Источники' / '### Дополнительные материалы')")
def s09(raw, t, path):
    bad = lines(t, r"^(\*\*|_)?(Источник[и]?|Доп\.? ?материал[ы]?|Дополнительн(ый|ые) материал[ы]?|Дополнительно)"
                   r"\s*(\+[^:]*)?:?(\*\*|_)?:?\s*(&#x20;)?\s*$")
    return bad + lines(t, r"^(\*\*)?Источник[и]?:?(\*\*)? \[")


@rule("S-10", "Блок кода без языка (для схем и вывода — ```text)")
def s10(raw, t, path):
    out, inside = [], False
    for i, line in enumerate(raw.splitlines(), 1):
        if line.startswith("```"):
            if not inside and line.strip() == "```":
                out.append(i)
            inside = not inside
    return out


@rule("S-11", "Картинка с внешнего хоста (нужна копия в .gitbook/assets)")
def s11(raw, t, path):
    return lines(t, r"!\[[^\]]*\]\(https?://|<img [^>]*src=\"https?://")


@rule("S-12", "Картинка без alt-текста")
def s12(raw, t, path):
    return lines(t, r"!\[\]\(|<img (?![^>]*alt=\"[^\"]+\")[^>]*>")


@rule("S-13", "Разделитель --- / *** между секциями")
def s13(raw, t, path):
    return lines(t, r"^(---|\*\*\*)\s*$")


@rule("S-14", "Хвосты Википедии: сноски [1], «(англ. …)»")
def s14(raw, t, path):
    return lines(t, r"\\?\[\d{1,2}\\?\](?!\()|\(англ\.")


@rule("S-15", "Голый URL вне markdown-ссылки")
def s15(raw, t, path):
    tt = re.sub(r"\[[^\]]*\]\([^)]*\)|<[^>]+>", "", no_inline(t))
    return lines(tt, r"https?://\S+")


@rule("S-16", "Внутренняя ссылка без .md или на несуществующий файл")
def s16(raw, t, path):
    out = []
    for i, line in enumerate(no_inline(t).splitlines(), 1):
        for m in re.finditer(r"\]\((?!https?:|mailto:|tel:|#)([^)\s]+)\)", line):
            target = unescape_target(m.group(1)).split("#")[0]
            if ".gitbook/" in target:
                continue
            if not target.endswith(".md") or not os.path.exists(os.path.join(ROOT, resolve(path, target))):
                out.append(i)
    return out


@rule("S-17", "Определение курсивом _…_ (ISTQB) — нужна цитата >")
def s17(raw, t, path):
    return lines(t, r"^_[^_\n]{20,}_\s*$|^\s*\* _[^_\n]{10,}_;?\s*$")


@rule("S-18", "Нет секции '## Источники'", readme=False)
def s18(raw, t, path):
    if path.startswith(("poleznye-ssylki/", "prakticheskaya-chast/", "faq-dlya-novichkov/")) or path == "kontakty.md":
        return []
    return [] if re.search(r"^## Источник", t, re.M) else [0]


@rule("S-19", "Больше ~300 слов и ни одного ## заголовка", readme=False)
def s19(raw, t, path):
    return [0] if len(t.split()) > 300 and not re.search(r"^## ", t, re.M) else []


@rule("S-20", "Больше 3 hint-блоков на странице")
def s20(raw, t, path):
    hits = lines(t, r"\{% hint")
    return hits if len(hits) > 3 else []


@rule("S-21", "Hint со стилем success/danger (разрешены info и warning)")
def s21(raw, t, path):
    return lines(t, r"\{% hint style=\"(success|danger)\"")


def lint(path):
    raw = read(path)
    t = strip_code(raw)
    is_readme = path.endswith("README.md")
    res = {}
    for rid, (_title, fn, for_readme) in RULES.items():
        if is_readme and not for_readme:
            continue
        hits = fn(raw, t, path)
        if hits:
            res[rid] = hits
    return res


def print_page(path, res):
    if not res:
        print(f"OK    {path}")
        return
    print(f"FAIL  {path}")
    for rid, hits in sorted(res.items()):
        shown = ", ".join(str(h) for h in hits[:12] if h) + (" …" if len(hits) > 12 else "")
        print(f"      {rid} {RULES[rid][0]}" + (f" — строки: {shown} ({len(hits)})" if shown else ""))


def counts(res):
    return {rid: len(h) for rid, h in res.items()}


def main():
    ensure_py38()
    argv = sys.argv[1:]

    def arg_after(flag):
        i = argv.index(flag)
        return argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("--") else None

    if "--page" in argv:
        pages = [p for p in argv[argv.index("--page") + 1:] if not p.startswith("--")]
        bad = 0
        for p in pages:
            p = os.path.relpath(os.path.abspath(p), ROOT).replace(os.sep, "/")
            r = lint(p)
            print_page(p, r)
            bad += bool(r)
        return 1 if bad else 0

    if "--changed" in argv or "--regress" in argv:
        flag = "--changed" if "--changed" in argv else "--regress"
        pages = changed_pages(arg_after(flag))
        if not pages:
            print("Изменённых страниц нет.")
            return 0
        if flag == "--changed":
            bad = 0
            for p in pages:
                r = lint(p)
                print_page(p, r)
                bad += bool(r)
            return 1 if bad else 0
        base = json.load(open(BASELINE, encoding="utf-8")) if os.path.exists(BASELINE) else {}
        worse = 0
        for p in pages:
            now, was = counts(lint(p)), base.get(p, {})
            grown = {r: (was.get(r, 0), c) for r, c in now.items() if c > was.get(r, 0)}
            fixed = sum(max(0, c - now.get(r, 0)) for r, c in was.items())
            if grown:
                worse += 1
                print(f"WORSE {p}: " + ", ".join(f"{r} {a}→{b}" for r, (a, b) in sorted(grown.items())))
            else:
                print(f"OK    {p}" + (f" (исправлено нарушений: {fixed})" if fixed else ""))
        return 1 if worse else 0

    all_res = {p: lint(p) for p in book_pages()}

    if "--write-baseline" in argv:
        with open(BASELINE, "w", encoding="utf-8") as fh:
            json.dump({p: counts(r) for p, r in all_res.items() if r}, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")
        print(f"Базовая линия записана: {os.path.relpath(BASELINE, ROOT)}")
        return 0

    if "--rule" in argv:
        rid = arg_after("--rule")
        for p, r in all_res.items():
            if rid in r:
                print(f"{len(r[rid]):4d}  {p}")
        return 0

    if "--worst" in argv:
        k = int(arg_after("--worst") or 20)
        for p, r in sorted(all_res.items(), key=lambda x: -len(x[1]))[:k]:
            print(f"{len(r):2d}  {p}  [{' '.join(sorted(r))}]")
        return 0

    by_rule = Counter()
    sec = defaultdict(lambda: [0, 0])
    for p, r in all_res.items():
        s = p.split("/")[0] if "/" in p else "(корень)"
        sec[s][0] += 1
        sec[s][1] += len(r)
        by_rule.update(r.keys())
    clean = sum(1 for r in all_res.values() if not r)
    print(f"Страниц: {len(all_res)}, без нарушений: {clean}\n")
    print("Правило  Страниц  Описание")
    for rid, (title, _fn, _r) in RULES.items():
        print(f"{rid}     {by_rule[rid]:5d}  {title}")
    print("\nСреднее число нарушенных правил на страницу по разделам:")
    for s, (cnt, v) in sorted(sec.items(), key=lambda x: -x[1][1] / x[1][0]):
        print(f"  {v / cnt:4.1f}  {cnt:3d} стр.  {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
