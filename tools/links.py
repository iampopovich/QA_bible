#!/usr/bin/env python3
"""Проверка внешних ссылок QA_bible.

Использование:
    python3 tools/links.py                     # все внешние ссылки книги (долго: ~3000 URL)
    python3 tools/links.py --page PATH [...]   # только ссылки указанных страниц
    python3 tools/links.py --changed [BASE]    # только страницы, изменённые относительно BASE
    python3 tools/links.py --domain habr.com   # только ссылки на домен
    python3 tools/links.py --refresh           # игнорировать кэш
    python3 tools/links.py --json out.json

Результаты кэшируются в .cache/links.json (на 7 дней; каталог в .gitignore).
Классы результата:
    DEAD     404/410, домен не существует, — ссылку заменить (архив/первоисточник) или удалить
    MOVED    постоянный редирект на другой домен или на главную — проверить, обновить URL
    BLOCKED  401/403/429/999, защита от ботов — проверить вручную в браузере
    ERROR    таймаут, TLS, 5xx — перепроверить позже
    OK       2xx (или редирект в пределах того же смысла)
Домены из tools/links-skip.txt не проверяются (известная защита от ботов).
Код выхода 1, если есть DEAD.
"""
from __future__ import annotations

import json
import os
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, book_pages, changed_pages, ensure_py38, is_external, links_in, read  # noqa: E402

CACHE = os.path.join(ROOT, ".cache", "links.json")
SKIP_FILE = os.path.join(ROOT, "tools", "links-skip.txt")
TTL = 7 * 24 * 3600
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"


SAME_SITE = {"youtu.be": "youtube.com", "t.me": "telegram.me"}


def normalize(url: str) -> str:
    # GitBook экранирует спецсимволы в URL: \_ \~ \* \# и т.п.
    url = re.sub(r"\\([_~*#\[\]()!+.-])", r"\1", url).strip("<>")
    return "https:" + url if url.startswith("//") else url


def host_of(url: str) -> str:
    h = urllib.parse.urlparse(url).netloc.lower()
    h = h[4:] if h.startswith("www.") else h
    return SAME_SITE.get(h, h)


def classify(url: str):
    req_headers = {"User-Agent": UA, "Accept": "text/html,*/*;q=0.8", "Accept-Language": "ru,en;q=0.8"}
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers=req_headers)
        try:
            with urllib.request.urlopen(req, timeout=20, context=ssl.create_default_context()) as r:
                final = r.geturl()
                src, dst = urllib.parse.urlparse(url), urllib.parse.urlparse(final)
                if host_of(url) != host_of(final) or (
                    src.path.strip("/") and not dst.path.strip("/")
                ):
                    return "MOVED", r.status, final
                return "OK", r.status, final
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (400, 403, 404, 405, 406, 429, 500, 501, 503):
                continue  # многие сайты не поддерживают HEAD — повторяем GET
            if e.code in (404, 410):
                return "DEAD", e.code, ""
            if e.code in (401, 403, 429, 999):
                return "BLOCKED", e.code, ""
            return "ERROR", e.code, ""
        except urllib.error.URLError as e:
            reason = e.reason
            if isinstance(reason, socket.gaierror):
                return "DEAD", "DNS", ""
            if method == "HEAD":
                continue
            return "ERROR", type(reason).__name__, ""
        except Exception as e:  # noqa: BLE001 — таймауты, TLS, обрывы
            if method == "HEAD":
                continue
            return "ERROR", type(e).__name__, ""
    return "ERROR", "?", ""


def main():
    ensure_py38()
    argv = sys.argv[1:]
    if "--page" in argv:
        pages = [os.path.relpath(os.path.abspath(p), ROOT).replace(os.sep, "/")
                 for p in argv[argv.index("--page") + 1:] if not p.startswith("--")]
    elif "--changed" in argv:
        i = argv.index("--changed")
        base = argv[i + 1] if i + 1 < len(argv) and not argv[i + 1].startswith("--") else None
        pages = changed_pages(base)
    else:
        pages = book_pages()

    skip = set()
    if os.path.exists(SKIP_FILE):
        skip = {ln.strip().lower() for ln in open(SKIP_FILE, encoding="utf-8") if ln.strip() and not ln.startswith("#")}
    domain = argv[argv.index("--domain") + 1].lower() if "--domain" in argv else None

    where = defaultdict(set)
    for p in pages:
        for line, target in links_in(read(p)):
            if is_external(target):
                where[normalize(target)].add(f"{p}:{line}")
    urls = []
    for u in sorted(where):
        host = host_of(u)
        if domain and domain not in host:
            continue
        if any(host == s or host.endswith("." + s) for s in skip):
            continue
        urls.append(u)

    cache = {}
    if os.path.exists(CACHE) and "--refresh" not in argv:
        cache = json.load(open(CACHE, encoding="utf-8"))
    now = time.time()
    todo = [u for u in urls if u not in cache or now - cache[u]["t"] > TTL]
    print(f"Ссылок: {len(urls)} (пропущено по links-skip.txt: {len(where) - len(urls) if not domain else '-'}), "
          f"проверяется: {len(todo)}, из кэша: {len(urls) - len(todo)}", file=sys.stderr)

    with ThreadPoolExecutor(12) as ex:
        for n, (u, res) in enumerate(zip(todo, ex.map(classify, todo)), 1):
            cache[u] = {"t": now, "class": res[0], "code": res[1], "final": res[2]}
            if n % 100 == 0:
                print(f"  … {n}/{len(todo)}", file=sys.stderr)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    with open(CACHE, "w", encoding="utf-8") as fh:
        json.dump(cache, fh, ensure_ascii=False)

    stats = Counter()
    report = []
    for u in urls:
        c = cache[u]
        stats[c["class"]] += 1
        if c["class"] != "OK":
            report.append((c["class"], c["code"], u, c["final"], sorted(where[u])))
    order = {"DEAD": 0, "MOVED": 1, "BLOCKED": 2, "ERROR": 3}
    for cls, code, u, final, locs in sorted(report, key=lambda r: (order[r[0]], r[2])):
        print(f"{cls:7} {code}  {u}" + (f"  →  {final}" if final else ""))
        for loc in locs:
            print(f"          {loc}")
    print("\nИтого: " + ", ".join(f"{k}={stats[k]}" for k in ("OK", "DEAD", "MOVED", "BLOCKED", "ERROR")))

    if "--json" in argv:
        with open(argv[argv.index("--json") + 1], "w", encoding="utf-8") as fh:
            json.dump([dict(zip(("class", "code", "url", "final", "where"), r)) for r in report], fh,
                      ensure_ascii=False, indent=1)
    return 1 if stats["DEAD"] else 0


if __name__ == "__main__":
    sys.exit(main())
