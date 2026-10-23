"""ChatGPTで作った「部品シート」（無地のマゼンタ背景に部品を格子状に並べた1枚）を、1個ずつの透過PNGに切り分けて仕上げる。

AIっぽさを消すための仕上げ（docs/style-bible.md）：
  1. 背景（マゼンタ）を抜く・小さなゴミを消す
  2. 色を少ない数の平らな塗りにまとめる（グラデーション・ぼんやりした光を消す）
  3. その色を、シネマホリックの色（assets/style/palette.json）に少し寄せる
  4. 外側の輪郭線を、キャラと同じこげ茶の太さにそろえる

使い方：
    python3 scripts/slice_sheet.py <シート画像> fx                          … 記号シート（⑧）。名前は決まった順
    python3 scripts/slice_sheet.py <シート画像> props <名前1> <名前2> …     … 小物シート（⑨）。左上から右へ、行ごとに
        名前は「ファイル名:表示名」で書ける（例：vhs:ビデオテープ）。省略すると prop_01 …
オプション：
    --colors 8      … 1個あたりの色の数（少ないほど平ら。既定8）
    --snap 0.5      … シネマホリックの色に寄せる強さ（0〜1）
    --line 0        … 輪郭線を足さない
出力：assets/fx/<名前>.png（記号）、assets/props/<名前>.png と assets/props/index.json（小物）
確認用に、切り分けた結果の一覧を <出力先>/_last_sheet.jpg に書き出す。
"""
from __future__ import annotations

import argparse
import json
import os

import cv2
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FX_ORDER = [("sweat", "汗"), ("anger", "怒りマーク"), ("gaan", "ガーン（縦線）"),
            ("gloom", "どんより"), ("note", "音符"), ("sparkle", "キラキラ"),
            ("exclaim", "！"), ("question", "？"), ("steam", "ため息の煙")]
INK = np.array([31, 21, 15])


def palette():
    p = os.path.join(ROOT, "assets/style/palette.json")
    return np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in json.load(open(p))["colors"]], np.float32)


def remove_bg(rgb):
    """マゼンタ（と、その近くの色）を背景として抜く。四隅の色を背景色とみなす。"""
    h, w, _ = rgb.shape
    corners = np.concatenate([rgb[:8, :8].reshape(-1, 3), rgb[:8, -8:].reshape(-1, 3),
                              rgb[-8:, :8].reshape(-1, 3), rgb[-8:, -8:].reshape(-1, 3)]).astype(np.float32)
    bg = np.median(corners, 0)
    d = np.linalg.norm(rgb.astype(np.float32) - bg, axis=2)
    alpha = np.clip((d - 60) / 50, 0, 1)
    # マゼンタのにじみ（ふちのピンク）を消す
    r, g, b = [rgb[..., i].astype(int) for i in range(3)]
    fringe = (r > 150) & (b > 150) & (g < 120) & (alpha < 1)
    alpha[fringe] = 0
    return (alpha * 255).astype(np.uint8)


