"""映画館のセット（後ろから2人を撮る）のイメージを、コードで描く。

スクリーンには本物の予告を流さず、
  mode="light" … その映画の色合いの光のちらつき＋カットの切り替わり（見せ方1）
  mode="motif" … オリジナルの「それっぽい」モチーフ絵をぼかして流す（見せ方2）
  mode="licensed" … 許可が取れた予告の場所（灰色の札。見せ方3）
2人は後ろ姿。スクリーンの光が背中と頭の輪郭に当たる。

使い方：
    python3 renderer/preview/theater_mock.py            … 絵コンテ（docs/storyboard/theater_storyboard.jpg）と動き見本（output/theater_demo.mp4）
"""
from __future__ import annotations

import math
import os
import subprocess

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
W, H = 1080, 1920
INK = (31, 21, 15)
BLACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
F = lambda p, s: ImageFont.truetype(p, s, index=0)
SCREEN = (150, 230, 930, 690)  # スクリーンの位置（x0,y0,x1,y1）

# 映画ごとの色（例：雨のネオン街ふうの新作）
PALETTES = {"neon": [(255, 70, 160), (60, 200, 255), (250, 190, 90), (120, 90, 255)],
            "warm": [(255, 170, 80), (230, 90, 60), (250, 220, 150), (120, 60, 40)],
            "space": [(40, 70, 160), (200, 220, 255), (90, 40, 140), (250, 200, 120)]}


def rng(seed):
    r = np.random.default_rng(seed)
    return r


# ---------------- スクリーンの中身 ----------------
def screen_content(t, mode, pal_name="neon", motif="city"):
    sw, sh = SCREEN[2] - SCREEN[0], SCREEN[3] - SCREEN[1]
    pal = PALETTES[pal_name]
    cut = int(t / 0.9)  # 0.9秒ごとにカットが切り替わる
    ph = (t % 0.9) / 0.9
    im = Image.new("RGB", (sw, sh), (20, 16, 14))
    d = ImageDraw.Draw(im)
    if mode == "light":
        a, b = pal[cut % len(pal)], pal[(cut + 1) % len(pal)]
        r = rng(cut)
        for i in range(5):  # 大きな色のかたまりがゆっくり動く
            cx = r.uniform(0, sw) + 60 * math.sin(t * 1.3 + i)
            cy = r.uniform(0, sh) + 30 * math.cos(t + i)
            rad = r.uniform(120, 260)
            c = a if i % 2 else b
            d.ellipse((cx - rad, cy - rad * 0.7, cx + rad, cy + rad * 0.7), fill=c)
        im = im.filter(ImageFilter.GaussianBlur(45))
    elif mode == "motif":
        m = ["city", "space", "run"][cut % 3] if motif == "mix" else motif
        if m == "city":  # 雨のネオン街（オリジナル）
            d.rectangle((0, 0, sw, sh), fill=(30, 26, 60))
            for i in range(9):
                x = i * sw / 9
                h = 160 + (i * 73) % 220
                d.rectangle((x, sh - h, x + sw / 9 - 8, sh), fill=(18, 16, 36))
                for k in range(4):
                    d.rectangle((x + 14, sh - h + 20 + k * 40, x + 40, sh - h + 34 + k * 40), fill=pal[(i + k) % 4])
            for i in range(60):
                x = (i * 37 + t * 400) % sw
                y = (i * 53 + t * 900) % sh
                d.line((x, y, x - 6, y + 26), fill=(180, 200, 240), width=2)
        elif m == "space":
            d.rectangle((0, 0, sw, sh), fill=(12, 14, 40))
            r = rng(7)
            for i in range(80):
                x, y = r.uniform(0, sw), r.uniform(0, sh)
                d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(240, 240, 255))
            px = sw * 0.6 - ph * 60
            d.ellipse((px - 150, 120, px + 150, 420), fill=(200, 120, 80))
            d.ellipse((px - 230, 250, px + 230, 300), outline=(240, 200, 150), width=8)
        else:  # 走る影
            d.rectangle((0, 0, sw, sh), fill=(230, 120, 70))
            d.rectangle((0, sh * 0.72, sw, sh), fill=(60, 30, 20))
            x = 100 + ph * (sw - 200)
            y = sh * 0.72
            d.ellipse((x - 30, y - 230, x + 30, y - 170), fill=(20, 10, 8))
            d.polygon([(x - 35, y - 170), (x + 35, y - 170), (x + 25, y - 60), (x - 25, y - 60)], fill=(20, 10, 8))
            s = math.sin(ph * 12)
            d.line((x, y - 60, x + 50 * s, y), fill=(20, 10, 8), width=22)
            d.line((x, y - 60, x - 50 * s, y), fill=(20, 10, 8), width=22)
        im = im.filter(ImageFilter.GaussianBlur(9))  # ぼんやり
    else:  # licensed
        d.rectangle((0, 0, sw, sh), fill=(110, 110, 110))
        d.text((sw / 2, sh / 2 - 30), "許可が取れた予告", font=F(BLACK, 52), fill=(255, 255, 255), anchor="mm")
        d.text((sw / 2, sh / 2 + 40), "（配給会社の条件どおりに使う）", font=F(BOLD, 32), fill=(235, 235, 235), anchor="mm")
    # カットの頭で一瞬だけ明るく（切り替わりの感じ）
    flash = max(0, 1 - ph / 0.12)
    if flash > 0 and mode != "licensed":
        im = Image.blend(im, Image.new("RGB", im.size, (255, 255, 255)), 0.25 * flash)
    return im


