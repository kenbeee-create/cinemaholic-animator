"""じょんどぅーのリアクション一覧を、部屋の中で動かした確認用動画にする。

使い方：
    python3 renderer/preview/johndoe_reactions.py <出力.mp4>
"""
from __future__ import annotations

import json
import math
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "renderer"))
from motion.reactions import REACTIONS, pose  # noqa: E402

W, H, FPS = 1080, 1920, 30
SEG = 1.5  # 1つのリアクションの長さ（秒）

# 完成図（1024x1536）の中での置き場所。元の絵のこの範囲（src_bbox）を、この倍率で、ここ（pos）に置く
PLACE = {
    "gonbe": {"scale": 0.345, "pos": (317, 537), "src_bbox": (153, 192, 860, 1375)},
    "johndoe": {"scale": 0.445, "pos": (572, 499), "src_bbox": (228, 259, 901, 1343)},
}
KV_SCALE = W / 1024
KV_PAD = (H - round(1536 * KV_SCALE)) // 2


def room():
    im = Image.open(os.path.join(ROOT, "assets/backgrounds/room_base_source.png")).convert("RGB")
    fit = im.resize((W, round(im.height * KV_SCALE)), Image.LANCZOS)
    pad = (H - fit.height) // 2
    c = Image.new("RGB", (W, H))
    c.paste(fit.crop((0, 0, W, 8)).resize((W, pad)).filter(ImageFilter.GaussianBlur(10)), (0, 0))
    c.paste(fit, (0, pad))
    c.paste(fit.crop((0, fit.height - 8, W, fit.height)).resize((W, H - pad - fit.height)).filter(ImageFilter.GaussianBlur(10)),
            (0, pad + fit.height))
    return c.convert("RGBA")


def to_screen(name, sx, sy):
    p = PLACE[name]
    x0, y0 = p["src_bbox"][:2]
    kx = p["pos"][0] + (sx - x0) * p["scale"]
    ky = p["pos"][1] + (sy - y0) * p["scale"]
    return kx * KV_SCALE, ky * KV_SCALE + KV_PAD


def place(canvas, img, name, extra_scale=(1.0, 1.0), anchor_src=None, offset=(0, 0), rot=0.0, pivot_src=None):
    """元の絵（キャンバス）の画像を、画面上の正しい位置・大きさで貼る。"""
    p = PLACE[name]
    s = p["scale"] * KV_SCALE
    if rot and pivot_src:
        img = img.rotate(rot, center=pivot_src, resample=Image.BICUBIC)
    sx, sy = s * extra_scale[0], s * extra_scale[1]
    w, h = max(1, int(img.width * sx)), max(1, int(img.height * sy))
    small = img.resize((w, h), Image.LANCZOS)
    ax, ay = anchor_src if anchor_src else (0, 0)
    tx, ty = to_screen(name, ax, ay)
    x = tx - ax * sx + offset[0] * s
    y = ty - ay * sy + offset[1] * s
    canvas.alpha_composite(small, (int(round(x)), int(round(y))))


def fx(draw, kind, x, y, t):
    ink = (31, 21, 15, 255)
    cream = (240, 228, 204, 255)
    if kind == "dots":
        n = min(3, int(t * 6))
        for i in range(n):
            draw.ellipse((x + i * 34 - 10, y - 10, x + i * 34 + 10, y + 10), fill=cream, outline=ink, width=4)
    elif kind == "question":
        f = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc", 90, index=0)
        draw.text((x, y), "？", font=f, fill=cream, stroke_width=6, stroke_fill=ink, anchor="mm")
    elif kind == "sweat":
        draw.polygon([(x, y - 30), (x - 16, y + 6), (x + 16, y + 6)], fill=(170, 210, 235, 255))
        draw.ellipse((x - 16, y - 10, x + 16, y + 22), fill=(170, 210, 235, 255), outline=ink, width=4)
    elif kind == "sparkle":
        for i, (dx, dy) in enumerate([(0, 0), (70, 40), (-50, 60)]):
            r = 22 + 8 * math.sin(t * 12 + i)
            cx, cy = x + dx, y + dy
            draw.polygon([(cx, cy - r), (cx + r * 0.3, cy - r * 0.3), (cx + r, cy), (cx + r * 0.3, cy + r * 0.3),
                          (cx, cy + r), (cx - r * 0.3, cy + r * 0.3), (cx - r, cy), (cx - r * 0.3, cy - r * 0.3)],
                         fill=(240, 210, 120, 255), outline=ink)
    elif kind == "gloom":
        for i in range(5):
            xx = x - 120 + i * 60
            draw.line((xx, y, xx, y + 120 + (i % 2) * 30), fill=(90, 90, 140, 200), width=6)
    elif kind == "shock":
        for i in range(8):
            a = i * math.pi / 4
            draw.line((x + 120 * math.cos(a), y + 120 * math.sin(a), x + 170 * math.cos(a), y + 170 * math.sin(a)),
                      fill=cream, width=8)


def main(out):
    J = os.path.join(ROOT, "assets/characters/johndoe")
    rig = json.load(open(os.path.join(J, "rig.json")))
    head = Image.open(os.path.join(J, "parts/head.png"))
    body = Image.open(os.path.join(J, "parts/body.png"))
    gonbe = Image.open(os.path.join(ROOT, "assets/characters/gonbe/sit_source.png")).convert("RGBA")
    pivot = tuple(rig["layers"][1]["pivot"])
    hb = rig["head_bbox"]
    feet = (pivot[0], 1343)
    bg = room()
    bg.alpha_composite(Image.new("RGBA", bg.size, (0, 0, 0, 0)))
    place(bg, gonbe, "gonbe")
    font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc", 64, index=0)
    names = list(REACTIONS)
    n = int(len(names) * SEG * FPS)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", out],
                          stdin=subprocess.PIPE)
    for i in range(n):
        t_all = i / FPS
        name = names[int(t_all // SEG)]
        t = t_all % SEG
        p = pose(name, t)
        fr = bg.copy()
        # 体：足元を中心に伸び縮み
        place(fr, body, "johndoe", (p["body_sx"], p["body_sy"]), anchor_src=feet, offset=(p["body_dx"], p["body_dy"]))
        # 頭：首を中心に回転・拡大。体の伸び縮みと一緒に上下する
        hs = p["head_s"]
        neck_shift = (pivot[1] - feet[1]) * (p["body_sy"] - 1)
        place(fr, head, "johndoe", (p["body_sx"] * hs, p["body_sy"] * hs), anchor_src=pivot,
              offset=(p["body_dx"] + p["head_dx"], p["body_dy"] + p["head_dy"] + neck_shift), rot=p["head_rot"],
              pivot_src=pivot)
        d = ImageDraw.Draw(fr)
        if p["fx"]:
            hx, hy = to_screen("johndoe", (hb[0] + hb[2]) / 2, hb[1])
            fx(d, p["fx"], hx + 150, hy + 10, t)
        d.text((W / 2, 260), REACTIONS[name], font=font, fill=(240, 228, 204, 255), stroke_width=7,
               stroke_fill=(31, 21, 15, 255), anchor="mm")
        ff.stdin.write(fr.convert("RGB").tobytes())
    ff.stdin.close()
    ff.wait()
    print("書き出し完了:", out)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "output/johndoe_reactions.mp4")
