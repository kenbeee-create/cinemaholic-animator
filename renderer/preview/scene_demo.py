"""会話シーンの見え方の試作：キャラに寄ったカメラ・待機の動き・動く小物・映画カード。

使い方：
    python3 renderer/preview/scene_demo.py <movie.json> <出力.mp4>
"""
from __future__ import annotations

import json
import math
import os
import random
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "renderer"))
sys.path.insert(0, os.path.join(ROOT, "renderer/preview"))
from johndoe_reactions import PLACE, place, room, to_screen  # noqa: E402
from storyboard import gonbe, put_johndoe, caption  # noqa: E402

W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
INK = (31, 21, 15, 255)
CREAM = (240, 228, 204, 255)
DIM = (176, 160, 136, 255)
RED = (196, 70, 47, 255)
KV = W / 1024


def kv(x, y):
    """完成図（1024x1536）の座標 → 画面（1080x1920）の座標。"""
    return x * KV, y * KV + (H - round(1536 * KV)) // 2


def f(path, size):
    return ImageFont.truetype(path, size, index=0)


# ---------- カメラ ----------
def camera(fr, zoom, center):
    """center を中心に zoom 倍に寄る（画面からはみ出さないよう中心を調整）。"""
    w, h = W / zoom, H / zoom
    cx = min(max(center[0], w / 2), W - w / 2)
    cy = min(max(center[1], h / 2), H - h / 2)
    box = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    return fr.transform((W, H), Image.EXTENT, box, resample=Image.BICUBIC)


# ---------- 動く小物（毎回入る） ----------
def lamp_glow(fr, t):
    x, y = kv(215, 480)
    a = 70 + 18 * math.sin(t * 9.0) * math.sin(t * 2.3) + 10 * math.sin(t * 23)
    g = Image.new("RGBA", fr.size, (0, 0, 0, 0))
    ImageDraw.Draw(g).ellipse((x - 230, y - 230, x + 230, y + 230), fill=(255, 190, 90, int(max(0, a))))
    fr.alpha_composite(g.filter(ImageFilter.GaussianBlur(70)))


def tv_light(fr, t):
    a = 16 + 10 * math.sin(t * 3.1) + 8 * math.sin(t * 7.7 + 1)
    fr.alpha_composite(Image.new("RGBA", fr.size, (110, 150, 220, int(max(0, a)))))


def window_stars(fr, t):
    d = ImageDraw.Draw(fr)
    rnd = random.Random(3)
    for i in range(9):
        x, y = kv(rnd.uniform(8, 95), rnd.uniform(100, 255))
        b = 0.5 + 0.5 * math.sin(t * rnd.uniform(2, 5) + i)
        r = 2 + 3 * b
        d.ellipse((x - r, y - r, x + r, y + r), fill=(250, 240, 200, int(120 + 135 * b)))


def mug_and_steam(fr, t):
    x, y = kv(470, 1035)
    d = ImageDraw.Draw(fr)
    d.rounded_rectangle((x - 34, y - 70, x + 34, y), 12, fill=(214, 120, 70, 255), outline=INK, width=5)
    d.arc((x + 20, y - 58, x + 58, y - 18), -90, 90, fill=INK, width=6)
    d.ellipse((x - 34, y - 80, x + 34, y - 60), fill=(90, 50, 30, 255), outline=INK, width=4)
    st = Image.new("RGBA", fr.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(st)
    for k in range(3):
        ph = (t * 0.6 + k / 3) % 1
        pts = []
        for j in range(12):
            u = j / 11
            yy = y - 90 - u * 150 - ph * 60
            xx = x + (k - 1) * 18 + 14 * math.sin(u * 6 + t * 3 + k)
            pts.append((xx, yy))
        sd.line(pts, fill=(245, 240, 230, int(150 * (1 - ph))), width=8, joint="curve")
    fr.alpha_composite(st.filter(ImageFilter.GaussianBlur(3)))


def dust(fr, t):
    d = ImageDraw.Draw(fr)
    rnd = random.Random(11)
    lx, ly = kv(215, 520)
    for i in range(14):
        ox, oy = rnd.uniform(-180, 180), rnd.uniform(-200, 260)
        x = lx + ox + 20 * math.sin(t * 0.7 + i)
        y = ly + oy - (t * 18 + i * 37) % 300
        a = int(90 + 80 * math.sin(t * 2 + i))
        d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 230, 170, max(0, a)))


