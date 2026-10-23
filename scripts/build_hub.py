"""まとめページ（hub/index.html）を作る。道具へのリンク・ChatGPTのプロンプト（コピーボタン付き）・
添付する画像・必要な素材・資料へのリンクを1ページにまとめる。

使い方：
    python3 scripts/build_hub.py
プロンプト集（assets/keyvisual/PROMPTS_ChatGPT.md）や素材一覧（docs/assets-todo.md）を直したら、これを実行し直す。
公開URL：https://kenbeee-create.github.io/cinemaholic-animator/hub/
"""
from __future__ import annotations

import datetime
import html
import os
import re

import markdown

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "hub", "index.html")
SITE = "https://kenbeee-create.github.io/cinemaholic-animator/"
REPO = "https://github.com/kenbeee-create/cinemaholic-animator/blob/main/"

TOOLS = [
    ("スタジオ", "tools/studio/", "部屋のセットに2人を置いて、カットごとにカメラ・セリフ・表情・動きを決めて会話シーンを作る"),
    ("トーク画面メーカー", "tools/chat-maker/", "冒頭のトーク画面（S1）。メッセージを打つと動く画面になる"),
    ("映画紹介メーカー", "tools/movie-card-maker/", "処方箋ふうの映画紹介（ポスター・効きめ・もらえる薬局）"),
    ("文字の画面メーカー", "tools/card-maker/", "バックボーン（S5）・名言（S7）・処方箋（S8）"),
    ("（旧）アニメーター", "", "最初に作ったキャラを動かす道具"),
]

# 添付に使う画像（プロンプトの中のファイル名 → リポジトリの場所）
IMAGES = [
    ("gonbe_base.png", "assets/characters/gonbe/gonbe_base.png", "ごんべぇ（最初の基本の絵）"),
    ("johndoe_base.png", "assets/characters/johndoe/johndoe_base.png", "じょんどぅー（最初の基本の絵）"),
    ("johndoe_room_v1.png", "assets/backgrounds/johndoe_room_v1.png", "部屋（最初の絵）"),
    ("keyvisual.png", "assets/keyvisual/keyvisual.png", "完成図（Tシャツ無地版）"),
    ("gonbe/sit_source.png", "assets/characters/gonbe/sit_source.png", "ごんべぇ（座り・透明背景）"),
    ("johndoe/sit_source.png", "assets/characters/johndoe/sit_source.png", "じょんどぅー（座り・無地Tシャツ・透明背景）"),
    ("doctor_stand.png", "assets/characters/johndoe/doctor_stand.png", "白衣のじょんどぅー（立ち絵）"),
    ("room_base_source.png", "assets/backgrounds/room_base_source.png", "2人がいない部屋"),
]

DOCS = [
    ("キャラクター設定書", "docs/characters.md"), ("冒頭（トーク画面・タイトル）", "docs/opening.md"),
    ("回ごとの見た目（部屋と服）", "docs/episode-look.md"), ("映画紹介の画面", "docs/movie-card.md"),
    ("スタジオの使い方", "docs/studio.md"), ("絵柄のルール（AIっぽさを消す）", "docs/style-bible.md"), ("動画の作り方", "docs/production-flow.md"),
    ("品質基準", "docs/quality-bar.md"), ("トーン（色・文字）", "docs/tone.md"),
    ("入りのひと言の台帳", "docs/opening-lines.md"), ("絵コンテ（型）", "docs/storyboard/README.md"),
    ("進捗", "docs/studio-status.md"), ("CLAUDE.md（全体のルール）", "CLAUDE.md"),
]

PREVIEWS = [
    ("下書き動画（段階2・540×960・秒数の透かし入り）", "hub/media/ep00-sample-draft.mp4", "video"),
    ("通しの試作（約50秒・声なし）", "hub/media/ep00-sample.mp4", "video"),
    ("最新の絵コンテ（試作の実際のコマ）", "docs/storyboard/latest_storyboard.jpg", "img"),
    ("最初の絵コンテ（型）", "docs/storyboard/format_storyboard.jpg", "img"),
    ("映画紹介の画面", "docs/storyboard/movie_intro_mock.jpg", "img"),
    ("ごんべぇの表情", "assets/characters/gonbe/_preview/expressions.png", "img"),
]


def rel(p):
    return "../" + p


def md(text):
    return markdown.markdown(text, extensions=["tables", "fenced_code"])


