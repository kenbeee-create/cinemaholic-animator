"""生成AIで作った表情違いの絵から、変わった部分（口・目など）だけを切り出して、
基本の絵に重ねる透過パーツにする。

- 基本の絵と比べて色が変わった所だけを使う（顔の形・ほかの部分は基本の絵のまま）
- 生成AIの絵は色が少し濃くなるので、まわりの毛の色を基本の絵にそろえる
- 背景が市松模様・黒でも、切り出す範囲は顔の中だけなので影響しない

使い方：
    python3 renderer/rig/extract_patch.py <基本の絵> <表情違いの絵> <出力> <範囲 x0,y0,x1,y1> [ずれ dx,dy]
"""
from __future__ import annotations

import sys

import numpy as np
from PIL import Image, ImageFilter


def extract(base_path, var_path, out_path, box, shift=(0, 0), thresh=38, grow=7, feather=3):
    base = Image.open(base_path).convert("RGBA")
    var = Image.open(var_path).convert("RGB")
    W, H = base.size
    if var.size != base.size or shift != (0, 0):
        canvas = Image.new("RGB", base.size)
        canvas.paste(var, (-shift[0], -shift[1]))
        var = canvas
    b = np.array(base).astype(float)
    v = np.array(var).astype(float)
    x0, y0, x1, y1 = box
    region = np.zeros((H, W), bool)
    region[y0:y1, x0:x1] = True
    region &= b[..., 3] > 200

    # 色合わせ：変わっていない毛の部分で、チャンネルごとの比率を求める
    diff = np.abs(b[..., :3] - v).sum(axis=2)
    same = region & (diff < 60) & (b[..., :3].sum(axis=2) > 150)
    gain = (b[..., :3][same].mean(axis=0) + 1) / (v[same].mean(axis=0) + 1)
    vc = np.clip(v * gain, 0, 255)

    # 変わった所＝マスク（少し広げて、ふちをぼかす）
    diff = np.abs(b[..., :3] - vc).sum(axis=2)
    m = (region & (diff > thresh)).astype(np.uint8) * 255
    mask = Image.fromarray(m).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))  # 小さな点を消す
    mask = mask.filter(ImageFilter.MaxFilter(grow * 2 + 1)).filter(ImageFilter.GaussianBlur(feather))
    reg = Image.fromarray((region * 255).astype(np.uint8))
    mask = Image.fromarray(np.minimum(np.array(mask), np.array(reg)))

    out = Image.fromarray(vc.astype(np.uint8)).convert("RGBA")
    out.putalpha(mask)
    out.save(out_path)
    return gain


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(__doc__)
        sys.exit(1)
    box = tuple(int(v) for v in sys.argv[4].split(","))
    shift = tuple(int(v) for v in sys.argv[5].split(",")) if len(sys.argv) > 5 else (0, 0)
    g = extract(sys.argv[1], sys.argv[2], sys.argv[3], box, shift)
    print("色合わせ", np.round(g, 3))