def blobs(alpha, min_area):
    """部品ごとのかたまりを見つける（近くの小さな部分＝汗のしずくの点など は同じ部品にまとめる）。"""
    m = (alpha > 128).astype(np.uint8)
    k = max(9, int(min(alpha.shape) * 0.02))
    merged = cv2.dilate(m, np.ones((k, k), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(merged, 8)
    boxes = [tuple(st[i, :4]) for i in range(1, n) if st[i, cv2.CC_STAT_AREA] >= min_area]
    # 行ごと → 左から右 の順に並べる
    if not boxes:
        return []
    hs = np.median([b[3] for b in boxes])
    boxes.sort(key=lambda b: (round((b[1] + b[3] / 2) / (hs * 0.8)), b[0]))
    return boxes


def flatten(rgb, a, n_colors, pal, snap):
    """色をn色の平らな塗りにして、シネマホリックの色に寄せる。"""
    on = a > 128
    px = rgb[on].astype(np.float32)
    if len(px) < n_colors * 4:
        return rgb
    crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 25, 1.0)
    _, lab, cen = cv2.kmeans(px, n_colors, None, crit, 2, cv2.KMEANS_PP_CENTERS)
    if snap > 0:
        # Lab色空間で一番近い色に、snap の強さで寄せる。ただし黒っぽい色（線）はインクの色にする
        to_lab = lambda c: cv2.cvtColor(c.reshape(1, -1, 3).astype(np.uint8), cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)
        cl, pl = to_lab(cen), to_lab(pal)
        near = pal[np.argmin(((cl[:, None] - pl[None]) ** 2).sum(2), 1)]
        cen = cen * (1 - snap) + near * snap
        dark = cen.sum(1) < 140
        cen[dark] = INK
    out = rgb.copy()
    out[on] = cen[lab.ravel()].astype(np.uint8)
    # 1〜2pxの色のちらつきを消す
    out = cv2.medianBlur(out, 3)
    return out


def outline(rgba, width):
    """外側の輪郭線をインクの色で一定の太さにそろえる。"""
    a = rgba[..., 3]
    m = (a > 128).astype(np.uint8)
    ring = cv2.dilate(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * width + 1, 2 * width + 1))) - m
    out = rgba.copy()
    out[ring > 0, :3] = INK
    out[ring > 0, 3] = 255
    # 角をなめらかに
    out[..., 3] = cv2.GaussianBlur(np.maximum(out[..., 3], 0), (3, 3), 0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sheet")
    ap.add_argument("kind", choices=["fx", "props"])
    ap.add_argument("names", nargs="*")
    ap.add_argument("--colors", type=int, default=8)
    ap.add_argument("--snap", type=float, default=0.5)
    ap.add_argument("--line", type=float, default=1.0, help="輪郭線の太さの倍率（0で足さない）")
    args = ap.parse_args()

    rgb = np.array(Image.open(args.sheet).convert("RGB"))
    alpha = remove_bg(rgb)
    boxes = blobs(alpha, min_area=int(rgb.shape[0] * rgb.shape[1] * 0.002))
    out_dir = os.path.join(ROOT, "assets", args.kind)
    os.makedirs(out_dir, exist_ok=True)
    if args.kind == "fx":
        names = FX_ORDER
    else:
        names = []
        for i in range(len(boxes)):
            if i < len(args.names):
                f, _, lab = args.names[i].partition(":")
                names.append((f, lab or f))
            else:
                names.append((f"prop_{i + 1:02d}", f"小物{i + 1}"))
    if len(boxes) != len(names):
        print(f"注意：見つかった部品は {len(boxes)} 個、名前は {len(names)} 個。多い分は捨て、足りない分は作りません")
    pal = palette()
    saved = []
    for (x, y, w, h), (name, label) in zip(boxes, names):
        pad = 24
        x0, y0 = max(0, x - pad), max(0, y - pad)
        x1, y1 = min(rgb.shape[1], x + w + pad), min(rgb.shape[0], y + h + pad)
        c_rgb, c_a = rgb[y0:y1, x0:x1].copy(), alpha[y0:y1, x0:x1].copy()
        # この部品のかたまりだけ残す（隣の部品のはみ出しを消す）
        n, lab, st, _ = cv2.connectedComponentsWithStats((c_a > 128).astype(np.uint8), 8)
        if n > 1:
            keep = st[1:, cv2.CC_STAT_AREA] >= max(30, st[1:, cv2.CC_STAT_AREA].max() * 0.01)
            c_a = np.where(np.isin(lab, np.where(keep)[0] + 1), c_a, 0).astype(np.uint8)
        flat = flatten(c_rgb, c_a, args.colors, pal, args.snap)
        rgba = np.dstack([flat, np.where(c_a > 128, 255, 0).astype(np.uint8)])
        if args.line > 0:
            lw = max(3, int(round(max(w, h) * 0.014 * args.line)))
            rgba = np.pad(rgba, ((lw + 2, lw + 2), (lw + 2, lw + 2), (0, 0)))
            rgba = outline(rgba, lw)
        im = Image.fromarray(rgba)
        im = im.crop(im.getchannel("A").getbbox())
        p = os.path.join(out_dir, name + ".png")
        im.save(p)
        saved.append((name, label, im))
        print("保存:", os.path.relpath(p, ROOT), im.size)

    if args.kind == "props":
        idx_p = os.path.join(out_dir, "index.json")
        idx = json.load(open(idx_p, encoding="utf-8")) if os.path.exists(idx_p) else {"items": []}
        have = {i["file"]: i for i in idx["items"]}
        for name, label, _ in saved:
            have[f"props/{name}.png"] = {"file": f"props/{name}.png", "label": label}
        idx["items"] = sorted(have.values(), key=lambda i: i["file"])
        json.dump(idx, open(idx_p, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # 確認用の一覧
    if saved:
        cell = 260
        sheet = Image.new("RGB", (cell * min(5, len(saved)), cell * ((len(saved) + 4) // 5)), (60, 46, 34))
        for i, (_, _, im) in enumerate(saved):
            t = im.copy()
            t.thumbnail((cell - 20, cell - 20))
            sheet.paste(t, ((i % 5) * cell + (cell - t.width) // 2, (i // 5) * cell + (cell - t.height) // 2), t)
        sheet.save(os.path.join(out_dir, "_last_sheet.jpg"))


if __name__ == "__main__":
    main()
