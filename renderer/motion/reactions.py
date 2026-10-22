"""じょんどぅーのリアクション（動き）の型。

じょんどぅーは目が毛で隠れているので、気持ちは「頭と体の動き」で出す。
各リアクションは、経過時間 t（秒）を受け取り、頭と体をどう動かすかを返す。

返す値（すべて元の絵のピクセル単位・度）：
    body_dx, body_dy   体（全身）の移動
    body_sx, body_sy   体の伸び縮み（1.0 が元の大きさ。足元を中心に伸び縮み）
    head_dx, head_dy   頭だけの移動
    head_rot           頭の傾き（＋で左に傾く）
    head_s             頭の大きさ（毛が逆立つなど）
    fx                 一緒に出す記号（"dots"=…／"sweat"=汗／"sparkle"=キラキラ／"question"=？ など）
"""
from __future__ import annotations

import math

REACTIONS = {
    "idle":      "待機（ゆっくり呼吸）",
    "nod":       "うなずく",
    "tilt":      "首をかしげる",
    "shake":     "首を横に振る（ちがう）",
    "bounce":    "ノる・うれしい（小さく跳ねる）",
    "lean_in":   "乗り出して語る",
    "slump":     "しょんぼり",
    "puff":      "ゾワッ・驚き（毛が逆立つ）",
    "freeze":    "固まる（…）",
    "look_away": "そっぽを向く・照れ",
}


def _ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


def _bump(t, start, dur):
    """start から dur 秒で 0→1→0 になる山。"""
    if t < start or t > start + dur:
        return 0.0
    return math.sin(math.pi * (t - start) / dur)


def pose(name: str, t: float) -> dict:
    p = dict(body_dx=0.0, body_dy=0.0, body_sx=1.0, body_sy=1.0,
             head_dx=0.0, head_dy=0.0, head_rot=0.0, head_s=1.0, fx=None)
    # 待機の呼吸はいつも少しだけ入れる（固まる以外）
    if name != "freeze":
        br = math.sin(t * 2 * math.pi / 2.4)
        p["body_sy"] += 0.008 * br
        p["head_dy"] += -3 * br
    if name == "nod":
        p["head_dy"] += 22 * (_bump(t, 0.1, 0.35) + _bump(t, 0.5, 0.35))
        p["head_rot"] += -3 * (_bump(t, 0.1, 0.35) + _bump(t, 0.5, 0.35))
    elif name == "tilt":
        p["head_rot"] += 11 * _ease(t / 0.25)
        p["head_dx"] += -10 * _ease(t / 0.25)
        p["fx"] = "question" if t > 0.25 else None
    elif name == "shake":
        if t < 0.9:
            p["head_dx"] += 16 * math.sin(t * 2 * math.pi * 3.5) * (1 - t / 0.9)
            p["head_rot"] += 3 * math.sin(t * 2 * math.pi * 3.5) * (1 - t / 0.9)
    elif name == "bounce":
        for k in range(2):
            b = _bump(t, 0.05 + k * 0.4, 0.38)
            p["body_dy"] -= 34 * b
        squash = _bump(t, 0.0, 0.08) + _bump(t, 0.42, 0.08) + _bump(t, 0.82, 0.1)
        p["body_sy"] -= 0.06 * squash
        p["body_sx"] += 0.04 * squash
        p["fx"] = "sparkle"
    elif name == "lean_in":
        k = _ease(t / 0.3)
        p["body_sx"] += 0.04 * k
        p["body_sy"] += 0.04 * k
        p["body_dx"] -= 18 * k        # ごんべぇ（左）の方へ
        p["head_dx"] -= 14 * k
        p["head_rot"] += 4 * k
    elif name == "slump":
        k = _ease(t / 0.5)
        p["head_dy"] += 30 * k
        p["head_rot"] += -5 * k
        p["body_sy"] -= 0.035 * k
        p["fx"] = "gloom" if t > 0.4 else None
    elif name == "puff":
        k = _bump(t, 0.0, 0.25) * 1.0 + (0.6 if t >= 0.25 else 0) * max(0.0, 1 - (t - 0.25) / 0.6)
        p["head_s"] = 1 + 0.12 * k
        p["head_dy"] -= 12 * k
        p["body_dy"] -= 10 * _bump(t, 0.0, 0.2)
        p["fx"] = "shock" if t < 0.7 else None
    elif name == "freeze":
        p["fx"] = "dots" if t > 0.2 else None
    elif name == "look_away":
        k = _ease(t / 0.3)
        p["head_rot"] += -7 * k
        p["head_dx"] += 14 * k
        p["fx"] = "sweat" if t > 0.3 else None
    return p
