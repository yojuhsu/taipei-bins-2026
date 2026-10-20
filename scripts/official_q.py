"""官方題目原文（puma.taipei/hackathon，2026-10-21 06:5x 抓取，原始 HTML 在 ~/Projects/civic-debug-data/puma_hackathon_20261021.html）。
給各頁產生器用：題目怎麼說一律放這裡的原文，一個字不動（Erica 2026-10-21 07:0x）。"""
import json, os, html

_P = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "_草稿", "官方題目_20261021.json")
_RAW = json.load(open(_P, encoding="utf-8"))
FETCHED = "2026-10-21"


def get(n):
    """n 是 '#1' 到 '#7'。回 dict(num, title, labels, desc, shen, data)。"""
    for k, body in _RAW.items():
        lines = [l.strip() for l in k.split("\n")] + [l.strip() for l in body.split("\n")]
        lines = [l for l in lines if l]
        if lines[0] != n: continue
        title = lines[1]
        # 標籤：標題之後、描述之前的短字
        labels, desc, shen, data = [], "", "", []
        i = 2
        while i < len(lines) and len(lines[i]) <= 40 and not lines[i].startswith("沈伯洋說"):
            labels.append(lines[i]); i += 1
        if i < len(lines): desc = lines[i]; i += 1
        while i < len(lines):
            if lines[i].startswith("沈伯洋說"):
                shen = lines[i + 1] if i + 1 < len(lines) else ""; i += 2; continue
            if lines[i] == "開放資料":
                j = i + 2
                while j < len(lines) and not lines[j].startswith("→") and lines[j] not in ("Rules",):
                    data.append(lines[j]); j += 1
                break
            i += 1
        return dict(num=n, title=title, labels=labels, desc=desc, shen=shen, data=data)
    raise KeyError(n)


def block_html(n, cls="official"):
    """題目怎麼說的 HTML：標題、標籤、原文、沈伯洋說（有的話），全部原文。"""
    q = get(n); E = html.escape
    s = f'<div class="{cls}"><p><b>題目怎麼說</b>（官方活動頁原文，{FETCHED} 抓取，一字不改）</p>'
    s += f'<p class="qt">{E(q["num"])} {E(q["title"])}<span class="lbls">{"".join(f"<span>{E(l)}</span>" for l in q["labels"])}</span></p>'
    s += f'<p>{E(q["desc"])}</p>'
    if q["shen"]:
        s += f'<p><b>沈伯洋說：</b>{E(q["shen"])}</p>'
    return s + "</div>"


def block_md(n):
    q = get(n)
    s = f'**題目怎麼說**（官方活動頁原文，{FETCHED} 抓取，一字不改）：{q["num"]} {q["title"]}（{"、".join(q["labels"])}）\n\n> {q["desc"]}\n'
    if q["shen"]:
        s += f'>\n> 沈伯洋說：{q["shen"]}\n'
    return s


if __name__ == "__main__":
    for n in ("#1", "#2", "#3", "#4", "#5", "#6", "#7"):
        q = get(n); print(n, q["title"], q["labels"], "| desc", len(q["desc"]), "| shen", bool(q["shen"]), "| data", len(q["data"]))
