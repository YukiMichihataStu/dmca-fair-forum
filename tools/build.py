#!/usr/bin/env python3
"""index.html（日本語）と各言語版を tools/template.html と tools/strings.py から作る。
使い方: python3 tools/build.py
"""
import pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from strings import L, ORDER, NAMES

ROOT = pathlib.Path(__file__).resolve().parent.parent
TPL = (ROOT / "tools" / "template.html").read_text(encoding="utf-8")
DIRS = {"ja": "", "zh-tw": "zh-tw/", "ko": "ko/", "de": "de/"}

for lang in ORDER:
    d = dict(L[lang])
    up = "" if lang == "ja" else "../"
    d["lang"] = {"ja": "ja", "zh-tw": "zh-Hant-TW", "ko": "ko", "de": "de"}[lang]
    d["xlang"] = {"ja": "ja", "zh-tw": "zh-tw", "ko": "ko", "de": "de"}[lang]
    d["options"] = "".join(
        '<option value="%s%s"%s>%s</option>' % (up, DIRS[o] or "./", " selected" if o == lang else "", NAMES[o])
        for o in ORDER)
    d["alternates"] = "".join(
        '<link rel="alternate" hreflang="%s" href="https://yukimichihatastu.github.io/dmca-fair-forum/%s">\n' % (
            {"ja": "ja", "zh-tw": "zh-Hant-TW", "ko": "ko", "de": "de"}[o], DIRS[o]) for o in ORDER)
    html = TPL
    for k, v in d.items():
        html = html.replace("«" + k + "»", v)
    left = sorted(set(re.findall(r"«([a-z0-9_]+)»", html)))
    if left:
        sys.exit("%s: 未定義のキー %s" % (lang, left))
    out = ROOT / DIRS[lang] / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("wrote", out.relative_to(ROOT))