def prompts_html():
    src = open(os.path.join(ROOT, "assets/keyvisual/PROMPTS_ChatGPT.md"), encoding="utf-8").read()
    body = md(src)
    # 先頭の見出し（h1）は外す
    body = re.sub(r"^<h1>.*?</h1>", "", body, count=1, flags=re.S)
    # 「## 」ごとに折りたためるブロックにする
    parts = re.split(r"(?=<h2>)", body)
    out = [parts[0]]
    for p in parts[1:]:
        m = re.match(r"<h2>(.*?)</h2>(.*)", p, re.S)
        title, rest = m.group(1), m.group(2)
        out.append(f'<details class="step"><summary>{title}</summary><div class="inner">{rest}</div></details>')
    h = "\n".join(out)
    # 添付ファイル名を画像へのリンクに
    for name, path, _ in IMAGES:
        base = os.path.basename(name)
        h = h.replace(f"<code>{name}</code>", f'<a class="file" href="{rel(path)}" download="{base}"><code>{name}</code> ⬇</a>')
        if "/" not in name:
            continue
    return h


def build():
    todo = md(open(os.path.join(ROOT, "docs/assets-todo.md"), encoding="utf-8").read())
    todo = re.sub(r"^<h1>.*?</h1>", "", todo, count=1, flags=re.S)
    tools = "".join(
        f'<a class="tool" href="{rel(p)}"><b>{html.escape(n)}</b><span>{html.escape(d)}</span></a>' for n, p, d in TOOLS)
    imgs = "".join(
        f'<a class="img" href="{rel(p)}" download="{os.path.basename(p)}"><img loading="lazy" src="{rel(p)}" alt="">'
        f'<span>{html.escape(label)}<small>{html.escape(n)}</small></span></a>' for n, p, label in IMAGES
        if os.path.exists(os.path.join(ROOT, p)))
    docs = "".join(f'<a class="doc" href="{REPO}{p}">{html.escape(n)}</a>' for n, p in DOCS)
    prev = ""
    for label, p, kind in PREVIEWS:
        if not os.path.exists(os.path.join(ROOT, p)):
            continue
        media = (f'<video src="{rel(p)}" controls playsinline preload="metadata"></video>' if kind == "video"
                 else f'<a href="{rel(p)}"><img loading="lazy" src="{rel(p)}" alt=""></a>')
        prev += f'<figure>{media}<figcaption>{html.escape(label)}</figcaption></figure>'
    today = datetime.date.today().isoformat()
    page = TEMPLATE.replace("{{TOOLS}}", tools).replace("{{PROMPTS}}", prompts_html()).replace("{{IMAGES}}", imgs) \
        .replace("{{TODO}}", todo).replace("{{DOCS}}", docs).replace("{{PREVIEWS}}", prev).replace("{{DATE}}", today)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(page)
    print("書き出し完了:", OUT)


