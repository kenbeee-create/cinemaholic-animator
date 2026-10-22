"""じょんどぅーのリグ（動かすための部品）を作る。

じょんどぅーは目が毛で隠れているので、表情は「目」ではなく「動き」で出す（docs/characters.md）。
そのために、頭（毛のかたまり）と体を別の部品に分け、口は3種類（閉・半開き・開き）を用意する。

使い方：
    python3 renderer/rig/johndoe_rig.py
入力：
    assets/characters/johndoe/sit_source.png                         … 座りポーズ（口が開いた状態）
    assets/characters/johndoe/expressions_source/mouth_closed_chatgpt.png … 口を閉じた絵（口まわりだけ使う）
出力：assets/characters/johndoe/
    base_closed.png      … 口を閉じた全身（確認用）
    parts/head.png       … 頭（毛・鼻・閉じた口）。体の上に重ねる
    parts/body.png       … 体（首の下は頭が動いても穴が開かないように埋めてある）
    parts/mouth_half.png / mouth_open.png … 頭に重ねる口
    rig.json             … 部品の重なり順と、頭を動かす中心（首）の位置
"""
from __future__ import annotations

import json
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from extract_patch import extract  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
J = os.path.join(ROOT, "assets/characters/johndoe")

INK = (30, 18, 10, 255)
MOUTH_RED = (178, 60, 44, 255)
MOUTH_DARK = (70, 24, 18, 255)


def keep_big(img: Image.Image, min_area: int = 2000) -> Image.Image:
    """小さなゴミ（生成AIの光の残りなど）を消して、大きなかたまりだけ残す。"""
    import cv2
    a = np.array(img)
    n, lab, stats, _ = cv2.connectedComponentsWithStats((a[..., 3] > 0).astype(np.uint8), 8)
    keep = np.zeros(n, bool)
    keep[1:] = stats[1:, cv2.CC_STAT_AREA] >= min_area
    a[..., 3] = np.where(keep[lab], a[..., 3], 0)
    return Image.fromarray(a)


