#!/usr/bin/env python3
"""index.html（日本語）と各言語版を tools/template.html と tools/strings.py から作る。
使い方: python3 tools/build.py
"""
import html as htmllib, pathlib, re, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from strings import L, ORDER, NAMES

ROOT = pathlib.Path(__file__).resolve().parent.parent
TPL = (ROOT / "tools" / "template.html").read_text(encoding="utf-8")
DIRS = {"ja": "", "zh-tw": "zh-tw/", "ko": "ko/", "de": "de/"}

for lang in ORDER:
    d = dict(L[lang])
    up = "" if lang == "ja" else "../"
    d["up"] = up
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


# 検討事項ごとの詳細ページ（日本語のみ）。文言は tools/topics.py に置く。
from topics import TOPICS, ISSUES, LEAN, LEAN_NOTE

TOPIC_TPL = (ROOT / "tools" / "topic_template.html").read_text(encoding="utf-8")
# 詳細ページは概要ページの CSS をそのまま使う。<style> 内に新しい «キー» を足したら、下の置き換えにも足す
# （足し忘れると、未定義のキーとして生成が止まる）。
m = re.search(r"<style[^>]*>\s*(.*?)</style>", TPL, re.S)
if not m:
    sys.exit("tools/template.html に <style> が見つかりません")
CSS = m.group(1)
JA = L["ja"]
CSS = CSS.replace("«font»", JA["font"]).replace("«lh»", JA["lh"]).replace("«ls»", JA["ls"])
TITLES = {t["slug"]: t["title"] for t in TOPICS}

# 概要ページの「検討事項」のリンク先と、詳細ページの slug が一致しないと「詳しく読む」が404になる。
linked = re.findall(r"«up»topics/([a-z0-9-]+)\.html", TPL)
if sorted(linked) != sorted(TITLES) or len(set(linked)) != len(linked):
    sys.exit("template.html のリンク先と topics.py の slug が一致しません: %s" % sorted(set(linked) ^ set(TITLES)))


def items(xs):
    return "\n".join("    <li>%s</li>" % x for x in xs)


def paras(xs):
    return "".join("  <p>%s</p>\n" % x for x in xs)


for t in TOPICS:
    issue_url = "%s/%d" % (ISSUES, t["issue"])
    note = t.get("lean_note", LEAN_NOTE)
    d = {
        "css": CSS,
        "site_title": JA["title"],
        "title": t["title"],
        "desc": htmllib.escape(re.sub(r"<[^>]+>", "", t["lead"]), quote=True),
        "back": "← 概要ページに戻る",
        "bar_issue": JA["bar_issue"],
        "issue_url": issue_url,
        "h_open": JA["h_open"],
        "lead": t["lead"],
        "more_p": paras(t.get("more_p", [])),
        "decided_h": t.get("decided_h", "いまの構想で決まっていること"),
        "decided": items(t["decided"]),
        "undecided_h": "決まっていないこと",
        "undecided": items(t["undecided"]),
        "options_h": "案の比較",
        "options": "\n".join(
            '    <li><h3>%s</h3><dl><dt class="good">よい点</dt><dd>%s</dd><dt class="bad">困る点</dt><dd>%s</dd></dl></li>' % o
            for o in t["options"]),
        "lean_h": t.get("lean_h", LEAN),
        "lean_note": '  <p class="note">%s</p>\n' % note if note else "",
        "lean_p": t["lean_p"],
        "lean_items": items(t["lean_items"]),
        "lean_after": paras([t["lean_after"]] if t.get("lean_after") else []),
        "rest_h": "残る課題",
        "rest": t["rest"],
        "related_h": "関連する検討事項",
        "related": items('<a href="%s.html">%s</a>' % (s, TITLES[s]) for s in t["related"]),
        "ask": 'この検討事項への意見は、<a href="%s">GitHubのIssue %d番</a>に書いてください。' % (issue_url, t["issue"]),
        "foot1": JA["foot1"],
        "foot2": JA["foot2"],
    }
    html = TOPIC_TPL
    for k, v in d.items():
        html = html.replace("«" + k + "»", v)
    left = sorted(set(re.findall(r"«([a-z0-9_]+)»", html)))
    if left:
        sys.exit("%s: 未定義のキー %s" % (t["slug"], left))
    out = ROOT / "topics" / (t["slug"] + ".html")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print("wrote", out.relative_to(ROOT))
