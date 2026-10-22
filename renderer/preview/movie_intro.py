"""映画紹介の画面（画面ごと切り替える・処方箋ふう）のイメージ画像。

左に大きなポスター、右に映画の紹介、右下に白衣のじょんどぅーがひと言。
使い方：
    python3 renderer/preview/movie_intro.py <movie.json> <出力.png>
"""
from __future__ import annotations

import json
import os
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
W, H = 1080, 1920
BLACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc"
INK = (31, 21, 15, 255)
PAPER = (244, 236, 214, 255)
PAPER_LINE = (214, 200, 170, 255)
RED = (196, 70, 47, 255)
BROWN = (120, 96, 72, 255)
GREEN = (74, 110, 88, 255)


def f(p, s):
    return ImageFont.truetype(p, s, index=0)


def wrap(d, text, fnt, maxw):
    no_head = "、。，．・ー〜！？!?）」』…"
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=fnt) > maxw and cur and ch not in no_head:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def doctor_johndoe() -> Image.Image:
    """じょんどぅーに白衣と聴診器を描き足す（イメージ用の仮。本番はちゃんと描いた服を使う）。"""
    J = os.path.join(ROOT, "assets/characters/johndoe")
    im = Image.open(os.path.join(J, "base_closed.png")).convert("RGBA")
    a = np.array(im)
    shirt = (a[..., :3].astype(int).sum(axis=2) > 560) & (a[..., 3] > 200)
    ys, xs = np.where(shirt)
    cx = int(np.median(xs))
    top = ys.min()
    coat = shirt.copy()
    # 前は開いていて、Tシャツが見える
    for y in range(a.shape[0]):
        half = 70 + max(0, (y - top)) * 0.05
        coat[y, int(cx - half):int(cx + half)] = False
    a[coat, :3] = (250, 250, 246)
    out = Image.fromarray(a)
    d = ImageDraw.Draw(out)
    bottom = ys.max()
    for sgn in (-1, 1):
        x_top, x_bot = cx + sgn * 70, cx + sgn * (70 + (bottom - top) * 0.05)
        d.line((x_top, top, x_bot, bottom), fill=INK, width=6)
        # えり
        d.polygon([(cx + sgn * 70, top), (cx + sgn * 150, top - 5), (cx + sgn * 95, top + 120)], fill=(250, 250, 246, 255),
                  outline=INK, width=5)
    # 胸ポケットとペン
    px = cx + 170
    d.rectangle((px, top + 150, px + 90, top + 230), outline=INK, width=5)
    d.rectangle((px + 20, top + 120, px + 32, top + 175), fill=(60, 90, 160, 255), outline=INK, width=3)
    # 聴診器
    d.arc((cx - 160, top - 60, cx + 160, top + 230), 20, 160, fill=(70, 70, 76, 255), width=12)
    d.line((cx - 150, top + 120, cx - 150, top + 260), fill=(70, 70, 76, 255), width=10)
    d.ellipse((cx - 180, top + 250, cx - 120, top + 310), fill=(180, 180, 186, 255), outline=INK, width=5)
    return out.crop(out.getbbox())


