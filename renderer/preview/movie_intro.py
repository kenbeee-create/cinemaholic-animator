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


def build(m, out):
    img = paper_bg()
    d = ImageDraw.Draw(img)
    # ---- 見出し（処方箋ふう） ----
    d.text((70, 250), "処 方 箋", font=f(SERIF, 84), fill=INK, anchor="lm")
    d.text((72, 320), "CINEMA HOLIC 映画処方所", font=f(BOLD, 28), fill=BROWN, anchor="lm")
    d.text((880, 250), "No. 001", font=f(BOLD, 30), fill=BROWN, anchor="rm")
    d.text((880, 300), "患者：そこの君", font=f(BOLD, 30), fill=BROWN, anchor="rm")
    d.line((60, 360, 890, 360), fill=INK, width=5)
    d.line((60, 370, 890, 370), fill=INK, width=2)

    # ---- 左：大きなポスター ----
    px0, py0, pw, ph = 60, 410, 470, 705
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).rectangle((px0 + 12, py0 + 16, px0 + pw + 12, py0 + ph + 16), fill=(0, 0, 0, 90))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    img.alpha_composite(poster(m, (pw, ph)), (px0, py0))
    d.rectangle((px0, py0, px0 + pw, py0 + ph), outline=INK, width=6)
    # テープ
    for tx in (px0 + 40, px0 + pw - 120):
        d.rectangle((tx, py0 - 22, tx + 80, py0 + 20), fill=(232, 220, 170, 220))

    # ---- 右：紹介 ----
    rx, rw = 560, 330
    y = 420
    d.text((rx, y), "お薬の名前", font=f(BOLD, 24), fill=BROWN)
    y += 40
    for ln in wrap(d, m["title"], f(BLACK, 58), rw):
        d.text((rx, y), ln, font=f(BLACK, 58), fill=INK)
        y += 72
    d.text((rx, y + 4), f"{m['year']}年／{m['runtime_min']}分", font=f(BOLD, 26), fill=BROWN)
    y += 42
    for ln in wrap(d, f"監督：{m['director']}", f(BOLD, 26), rw):
        d.text((rx, y), ln, font=f(BOLD, 26), fill=BROWN)
        y += 38
    y += 32
    d.line((rx, y, rx + rw, y), fill=PAPER_LINE, width=3)
    y += 24
    d.text((rx, y), "効きめ", font=f(BOLD, 24), fill=BROWN)
    y += 40
    one = m.get("one_liner", "")
    if one.startswith("（"):
        one = "ぜんぶ持ってるのに、空っぽな夜に。"
        d.text((rx + rw, y - 36), "※例", font=f(BOLD, 20), fill=RED, anchor="ra")
    for ln in wrap(d, one, f(BLACK, 36), rw):
        d.text((rx, y), ln, font=f(BLACK, 36), fill=INK)
        y += 50
    y += 20
    d.line((rx, y, rx + rw, y), fill=PAPER_LINE, width=3)
    y += 24
    d.text((rx, y), "もらえる薬局（配信）", font=f(BOLD, 24), fill=BROWN)
    y += 44
    order = sorted(m["streaming"], key=lambda s: 0 if "見放題" in s["type"] else 1)
    for s in order[:5]:
        mine = "見放題" in s["type"]
        d.rounded_rectangle((rx, y, rx + rw, y + 48), 24, fill=GREEN if mine else (255, 255, 255, 0), outline=INK, width=3)
        fs = 26
        while d.textlength(s["service"], font=f(BLACK, fs)) > rw - 130 and fs > 16:
            fs -= 1
        d.text((rx + 20, y + 24), s["service"], font=f(BLACK, fs), fill=PAPER if mine else INK, anchor="lm")
        d.text((rx + rw - 18, y + 24), "見放題" if mine else "レンタル", font=f(BOLD, 20),
               fill=PAPER if mine else BROWN, anchor="rm")
        y += 58
    rest = len(m["streaming"]) - 5
    d.text((rx, y + 6), (f"ほか{rest}　" if rest > 0 else "") + f"{m['streaming_as_of'].split('（')[0]}時点",
           font=f(BOLD, 20), fill=BROWN)

    # ---- 右下：白衣のじょんどぅー＋ひと言 ----
    doc = doctor_johndoe()
    s = 360 / doc.width
    doc = doc.resize((int(doc.width * s), int(doc.height * s)), Image.LANCZOS)
    img.alpha_composite(doc, (W - doc.width - 190, 1430))
    bx0, by0, bx1, by1 = 110, 1400, 540, 1560
    d.rounded_rectangle((bx0, by0, bx1, by1), 40, fill=(255, 255, 255, 255), outline=INK, width=6)
    d.polygon([(bx1 - 10, by0 + 60), (bx1 + 60, by0 + 100), (bx1 - 10, by0 + 110)], fill=(255, 255, 255, 255))
    d.line([(bx1 - 4, by0 + 60), (bx1 + 60, by0 + 100), (bx1 - 4, by0 + 110)], fill=INK, width=6)
    d.text(((bx0 + bx1) / 2, (by0 + by1) / 2), "…一人で、深夜に。\nよく効くよ。", font=f(BLACK, 38), fill=INK,
           anchor="mm", align="center", spacing=12)

    # ---- はんこ ----
    cx, cy = 470, 1110
    st = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    sd.ellipse((cx - 85, cy - 85, cx + 85, cy + 85), outline=RED, width=9)
    sd.text((cx, cy), "処方", font=f(BLACK, 54), fill=RED, anchor="mm")
    img.alpha_composite(st.rotate(-14, center=(cx, cy)))

    img.convert("RGB").save(out)
    print("書き出し完了:", out)


if __name__ == "__main__":
    build(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2])