def build():
    src = keep_big(Image.open(os.path.join(J, "sit_source.png")).convert("RGBA"))
    W, H = src.size
    os.makedirs(os.path.join(J, "parts"), exist_ok=True)
    tmp = os.path.join(J, "parts", "_closed_patch.png")

    # 1) 口を閉じた全身：赤い口を毛の色で埋め、閉じた口の線を描く
    import cv2
    s0 = np.array(src).astype(int)
    red0 = (s0[..., 0] > 150) & (s0[..., 1] < 90) & (s0[..., 2] < 80) & (s0[..., 3] > 200)
    ys0, xs0 = np.where(red0)
    mx0, my0 = (xs0.min() + xs0.max()) / 2, (ys0.min() + ys0.max()) / 2
    rx0, ry0 = (xs0.max() - xs0.min()) / 2, (ys0.max() - ys0.min()) / 2
    hole = np.zeros((H, W), np.uint8)
    cv2.ellipse(hole, (int(mx0), int(my0)), (int(rx0) + 10, int(ry0) + 10), 0, 0, 360, 255, -1)
    bgr = cv2.cvtColor(np.array(src)[..., :3], cv2.COLOR_RGB2BGR)
    fill = cv2.cvtColor(cv2.inpaint(bgr, hole, 15, cv2.INPAINT_TELEA), cv2.COLOR_BGR2RGB)
    arr = np.array(src)
    arr[..., :3] = np.where(hole[..., None] > 0, fill, arr[..., :3])
    closed = Image.fromarray(arr)
    K = 4
    ln = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
    ImageDraw.Draw(ln).line([((mx0 - rx0 * 0.55) * K, (my0 - ry0 * 0.15) * K), ((mx0 + rx0 * 0.55) * K, (my0 - ry0 * 0.15) * K)],
                            fill=INK, width=5 * K)
    closed.alpha_composite(ln.resize((W, H), Image.LANCZOS))
    closed.save(os.path.join(J, "base_closed.png"))

    # 2) 頭と体を分ける：列ごとに、上から見て最初にTシャツ（明るいクリーム色）が出てくる所より上が頭
    a = np.array(closed).astype(int)
    alpha = a[..., 3] > 200
    shirt = (a[..., :3].sum(axis=2) > 560) & alpha
    head = np.zeros((H, W), bool)
    neck_y = []
    for x in range(W):
        col = np.where(alpha[:, x])[0]
        if len(col) == 0:
            continue
        sh = np.where(shirt[:, x])[0]
        limit = sh[0] if len(sh) and sh[0] < 760 else 700
        if len(sh) and sh[0] < 760:
            neck_y.append(sh[0])
        head[:limit, x] = alpha[:limit, x]
    # 頭の毛のふちがギザギザにならないよう少し整える
    # 細い線（Tシャツの肩の輪郭）を落とす：太い所だけ残す
    hm = Image.fromarray((head * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(11)).filter(ImageFilter.MaxFilter(11))
    head_img = closed.copy()
    head_img.putalpha(Image.fromarray(np.minimum(np.array(hm), np.array(closed.getchannel("A")))))
    head_img = keep_big(head_img)
    head_img.save(os.path.join(J, "parts", "head.png"))

    # 体：頭の部分を消し、頭の下（首まわり）をTシャツと毛の色で埋める
    body = closed.copy()
    ba = np.array(body)
    ba[..., 3] = np.where(np.array(hm) > 0, 0, ba[..., 3])
    body = Image.fromarray(ba)
    d = ImageDraw.Draw(body)
    top = int(np.median(neck_y)) if neck_y else 690
    xs = np.where(shirt.any(axis=0))[0]
    sx0, sx1 = int(xs.min()) + 40, int(xs.max()) - 40
    cx = (sx0 + sx1) // 2
    d.rounded_rectangle((cx - 200, top - 50, cx + 200, top + 10), 24, fill=(236, 220, 186, 255))  # 毛の下に隠れていたTシャツ
    d.ellipse((cx - 160, top - 140, cx + 160, top + 15), fill=(52, 36, 22, 255))                   # 首（毛）
    body = keep_big(body)
    body.save(os.path.join(J, "parts", "body.png"))

    # 3) 口：閉じた口は頭に含まれる。半開き・開きは赤い楕円を重ねる
    s = np.array(src).astype(int)
    red_src = (s[..., 0] > 150) & (s[..., 1] < 90) & (s[..., 2] < 80) & (s[..., 3] > 200)
    ys, xs2 = np.where(red_src)
    mx, my = (xs2.min() + xs2.max()) / 2, (ys.min() + ys.max()) / 2
    rx, ry = (xs2.max() - xs2.min()) / 2, (ys.max() - ys.min()) / 2

    def mouth(scale_y, scale_x=1.0):
        K = 4
        img = Image.new("RGBA", (W * K, H * K), (0, 0, 0, 0))
        dd = ImageDraw.Draw(img)
        ex, ey = rx * scale_x, ry * scale_y
        cy = my - ry + ey  # 上の縁の高さはそろえる（下にだけ開く）
        lw = 6
        dd.ellipse(((mx - ex - lw) * K, (cy - ey - lw) * K, (mx + ex + lw) * K, (cy + ey + lw) * K), fill=INK)
        dd.ellipse(((mx - ex) * K, (cy - ey) * K, (mx + ex) * K, (cy + ey) * K), fill=MOUTH_RED)
        if scale_y > 0.6:  # 大きく開いたときだけ奥を暗く
            dd.ellipse(((mx - ex * 0.55) * K, (cy - ey * 0.6) * K, (mx + ex * 0.55) * K, (cy + ey * 0.1) * K), fill=MOUTH_DARK)
        return img.resize((W, H), Image.LANCZOS)

    mouth(0.45, 0.85).save(os.path.join(J, "parts", "mouth_half.png"))
    mouth(1.0).save(os.path.join(J, "parts", "mouth_open.png"))

    # 4) リグ情報
    hb = Image.fromarray((np.array(hm) > 0).astype(np.uint8) * 255).getbbox()
    rig = {
        "canvas": [W, H],
        "layers": [{"name": "body", "file": "parts/body.png", "z": 1},
                   {"name": "head", "file": "parts/head.png", "z": 2, "pivot": [cx, top]},
                   {"name": "mouth", "parent": "head", "z": 3,
                    "states": {"closed": None, "half": "parts/mouth_half.png", "open": "parts/mouth_open.png"}}],
        "head_bbox": list(hb),
        "note": "目は毛で隠れているので表情差分は持たない。リアクションは renderer/motion/reactions.py の動きで出す",
    }
    json.dump(rig, open(os.path.join(J, "rig.json"), "w"), ensure_ascii=False, indent=2)
    print("書き出し完了: base_closed.png, parts/head.png, parts/body.png, parts/mouth_*.png, rig.json")


if __name__ == "__main__":
    build()