# ---------- 映画カード ----------
def movie_card(fr, m, p):
    """下からせり上がるカード。p=0→1 で出る。"""
    if p <= 0:
        return
    e = 1 - (1 - min(1, p)) ** 3
    x0, x1 = 60, 880
    h = 430
    y0 = 1110 + (1 - e) * 500
    card = Image.new("RGBA", fr.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((x0 + 10, y0 + 14, x1 + 10, y0 + h + 14), 28, fill=(0, 0, 0, 150))
    d.rounded_rectangle((x0, y0, x1, y0 + h), 28, fill=(32, 25, 20, 240), outline=INK, width=6)
    # ポスター枠（オリジナルの絵を入れる）
    px0, py0, pw, ph = x0 + 28, y0 + 28, 250, h - 56
    poster = m.get("poster")
    pp = os.path.join(ROOT, poster) if poster else None
    if pp and os.path.exists(pp):
        im = Image.open(pp).convert("RGBA")
        im = im.resize((pw, ph), Image.LANCZOS)
        card.alpha_composite(im, (int(px0), int(py0)))
    else:
        d.rectangle((px0, py0, px0 + pw, py0 + ph), fill=(70, 55, 44, 255))
        d.text((px0 + pw / 2, py0 + ph / 2), "ポスター\n（オリジナル絵）", font=f(FONT_B, 26), fill=DIM, anchor="mm",
               align="center")
    d.rectangle((px0, py0, px0 + pw, py0 + ph), outline=INK, width=5)
    # 文字
    tx = px0 + pw + 30
    d.text((tx, y0 + 40), m["title"], font=f(FONT, 50), fill=CREAM)
    d.text((tx, y0 + 108), f"{m['year']}年／{m['director']}／{m['runtime_min']}分", font=f(FONT_B, 24), fill=DIM)
    one = m.get("one_liner", "")
    if one.startswith("（"):
        one = "ひと言の紹介（台本と一緒に確定）"
    d.text((tx, y0 + 150), one[:16], font=f(FONT_B, 28), fill=CREAM)
    d.text((tx, y0 + 205), "観られる", font=f(FONT, 26), fill=(201, 163, 90, 255))
    by = y0 + 245
    bx = tx
    order = sorted(m["streaming"], key=lambda s: 0 if "見放題" in s["type"] else 1)
    for s in order[:5]:
        label = s["service"] + ("" if "見放題" not in s["type"] else " 見放題")
        fnt = f(FONT_B, 24)
        w = fnt.getlength(label) + 28
        if bx + w > x1 - 24:
            bx = tx
            by += 50
        fill = (176, 66, 46, 255) if "見放題" in s["type"] else (70, 55, 44, 255)
        d.rounded_rectangle((bx, by, bx + w, by + 40), 20, fill=fill, outline=INK, width=3)
        d.text((bx + w / 2, by + 20), label, font=fnt, fill=CREAM, anchor="mm")
        bx += w + 10
    rest = len(m["streaming"]) - 5
    d.text((tx, y0 + h - 44), (f"ほか{rest}サービス　" if rest > 0 else "") + f"{m['streaming_as_of']}時点",
           font=f(FONT_B, 20), fill=DIM)
    fr.alpha_composite(card)


def main(movie_path, out):
    m = json.load(open(movie_path, encoding="utf-8"))
    base_room = room()
    g_open = gonbe(None, "mouth_open")
    g_half = gonbe(None, "mouth_half")
    g_closed = gonbe()
    g_blink = gonbe("eyes_closed")
    gx0, gy0 = to_screen("gonbe", 506, 192)
    jx0, jy0 = to_screen("johndoe", 564, 259)
    pair_center = ((gx0 + jx0) / 2, (gy0 + jy0) / 2 + 260)
    dur = 9.0
    n = int(dur * FPS)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out],
                          stdin=subprocess.PIPE)
    for i in range(n):
        t = i / FPS
        fr = base_room.copy()
        window_stars(fr, t)
        lamp_glow(fr, t)
        dust(fr, t)
        # ごんべぇ：呼吸（足元を中心に少し伸び縮み）＋まばたき＋しゃべる口
        talking = 0.3 < t < 2.2
        img = g_closed
        if talking:
            img = [g_closed, g_half, g_open, g_half][int(t * 10) % 4]
        if (t % 3.1) < 0.12 and not talking:
            img = g_blink
        br = 1 + 0.008 * math.sin(t * 2 * math.pi / 2.6)
        place(fr, img, "gonbe", (1.0, br), anchor_src=(506, 1375))
        # じょんどぅー：待機 → 首かしげ → 乗り出して話す
        if t < 2.4:
            put_johndoe(fr, "idle", t)
        elif t < 4.0:
            put_johndoe(fr, "tilt", t - 2.4, "mouth_half" if int(t * 8) % 2 else None)
        else:
            put_johndoe(fr, "lean_in", t - 4.0, ["mouth_half", "mouth_open", None][int(t * 9) % 3] if t < 5.4 else None)
        mug_and_steam(fr, t)
        tv_light(fr, t)
        # カメラ：2人に寄った画をゆっくり押す。セリフで寄る先を変える
        if t < 2.4:
            z = 1.45 + 0.04 * t
            c = (pair_center[0] - 40, pair_center[1])
        elif t < 4.0:
            z = 1.9
            c = (jx0, jy0 + 280)
        else:
            z = 1.5 + 0.02 * (t - 4)
            c = pair_center
        shot = camera(fr, z, c)
        if talking:
            caption(shot, ["今日マジで", "上司が", "ありえなくて"][min(2, int((t - 0.3) / 0.65))], "gonbe", (W * 0.46, 1380))
        elif 2.4 <= t < 4.0:
            caption(shot, ["…それ", m["title"] + "、見た？"][0 if t < 3.0 else 1], "johndoe", (W * 0.46, 1380))
        movie_card(shot, m, (t - 4.4) / 0.45)
        ff.stdin.write(shot.convert("RGB").tobytes())
    ff.stdin.close()
    ff.wait()
    print("書き出し完了:", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
