"""ごんべぇのリグ（頭と体を分けた部品）を作る。

頭と体が分かれていれば、うなずく・首をかしげる・乗り出す・ため息で沈む などをプログラムで動かせる。
目と口の部品（parts/eyes_*.png, parts/mouth_*.png）は元の絵と同じ位置に描いてあるので、頭と同じ動きで重ねればよい。

使い方：
    python3 renderer/rig/gonbe_rig.py
入力：assets/characters/gonbe/sit_source.png
出力：assets/characters/gonbe/
    parts/head.png  … 頭（帽子・耳・顔）。パーカーより上
    parts/body.png  … 体（頭が動いても首に穴が開かないよう、首まわりを毛の色で埋めてある）
    rig.json        … 頭を動かす中心（首）の位置
"""
from __future__ import annotations

import json
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
G = os.path.join(ROOT, "assets/characters/gonbe")
FUR = (154, 80, 21, 255)
INK = (3, 1, 0, 255)


def keep_big(m: Image.Image) -> Image.Image:
    """いちばん大きなかたまり（頭）だけ残す。"""
    import cv2
    a = (np.array(m) > 0).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(a, 8)
    if n <= 1:
        return m
    k = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    return Image.fromarray(((lab == k) * 255).astype(np.uint8))


def build():
    src = Image.open(os.path.join(G, "sit_source.png")).convert("RGBA")
    W, H = src.size
    a = np.array(src).astype(int)
    alpha = a[..., 3] > 128
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    parka = (r > 90) & (r > 2.8 * g) & (b < 60) & alpha

    # 列ごとに、上から見て最初にパーカーが出てくる所より上が頭（耳は顔の横に垂れているので頭に入る）
    head = np.zeros((H, W), bool)
    tops = []
    for x in range(W):
        if not alpha[:, x].any():
            continue
        pk = np.where(parka[150:900, x])[0]
        if len(pk) == 0:
            continue  # パーカーが無い列（しっぽなど）は体のまま
        lim = 150 + pk[0]
        tops.append((x, lim))
        head[:lim, x] = alpha[:lim, x]
    # 輪郭の黒い線は境目で上下に分かれるので、境目より2px下までは頭に含めて線を残す
    head[760:] = False  # 肩の輪郭線（細い線）が頭に入らないように
    hm = Image.fromarray((head * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(9)).filter(ImageFilter.MaxFilter(9))
    hm = keep_big(hm).filter(ImageFilter.MaxFilter(5))
    hm = Image.fromarray(np.minimum(np.array(hm), np.array(src.getchannel("A"))))

    head_img = src.copy()
    head_img.putalpha(hm)
    os.makedirs(os.path.join(G, "parts"), exist_ok=True)
    head_img.save(os.path.join(G, "parts", "head.png"))

    # 体：頭を消して、首まわり（頭の下）を毛の色で埋める
    body = src.copy()
    ba = np.array(body)
    ba[..., 3] = np.where(np.array(hm) > 0, 0, ba[..., 3])
    body = Image.fromarray(ba)
    xs = [x for x, _ in tops]
    # 首の位置：顔の真下あたり（パーカーの襟がいちばん高い所）
    mid = [(x, y) for x, y in tops if 420 < x < 760]
    neck_y = int(np.median([y for _, y in mid]))
    cx = int(np.mean([x for x, _ in mid]))
    under = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(under)
    d.ellipse((cx - 150, neck_y - 150, cx + 150, neck_y + 40), fill=FUR)
    # 頭が下がったり傾いたりしたときに、あごの下に穴が見えないよう、頭の下半分の形を毛の色で埋めておく
    fill = (np.array(hm) > 0)
    fill[:600] = False
    ua = np.array(under)
    ua[fill] = FUR
    under = Image.fromarray(ua)
    under.alpha_composite(body)
    under.save(os.path.join(G, "parts", "body.png"))

    hb = hm.getbbox()
    rig = {
        "canvas": [W, H],
        "layers": [{"name": "body", "file": "parts/body.png", "z": 1},
                   {"name": "head", "file": "parts/head.png", "z": 2, "pivot": [cx, neck_y]},
                   {"name": "eyes", "parent": "head", "z": 3}, {"name": "mouth", "parent": "head", "z": 3}],
        "head_bbox": list(hb),
        "note": "目と口の部品は元の絵と同じ位置。頭と同じ動きで重ねる。目はいつもの半目が基本（docs/characters.md）",
    }
    json.dump(rig, open(os.path.join(G, "rig.json"), "w"), ensure_ascii=False, indent=2)
    print("書き出し完了: parts/head.png, parts/body.png, rig.json  pivot=", (cx, neck_y), "head_bbox=", hb, "columns", min(xs), max(xs))


if __name__ == "__main__":
    build()
