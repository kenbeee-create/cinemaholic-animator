"""ネオンの2人の顔に「シネマホリック」の文字をネオン管風に足して、タイトルアイコンを作る。

使い方：
    python3 renderer/templates/neon_logo.py

入力：assets/brand/neon_faces_source.png（オーナー提供の元画像）
出力：assets/brand/
    logo_neon.png        … 正方形（1024x1024）。アカウントのアイコン・タイトルに使う
    logo_neon_glow.png   … 文字だけを光った状態で透過にしたもの（ほかの場面に重ねる用）
"""
from __future__ import annotations

import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "assets/brand/neon_faces_source.png")
OUT = os.path.join(ROOT, "assets/brand")

TEXT = "シネマホリック"
SUB = "CINEMA HOLIC"
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"  # 細めの線＝ネオン管に見える
SUB_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-DemiLight.ttc"

CORE = (255, 196, 232)   # 管の芯（明るいピンク）
TUBE = (247, 105, 192)   # 管の色（元画像からとった色）
GLOW = (255, 30, 160)    # 外側の光


def tube_mask(size, draw_fn):
    m = Image.new("L", size, 0)
    draw_fn(ImageDraw.Draw(m))
    return m


def neon(mask: Image.Image) -> Image.Image:
    """白黒の線（mask）を、ネオン管の光り方にする（加算合成用のRGB）。"""
    size = mask.size
    out = Image.new("RGB", size, (0, 0, 0))

    def layer(m, color, k=1.0):
        col = Image.new("RGB", size, tuple(int(c * k) for c in color))
        return ImageChops.multiply(col, m.convert("RGB"))

    wide = mask.filter(ImageFilter.GaussianBlur(26))
    mid = mask.filter(ImageFilter.GaussianBlur(9))
    near = mask.filter(ImageFilter.GaussianBlur(3))
    out = ImageChops.add(out, layer(wide.point(lambda v: min(255, v * 2.2)), GLOW, 0.75))
    out = ImageChops.add(out, layer(mid.point(lambda v: min(255, v * 1.6)), GLOW, 0.9))
    out = ImageChops.add(out, layer(near, TUBE))
    core = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1))
    out = ImageChops.add(out, layer(core, CORE))
    return out


def build():
    base = Image.open(SRC).convert("RGB")
    W, H = base.size
    k = 2  # 2倍で描いて縮小
    size = (W * k, H * k)

    # 文字の大きさを幅に合わせる
    max_w = 880 * k
    fs = 150 * k
    while True:
        f = ImageFont.truetype(FONT, fs, index=0)
        if f.getlength(TEXT) <= max_w:
            break
        fs -= 4
    sf = ImageFont.truetype(SUB_FONT, 40 * k, index=0)
    sub = " ".join(SUB)  # 字間をあける

    y_text = 772 * k
    y_sub = y_text + int(fs * 1.12) + 6 * k

    def draw_text(d):
        d.text((W * k // 2, y_text), TEXT, font=f, fill=255, anchor="mt")

    def draw_sub(d):
        d.text((W * k // 2, y_sub), sub, font=sf, fill=255, anchor="mt")

    m_text = tube_mask(size, draw_text)
    m_sub = tube_mask(size, draw_sub)
    glow_text = neon(m_text).resize((W, H), Image.LANCZOS)
    glow_sub = neon(m_sub.point(lambda v: int(v * 0.85))).resize((W, H), Image.LANCZOS)
    glow = ImageChops.add(glow_text, glow_sub)

    # 文字の後ろを少し暗くして、顔の光と重ならないように
    shade = Image.new("L", (W, H), 0)
    ImageDraw.Draw(shade).rounded_rectangle((60, 760, W - 60, 1010), 60, fill=90)
    shade = shade.filter(ImageFilter.GaussianBlur(40))
    darker = Image.composite(Image.new("RGB", (W, H), (8, 0, 20)), base, shade)

    final = ImageChops.add(darker, glow)
    final.save(os.path.join(OUT, "logo_neon.png"))

    # 透過版（文字の光だけ）
    alpha = glow.convert("L").point(lambda v: min(255, int(v * 1.4)))
    rgba = glow.copy()
    rgba.putalpha(alpha)
    rgba.crop(rgba.getbbox()).save(os.path.join(OUT, "logo_neon_glow.png"))
    print("書き出し完了:", os.path.join(OUT, "logo_neon.png"))


if __name__ == "__main__":
    if not os.path.exists(SRC):
        print("元画像がありません:", SRC)
        sys.exit(1)
    build()