TEMPLATE = r"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>シネマホリック まとめ</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@500;700;900&display=swap" rel="stylesheet">
<style>
:root{--ink:#1f150f;--night:#1b1511;--night2:#2c221b;--night3:#3d3026;--cream:#f0e4cc;--dim:#b0a088;--parka:#b0422e;--gold:#c9a35a;--green:#4a6e58}
*{box-sizing:border-box}
html,body{margin:0;background:var(--night);color:var(--cream);font-family:"Noto Sans JP","Hiragino Sans",sans-serif;overflow-x:hidden;line-height:1.7}
.wrap{max-width:860px;margin:0 auto;padding:16px}
header{padding:18px 0 6px}
header h1{font-size:26px;font-weight:900;margin:0;letter-spacing:.04em}
header p{margin:4px 0 0;color:var(--dim);font-size:13px}
nav{position:sticky;top:0;z-index:5;background:var(--night);display:flex;gap:6px;overflow-x:auto;padding:10px 0;border-bottom:2px solid var(--ink)}
nav a{flex:none;color:var(--cream);text-decoration:none;background:var(--night2);border:2px solid var(--ink);border-radius:999px;padding:6px 12px;font-size:13px;font-weight:700}
section{margin:26px 0}
h2.sec{font-size:19px;font-weight:900;color:var(--gold);margin:0 0 10px;border-left:6px solid var(--parka);padding-left:10px}
.tools{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:10px}
.tool{display:block;background:var(--parka);color:var(--cream);text-decoration:none;border:2px solid var(--ink);border-radius:14px;padding:14px}
.tool b{display:block;font-size:17px}
.tool span{font-size:12px;opacity:.9}
.tool:last-child{background:var(--night3)}
details.step{background:var(--night2);border:2px solid var(--ink);border-radius:14px;margin:10px 0;overflow:hidden}
details.step>summary{cursor:pointer;padding:12px 14px;font-weight:900;font-size:16px;list-style:none}
details.step>summary::before{content:"▸ ";color:var(--gold)}
details.step[open]>summary::before{content:"▾ "}
.inner{padding:0 14px 14px}
.inner h3{font-size:15px;color:var(--gold);margin:16px 0 6px}
pre{position:relative;background:#120d0a;border:2px solid var(--ink);border-radius:10px;padding:12px 12px 44px;white-space:pre-wrap;word-break:break-word;font-size:13px;line-height:1.55;color:#e8dcc4}
pre button.copy{position:absolute;right:8px;bottom:8px;background:var(--parka);color:var(--cream);border:2px solid var(--ink);border-radius:8px;padding:6px 12px;font:inherit;font-size:13px;font-weight:700;cursor:pointer}
pre button.copy.done{background:var(--green)}
code{background:var(--night3);border-radius:5px;padding:1px 5px;font-size:.92em}
pre code{background:none;padding:0}
table{width:100%;border-collapse:collapse;font-size:13px;margin:8px 0;display:block;overflow-x:auto}
th,td{border:1px solid var(--night3);padding:6px 8px;text-align:left;vertical-align:top}
th{background:var(--night3)}
a{color:var(--gold)}
a.file{text-decoration:none;white-space:nowrap}
.imgs{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
.img{display:block;background:var(--night2);border:2px solid var(--ink);border-radius:12px;overflow:hidden;text-decoration:none;color:var(--cream)}
.img img{display:block;width:100%;aspect-ratio:2/3;object-fit:contain;background:repeating-conic-gradient(#3d3026 0 25%,#2c221b 0 50%) 0 0/20px 20px}
.img span{display:block;padding:8px;font-size:12px;font-weight:700}
.img small{display:block;color:var(--dim);font-weight:500;word-break:break-all}
.docs{display:flex;flex-wrap:wrap;gap:8px}
.doc{background:var(--night2);border:2px solid var(--ink);border-radius:10px;padding:8px 12px;text-decoration:none;color:var(--cream);font-size:14px}
.prev{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}
figure{margin:0;background:var(--night2);border:2px solid var(--ink);border-radius:12px;overflow:hidden}
figure img,figure video{display:block;width:100%;background:#000}
figcaption{padding:8px;font-size:13px;font-weight:700}
.box{background:var(--night2);border:2px solid var(--ink);border-radius:14px;padding:4px 14px}
.note{font-size:12px;color:var(--dim)}
footer{color:var(--dim);font-size:12px;padding:30px 0}
</style>
</head>
<body>
<div class="wrap">
<header><h1>シネマホリック まとめ</h1><p>道具・プロンプト・画像・資料へのリンクを全部ここに。更新：{{DATE}}</p></header>
<nav><a href="#tools">道具</a><a href="#prompts">ChatGPTプロンプト</a><a href="#images">添付する画像</a><a href="#todo">必要な素材</a><a href="#preview">確認用</a><a href="#docs">資料</a></nav>

<section id="tools"><h2 class="sec">道具</h2><div class="tools">{{TOOLS}}</div>
<p class="note">どれもスマホ・PCのブラウザで使えます。「JSONをコピー」して Claude に渡すと、同じ見た目で高画質に書き出します。</p></section>

<section id="prompts"><h2 class="sec">ChatGPTプロンプト</h2>
<p class="note">各プロンプトの「コピー」ボタンで写せます。添付するファイル名（⬇）を押すと画像を保存できます。</p>
{{PROMPTS}}</section>

<section id="images"><h2 class="sec">添付する画像（押すと保存）</h2><div class="imgs">{{IMAGES}}</div></section>

<section id="todo"><h2 class="sec">まだ必要な素材</h2><div class="box">{{TODO}}</div></section>

<section id="preview"><h2 class="sec">確認用</h2><div class="prev">{{PREVIEWS}}</div></section>

<section id="docs"><h2 class="sec">資料（GitHub）</h2><div class="docs">{{DOCS}}</div></section>

<footer>このページは <code>python3 scripts/build_hub.py</code> で作り直せます。</footer>
</div>
<script>
document.querySelectorAll("pre").forEach(pre=>{
  const b=document.createElement("button"); b.className="copy"; b.textContent="コピー";
  b.onclick=async()=>{ const text=pre.querySelector("code")?.innerText||pre.innerText;
    try{ await navigator.clipboard.writeText(text); }catch(e){ const r=document.createRange(); r.selectNodeContents(pre.querySelector("code")||pre); const s=getSelection(); s.removeAllRanges(); s.addRange(r); document.execCommand("copy"); s.removeAllRanges(); }
    b.textContent="コピーしました"; b.classList.add("done"); setTimeout(()=>{ b.textContent="コピー"; b.classList.remove("done"); },1600); };
  pre.appendChild(b);
});
// 開いていた手順を覚えておく（この端末だけ）
document.querySelectorAll("details.step").forEach((d,i)=>{ try{ if(localStorage.getItem("hub-open-"+i)==="1") d.open=true; }catch(e){}
  d.addEventListener("toggle",()=>{ try{ localStorage.setItem("hub-open-"+i,d.open?"1":"0"); }catch(e){} }); });
</script>
</body>
</html>
"""

if __name__ == "__main__":
    build()