def screen_color(img):
    a = np.array(img.resize((16, 9))).reshape(-1, 3).mean(0)
    return tuple(int(v) for v in a)


# ---------------- 部屋（客席） ----------------
ROWS = [(960, 46, 18), (1060, 58, 15), (1180, 74, 12), (1330, 96, 10), (1560, 126, 8), (1800, 160, 7)]


def seat_rows(d, rows):
    for y, h, n in rows:
        w = W / n
        for i in range(n + 1):
            x = i * w - (w / 2 if (y // 10) % 2 else 0)
            d.rounded_rectangle((x + 6, y - h, x + w - 6, y + h * 0.4), int(h * 0.35), fill=(120, 28, 30), outline=INK, width=4)
            d.rounded_rectangle((x + 14, y - h + 10, x + w - 14, y - h * 0.35), int(h * 0.25), fill=(140, 36, 36))


def front_rows():
    """2人より手前の列（2人の体の下のほうを隠す）。"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    seat_rows(ImageDraw.Draw(lay), ROWS[5:])
    return lay


def theater_bg():
    im = Image.new("RGB", (W, H), (34, 20, 18))
    d = ImageDraw.Draw(im)
    # 壁と天井
    d.rectangle((0, 0, W, 900), fill=(46, 26, 22))
    for x in range(0, W, 90):
        d.rectangle((x, 0, x + 44, 900), fill=(52, 30, 25))
    # カーテン
    d.rectangle((70, 180, 150, 760), fill=(110, 30, 28))
    d.rectangle((930, 180, 1010, 760), fill=(110, 30, 28))
    d.rectangle((70, 170, 1010, 230), fill=(120, 34, 30))
    # 床
    d.rectangle((0, 900, W, H), fill=(28, 16, 14))
    # 客席（奥から手前へ、だんだん大きく）
    seat_rows(d, ROWS[:5])
    return im


# ---------------- 2人の後ろ姿 ----------------
def back_views():
    """ごんべぇ（左）とじょんどぅー（右）の後ろ姿を、透過の1枚で描く。"""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    lw = 8
    # ごんべぇ：赤いパーカーの肩とフード、茶色い垂れ耳、こげ茶のニット帽
    gx, gy = 360, 1300
    d.rounded_rectangle((gx - 190, gy + 40, gx + 190, gy + 420), 120, fill=(176, 50, 36), outline=INK, width=lw)   # 肩
    d.rounded_rectangle((gx - 120, gy - 10, gx + 120, gy + 150), 70, fill=(150, 40, 30), outline=INK, width=lw)    # フード
    d.ellipse((gx - 150, gy - 230, gx - 60, gy + 10), fill=(110, 58, 22), outline=INK, width=lw)                   # 左耳
    d.ellipse((gx + 60, gy - 230, gx + 150, gy + 10), fill=(110, 58, 22), outline=INK, width=lw)                   # 右耳
    d.ellipse((gx - 110, gy - 250, gx + 110, gy - 10), fill=(154, 80, 21), outline=INK, width=lw)                  # 頭
    d.chord((gx - 125, gy - 330, gx + 125, gy - 60), 180, 360, fill=(66, 46, 34), outline=INK, width=lw)          # ニット帽
    d.rounded_rectangle((gx - 128, gy - 205, gx + 128, gy - 150), 24, fill=(56, 38, 28), outline=INK, width=lw)    # 帽子の折り返し
    for k in range(-4, 5):
        d.line((gx + k * 24, gy - 310 + abs(k) * 8, gx + k * 26, gy - 210), fill=INK, width=3)
    # じょんどぅー：黒いもじゃもじゃの大きな頭、クリーム色のTシャツの肩
    jx, jy = 720, 1290
    d.rounded_rectangle((jx - 210, jy + 50, jx + 210, jy + 420), 140, fill=(236, 220, 186), outline=INK, width=lw)
    r = 190
    pts = []
    for i in range(36):
        a = i / 36 * 2 * math.pi
        rr = r + (22 if i % 2 else 0)
        pts.append((jx + rr * math.cos(a), jy - 120 + rr * 0.92 * math.sin(a)))
    d.polygon(pts, fill=(40, 30, 24), outline=INK, width=lw)
    for i in range(14):  # 毛のくるくる
        a = i / 14 * 2 * math.pi
        cx, cy = jx + 110 * math.cos(a), jy - 120 + 100 * math.sin(a)
        d.arc((cx - 30, cy - 30, cx + 30, cy + 30), 200, 340, fill=(70, 56, 46), width=5)
    return lay


def rim(lay, color, strength):
    """スクリーンの光が、2人の頭と肩の上側の輪郭に当たる。"""
    a = lay.getchannel("A")
    shifted = ImageChops.offset(a, 0, 14)
    edge = ImageChops.subtract(a, shifted).filter(ImageFilter.GaussianBlur(4))
    glow = Image.new("RGBA", lay.size, color + (0,))
    glow.putalpha(edge.point(lambda v: int(min(255, v * strength))))
    return glow


BG = None
BACK = None
FRONT = None


def frame(t, mode="light", pal="neon", motif="city", cam="wide"):
    global BG, BACK, FRONT
    BG = BG or theater_bg()
    BACK = BACK or back_views()
    FRONT = FRONT or front_rows()
    scr = screen_content(t, mode, pal, motif)
    col = screen_color(scr)
    im = BG.copy()
    # スクリーン（枠＋中身）
    d = ImageDraw.Draw(im)
    d.rectangle((SCREEN[0] - 10, SCREEN[1] - 10, SCREEN[2] + 10, SCREEN[3] + 10), fill=INK)
    im.paste(scr, SCREEN[:2])
    # スクリーンの光が部屋にこぼれる
    spill = Image.new("RGB", (W, H), col)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).ellipse((-200, 200, W + 200, 1700), fill=int(70 if mode != "licensed" else 30))
    mask = mask.filter(ImageFilter.GaussianBlur(160))
    im = Image.composite(spill, im, mask)
    im = im.convert("RGBA")
    # 2人：暗めに沈めて、輪郭だけ光らせる
    dark = BACK.copy()
    arr = np.array(dark).astype(float)
    arr[..., :3] *= 0.62
    dark = Image.fromarray(arr.astype(np.uint8))
    # 話している間の小さな動き（呼吸・首）
    dy = int(4 * math.sin(t * 2.4))
    im.alpha_composite(dark, (0, dy))
    im.alpha_composite(rim(BACK, col, 2.2 if mode != "licensed" else 1.0), (0, dy))
    fr = np.array(FRONT).astype(float)
    fr[..., :3] *= 0.75
    im.alpha_composite(Image.fromarray(fr.astype(np.uint8)))
    im = im.convert("RGB")
    # カメラ
    if cam == "screen":   # スクリーンに寄る（2人の頭が下に少しだけ入る）
        bw = 560
        box = (260, 160, 260 + bw, 160 + int(bw * 16 / 9))
        im = im.crop(box).resize((W, H), Image.LANCZOS)
    elif cam == "heads":  # 2人の頭に寄る
        bw = 820
        box = (130, H - int(bw * 16 / 9), 130 + bw, H)
        im = im.crop(box).resize((W, H), Image.LANCZOS)
    return im


def caption(im, text, who):
    d = ImageDraw.Draw(im)
    f = F(BLACK, 62)
    tw = d.textlength(text, font=f)
    x, y = W * 0.46, 1660
    bg = (176, 66, 46) if who == "gonbe" else (240, 228, 204) if who == "johndoe" else (0, 0, 0)
    fg = (240, 228, 204) if who != "johndoe" else INK
    d.rectangle((x - tw / 2 - 24, y - 46, x + tw / 2 + 24, y + 46), fill=bg, outline=INK, width=5)
    d.text((x, y + 2), text, font=f, fill=fg, anchor="mm")
    return im


def storyboard():
    panels = [
        ("見せ方1：光と色だけ", frame(0.3, "light", "neon"), "スクリーンは映画の色の光だけ。0.9秒ごとに切り替わる", None, None),
        ("見せ方2：オリジナルの絵", frame(0.5, "motif", "neon", "city"), "雨のネオン街（自分たちの絵）。実在の場面は描かない", None, None),
        ("見せ方3：許可を取った予告", frame(0.5, "licensed"), "配給会社の許可が出たときだけ。条件どおりに", None, None),
        ("0–2秒 フック", frame(1.1, "light", "neon"), "ごんべぇ「この新作、予習いる？」", "この新作、予習いる？", "gonbe"),
        ("2–4秒", frame(2.0, "light", "warm", cam="heads"), "じょんどぅー「…いる。2本だけ」（頭を寄せる）", "…いる。2本だけ", "johndoe"),
        ("4–8秒 スクリーンに寄る", frame(2.6, "motif", "neon", "city", cam="screen"), "監督の前作のイメージ（オリジナルの絵）", "監督の前作が、これ", "johndoe"),
        ("8–12秒", frame(3.4, "motif", "space", "space", cam="screen"), "シリーズ1作目のイメージ（オリジナルの絵）", "1作目は、これだけ見とけ", "johndoe"),
        ("12–14秒", frame(4.1, "light", "space", cam="heads"), "ごんべぇ「公開いつ？」", "公開いつ？", "gonbe"),
    ]
    tw, th = 300, 533
    cols = 4
    rows = math.ceil(len(panels) / cols)
    cell = th + 120
    S = Image.new("RGB", (cols * (tw + 24) + 24, 130 + rows * (cell + 20)), (27, 21, 17))
    d = ImageDraw.Draw(S)
    d.text((24, 24), "シネマホリック 新作予習：映画館のイメージ絵コンテ", font=F(BLACK, 36), fill=(240, 228, 204))
    d.text((24, 78), "上の段＝スクリーンの見せ方3つ（本物の予告は使わない／許可が出たときだけ）。下の段＝回の流れの例", font=F(BOLD, 20), fill=(176, 160, 136))
    for n, (lab, img, note, cap, who) in enumerate(panels):
        if cap:
            img = caption(img.copy(), cap, who)
        x = 24 + (n % cols) * (tw + 24)
        y = 130 + (n // cols) * (cell + 20)
        S.paste(img.resize((tw, th), Image.LANCZOS), (x, y))
        d.rectangle((x, y, x + tw, y + th), outline=(201, 163, 90) if n < 3 else (61, 48, 38), width=3)
        d.text((x, y + th + 10), lab, font=F(BLACK, 21), fill=(201, 163, 90))
        f = F(BOLD, 18)
        line, yy = "", y + th + 42
        for ch in note:
            if f.getlength(line + ch) > tw:
                d.text((x, yy), line, font=f, fill=(214, 202, 180))
                yy += 24
                line = ch
            else:
                line += ch
        d.text((x, yy), line, font=f, fill=(214, 202, 180))
    out = os.path.join(ROOT, "docs/storyboard/theater_storyboard.jpg")
    S.save(out, quality=88)
    return out


def demo(seconds=8, fps=24):
    out = os.path.join(ROOT, "output/theater_demo.mp4")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "540x960", "-r", str(fps), "-i", "-",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "22", out], stdin=subprocess.PIPE)
    for i in range(seconds * fps):
        t = i / fps
        if t < 2.0:
            im = caption(frame(t, "light", "neon"), "この新作、予習いる？", "gonbe")
        elif t < 3.5:
            im = caption(frame(t, "light", "warm", cam="heads"), "…いる。2本だけ", "johndoe")
        elif t < 5.8:
            im = caption(frame(t, "motif", "neon", "city", cam="screen"), "監督の前作が、これ", "johndoe")
        else:
            im = caption(frame(t, "motif", "space", "space", cam="screen"), "1作目は、これだけ見とけ", "johndoe")
        p.stdin.write(im.resize((540, 960)).tobytes())
    p.stdin.close()
    p.wait()
    return out


if __name__ == "__main__":
    print(storyboard())
    print(demo())
