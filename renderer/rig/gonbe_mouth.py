"""ごんべぇの口パク用の口（閉・半開・開）を、顔の骨格に合わせて描く。

画像生成AIの「口を開けた絵」は、鼻の下の線（上あご）の位置がずれて顔の形が崩れるため使わない。
ここでは基本の絵（sit_source.png）の口の線をそのまま上あごとして使い、
その下に口の中・舌・下あごを描き足す。どの口も基本の絵と同じキャンバス・同じ位置の透過PNG。

使い方：
    python3 renderer/rig/gonbe_mouth.py
出力：
    assets/characters/gonbe/parts/mouth_half.png  … 基本の絵に重ねると半開きになる
    assets/characters/gonbe/parts/mouth_open.png  … 同じく大きく開いた口
    assets/characters/gonbe/_preview/mouths.png   … 確認用（閉・半開・開を並べたもの）
（閉じた口は基本の絵そのまま）
"""
from __future__ import annotations

import math
import os

from PIL import Image, ImageDraw

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BASE = os.path.join(ROOT, "assets/characters/gonbe/sit_source.png")
PARTS = os.path.join(ROOT, "assets/characters/gonbe/parts")
PREVIEW = os.path.join(ROOT, "assets/characters/gonbe/_preview")

INK = (20, 12, 8, 255)
FUR = (156, 82, 22, 255)        # 顔の毛（基本の絵から取った色）
MOUTH_IN = (52, 22, 16, 255)    # 口の中
TONGUE = (214, 108, 104, 255)   # 舌

# 基本の絵の「口の線」（上あご）。左端のくぼみ → 右の鼻の下のラインへつながる
UPPER = [(626, 642), (634, 636), (645, 630), (660, 627), (680, 628), (700, 632), (720, 635), (740, 635), (754, 633)]
LINE = 7   # 線の太さ（基本の絵に合わせる）
K = 4      # 4倍で描いて縮小（線をなめらかに）


def _catmull(pts, n=80):
    """点の列をなめらかな曲線にする（Catmull-Rom）。"""
    P = [pts[0]] + list(pts) + [pts[-1]]
    out = []
    seg = len(pts) - 1
    for i in range(seg):
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        for j in range(n // seg):
            u = j / (n // seg)
            out.append(tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * u + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u * u
                                     + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u ** 3) for k in (0, 1)))
    out.append(pts[-1])
    return out


def mouth(depth: float, tongue: bool) -> Image.Image:
    base = Image.open(BASE)
    W, H = base.size
    img = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = lambda pts: [(x * K, y * K) for x, y in pts]
    up = _catmull(UPPER)
    n = len(up)
    # 下唇：両端（口角）は上唇とつながり、少し右寄りがいちばん深い
    f = lambda t: math.sin(math.pi * t ** 0.85)
    low = [(x, y + depth * f(i / (n - 1))) for i, (x, y) in enumerate(up)]
    # 下あごの外側：下唇の少し下を、口角ではゼロになるようにまるく
    jaw = [(x, y + 20 * math.sin(math.pi * (i / (n - 1)) ** 0.85) ** 0.7) for i, (x, y) in enumerate(low)]
    d.polygon(s(low + jaw[::-1]), fill=FUR)
    d.polygon(s(up + low[::-1]), fill=MOUTH_IN)
    if tongue:
        cx = up[int(n * 0.55)][0]
        cy = low[int(n * 0.55)][1] - depth * 0.15
        rx, ry = depth * 1.0, depth * 0.38
        tg = Image.new("RGBA", img.size, (0, 0, 0, 0))
        ImageDraw.Draw(tg).ellipse(((cx - rx) * K, (cy - ry) * K, (cx + rx) * K, (cy + ry) * K), fill=TONGUE)
        clip = Image.new("L", img.size, 0)
        ImageDraw.Draw(clip).polygon(s(up + low[::-1]), fill=255)
        img.paste(tg, (0, 0), Image.composite(tg.getchannel("A"), Image.new("L", img.size, 0), clip))
    for line in (up, low, jaw):
        d.line(s(line), fill=INK, width=LINE * K, joint="curve")
    for x, y in (up[0], up[-1]):
        d.ellipse(((x - LINE / 2) * K, (y - LINE / 2) * K, (x + LINE / 2) * K, (y + LINE / 2) * K), fill=INK)
    return img.resize((W, H), Image.LANCZOS)


def main():
    os.makedirs(PARTS, exist_ok=True)
    os.makedirs(PREVIEW, exist_ok=True)
    half = mouth(24, tongue=False)
    opn = mouth(50, tongue=True)
    half.save(os.path.join(PARTS, "mouth_half.png"))
    opn.save(os.path.join(PARTS, "mouth_open.png"))
    base = Image.open(BASE).convert("RGBA")
    tiles = []
    for ov in (None, half, opn):
        t = Image.new("RGBA", base.size, (90, 140, 90, 255))
        t.alpha_composite(base)
        if ov is not None:
            t.alpha_composite(ov)
        tiles.append(t.crop((480, 420, 840, 760)))
    w, h = tiles[0].size
    sheet = Image.new("RGB", (w * 3, h))
    for i, t in enumerate(tiles):
        sheet.paste(t.convert("RGB"), (i * w, 0))
    sheet.save(os.path.join(PREVIEW, "mouths.png"))
    print("書き出し完了: parts/mouth_half.png, parts/mouth_open.png, _preview/mouths.png")


if __name__ == "__main__":
    main()