def paper_bg() -> Image.Image:
    img = Image.new("RGBA", (W, H), (27, 21, 17, 255))
    paper = Image.new("RGBA", (W, H), PAPER)
    rnd = random.Random(5)
    noise = Image.new("L", (W // 4, H // 4))
    noise.putdata([128 + rnd.randint(-10, 10) for _ in range(noise.width * noise.height)])
    noise = noise.resize((W, H)).filter(ImageFilter.GaussianBlur(2))
    paper = Image.composite(paper, Image.new("RGBA", (W, H), (226, 214, 186, 255)), noise)
    img.alpha_composite(paper)
    return img


def poster(m, size):
    pw, ph = size
    pp = os.path.join(ROOT, m.get("poster", "")) if m.get("poster") else ""
    if pp and os.path.exists(pp):
        return Image.open(pp).convert("RGBA").resize(size, Image.LANCZOS)
    p = Image.new("RGBA", size, (56, 44, 36, 255))
    d = ImageDraw.Draw(p)
    for i in range(0, pw + ph, 26):
        d.line((i, 0, i - ph, ph), fill=(66, 52, 42, 255), width=10)
    d.text((pw / 2, ph / 2 - 30), "ポスター", font=f(BLACK, 46), fill=(214, 200, 170, 255), anchor="mm")
    d.text((pw / 2, ph / 2 + 30), "（公式 or オリジナル絵）", font=f(BOLD, 24), fill=(176, 160, 136, 255), anchor="mm")
    return p


# 配信サービスのアイコン：assets/ui/services/<id>.png があればそれを使う（公式のアイコンをオーナーが用意）。
# 無い間は、サービスの色の四角に名前を入れた仮のアイコン。
SERVICES = {
    "Netflix": ("netflix", (20, 20, 20), (229, 9, 20), "NETFLIX"),
    "U-NEXT": ("unext", (0, 0, 0), (255, 255, 255), "U-NEXT"),
    "WOWOWオンデマンド": ("wowow", (0, 32, 96), (255, 255, 255), "WOWOW"),
    "TELASA": ("telasa", (240, 90, 40), (255, 255, 255), "TELASA"),
    "Prime Video": ("primevideo", (0, 168, 225), (255, 255, 255), "prime\nvideo"),
    "DMM TV": ("dmmtv", (30, 30, 30), (255, 255, 255), "DMM TV"),
    "Disney+": ("disneyplus", (10, 30, 90), (255, 255, 255), "Disney+"),
    "Hulu": ("hulu", (28, 231, 131), (20, 20, 20), "Hulu"),
    "ABEMA": ("abema", (30, 30, 30), (255, 255, 255), "ABEMA"),
    "Lemino": ("lemino", (60, 60, 60), (255, 255, 255), "Lemino"),
    "FOD": ("fod", (230, 0, 18), (255, 255, 255), "FOD"),
    "J:COM STREAM": ("jcom", (0, 80, 160), (255, 255, 255), "J:COM"),
    "TSUTAYA DISCAS": ("discas", (0, 40, 120), (255, 255, 255), "DISCAS"),
    "music.jp": ("musicjp", (230, 60, 120), (255, 255, 255), "music.jp"),
}


def service_icon(name, size):
    sid, bg, fg, label = SERVICES.get(name, (name.lower(), (80, 80, 80), (255, 255, 255), name))
    path = os.path.join(ROOT, f"assets/ui/services/{sid}.png")
    if os.path.exists(path):
        return Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    k = 3
    im = Image.new("RGBA", (size * k, size * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, size * k - 1, size * k - 1), 26 * k, fill=bg + (255,))
    lines = label.split("\\n") if "\\n" in label else label.split("\n")
    fs = 30 * k
    while max(d.textlength(l, font=f(BLACK, fs)) for l in lines) > size * k * 0.82 and fs > 10:
        fs -= 2
    d.multiline_text((size * k / 2, size * k / 2), "\n".join(lines), font=f(BLACK, fs), fill=fg + (255,), anchor="mm",
                     align="center", spacing=2)
    return im.resize((size, size), Image.LANCZOS)


def doctor_standing():
    """白衣のじょんどぅー（立ち絵）。ChatGPTで作った素材があればそれを使う。無ければ座りの仮。"""
    p = os.path.join(ROOT, "assets/characters/johndoe/doctor_stand.png")
    if os.path.exists(p):
        im = Image.open(p).convert("RGBA")
        return im.crop(im.getbbox()), False
    return doctor_johndoe(), True


def build(m, out):
    img = paper_bg()
    d = ImageDraw.Draw(img)
    # ---- 見出し（処方箋ふう） ----
    d.text((60, 262), "処 方 箋", font=f(SERIF, 80), fill=INK, anchor="lm")
    d.text((62, 330), "CINEMA HOLIC 映画処方所", font=f(BOLD, 26), fill=BROWN, anchor="lm")
    d.text((890, 262), "No. 001", font=f(BOLD, 28), fill=BROWN, anchor="rm")
    d.text((890, 310), "患者：そこの君", font=f(BOLD, 28), fill=BROWN, anchor="rm")
    d.line((50, 368, 890, 368), fill=INK, width=5)
    d.line((50, 378, 890, 378), fill=INK, width=2)

    # ---- 左：大きなポスター（2:3） ----
    px0, py0, pw, ph = 50, 420, 560, 840
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((px0 + 12, py0 + 16, px0 + pw + 12, py0 + ph + 16), fill=(0, 0, 0, 90))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    img.alpha_composite(poster(m, (pw, ph)), (px0, py0))
    d.rectangle((px0, py0, px0 + pw, py0 + ph), outline=INK, width=6)
    for tx in (px0 + 40, px0 + pw - 120):
        d.rectangle((tx, py0 - 22, tx + 80, py0 + 20), fill=(232, 220, 170, 220))

    # ---- 右：紹介 ----
    rx, rw = 640, 250
    y = 425
    d.text((rx, y), "お薬の名前", font=f(BOLD, 22), fill=BROWN)
    y += 36
    for ln in wrap(d, m["title"], f(BLACK, 50), rw):
        d.text((rx, y), ln, font=f(BLACK, 50), fill=INK)
        y += 62
    y += 6
    for ln in [f"{m['year']}年／{m['runtime_min']}分"] + wrap(d, f"監督：{m['director']}", f(BOLD, 24), rw):
        d.text((rx, y), ln, font=f(BOLD, 24), fill=BROWN)
        y += 34
    y += 18
    d.line((rx, y, rx + rw, y), fill=PAPER_LINE, width=3)
    y += 20
    d.text((rx, y), "効きめ", font=f(BOLD, 22), fill=BROWN)
    one = m.get("one_liner", "")
    if one.startswith("（"):
        one = "ぜんぶ持ってるのに、空っぽな夜に。"
        d.text((rx + rw, y), "※例", font=f(BOLD, 20), fill=RED, anchor="ra")
    y += 36
    for ln in wrap(d, one, f(BLACK, 32), rw):
        d.text((rx, y), ln, font=f(BLACK, 32), fill=INK)
        y += 44
    y += 16
    d.line((rx, y, rx + rw, y), fill=PAPER_LINE, width=3)
    y += 20
    d.text((rx, y), "もらえる薬局", font=f(BOLD, 22), fill=BROWN)
    y += 40
    # アイコン：見放題を先に、3列×2段まで
    order = sorted(m["streaming"], key=lambda s: 0 if "見放題" in s["type"] else 1)
    size, gap = 72, 17
    for i, s in enumerate(order[:6]):
        cx = rx + (i % 3) * (size + gap)
        cy = y + (i // 3) * (size + 34)
        img.alpha_composite(service_icon(s["service"], size), (int(cx), int(cy)))
        d.rounded_rectangle((cx, cy, cx + size, cy + size), 18, outline=INK, width=3)
        d.text((cx + size / 2, cy + size + 4), "見放題" if "見放題" in s["type"] else "レンタル", font=f(BOLD, 17),
               fill=GREEN if "見放題" in s["type"] else BROWN, anchor="mt")
    y += 2 * (size + 34) + 4
    rest = len(m["streaming"]) - 6
    d.text((rx, y), (f"ほか{rest}　" if rest > 0 else "") + f"{m['streaming_as_of'].split('（')[0]}時点", font=f(BOLD, 18),
           fill=BROWN)

    # ---- はんこ（ポスターの角） ----
    cx, cy = px0 + pw - 85, py0 + ph - 90
    st = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.ellipse((cx - 80, cy - 80, cx + 80, cy + 80), outline=RED, width=9)
    sd.text((cx, cy), "処方", font=f(BLACK, 50), fill=RED, anchor="mm")
    img.alpha_composite(st.rotate(-14, center=(cx, cy)))

    # ---- 右下：白衣のじょんどぅー（立ち絵）＋ひと言 ----
    doc, temp = doctor_standing()
    target_h = 520
    s = target_h / doc.height
    doc = doc.resize((int(doc.width * s), target_h), Image.LANCZOS)
    dx = 905 - doc.width
    dy = 1290
    img.alpha_composite(doc, (dx, dy))
    if temp:
        d.text((dx + doc.width / 2, dy - 6), "（立ち絵は作成中）", font=f(BOLD, 18), fill=BROWN, anchor="mb")
    bx0, by0, bx1, by1 = 60, 1310, dx - 40, 1480
    d.rounded_rectangle((bx0, by0, bx1, by1), 40, fill=(255, 255, 255, 255), outline=INK, width=6)
    d.polygon([(bx1 - 10, by0 + 55), (bx1 + 50, by0 + 85), (bx1 - 10, by0 + 105)], fill=(255, 255, 255, 255))
    d.line([(bx1 - 4, by0 + 55), (bx1 + 50, by0 + 85), (bx1 - 4, by0 + 105)], fill=INK, width=6)
    d.text(((bx0 + bx1) / 2, (by0 + by1) / 2), "…一人で、深夜に。\nよく効くよ。", font=f(BLACK, 38), fill=INK,
           anchor="mm", align="center", spacing=12)

    img.convert("RGB").save(out)
    print("書き出し完了:", out)


if __name__ == "__main__":
    build(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2])
