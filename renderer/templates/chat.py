"""冒頭のトーク画面（Scene1）を、メッセージのJSONから書き出すテンプレート。

ごんべぇのスマホ（アニメの絵柄で描いたスマホ）に、じょんどぅーとのトーク画面が映る。
スマホの後ろには、その回の部屋をぼかして暗くした絵が入る（回ごとに最初の1枚が変わる）。

使い方：
    python3 renderer/templates/chat.py <chat.json> <出力フォルダ>

出力：
    chat.mp4        … 動くトーク画面（音なし、1080x1920・30fps）
    chat_last.png   … 最後のコマ（確認用）
    chat_first.png  … 最初のメッセージが出たコマ（フィードで最初に見える絵の確認用）
    cues.json       … 効果音を鳴らすタイミング（sound-designer 用）

メッセージを変えたいときは JSON の "messages" を書き換えて、もう一度実行するだけ。
JSON の書き方は renderer/templates/README.md。
"""
from __future__ import annotations

import json
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
import style as S  # noqa: E402
from style import C, SS, W, H  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

CHARS = {
    "gonbe": {"name": "ごんべぇ", "icon": "assets/ui/avatars/gonbe_icon.png", "icon_bg": (122, 116, 94)},
    "johndoe": {"name": "じょんどぅー", "icon": "assets/ui/avatars/johndoe_icon.png", "icon_bg": (196, 150, 84)},
}

# スマホ本体（右はSNSのボタン列を避けて少し左寄せ）
PHONE = (64, 150, 896, 1760)
PHONE_R = 96
BEZEL = 24
CASE = C["denim"]

# スマホ画面の中
HEADER_H = 140
FONT_SIZE = 50
BUBBLE_MAX_W = 590
PAD_X, PAD_Y = 34, 20
GAP = 24
ICON = 84
POP = 0.22  # 吹き出しが出る時間（秒）


def screen_box():
    x0, y0, x1, y1 = PHONE
    return (x0 + BEZEL, y0 + BEZEL, x1 - BEZEL, y1 - BEZEL)


def _bubble(text: str, who: str, mine: bool) -> Image.Image:
    """吹き出し1つ（しっぽ付き・輪郭線1本）を透過PNGで作る。2倍で描いて縮小。"""
    k = SS
    fnt = S.font("ui_bold", FONT_SIZE * k)
    lines = S.balance_lines(S.wrap_text(text, fnt, BUBBLE_MAX_W * k), fnt, BUBBLE_MAX_W * k)
    asc, desc = fnt.getmetrics()
    lh = int((asc + desc) * 1.06)
    tw = max(int(fnt.getlength(l)) for l in lines)
    bw = tw + PAD_X * 2 * k
    bh = lh * len(lines) + PAD_Y * 2 * k - int(desc * 0.4)
    lw = S.LINE_W * k
    tail = 20 * k
    m = lw * 2 + 8 * k
    size = (bw + tail + m * 2, bh + m * 2)
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    x0 = m if mine else m + tail
    box = (x0, m, x0 + bw, m + bh)
    r = min(40 * k, bh // 2)
    d.rounded_rectangle(box, r, fill=255)
    if mine:  # 右上にしっぽ
        d.polygon([(box[2] - r * 0.9, box[1]), (box[2] + tail, box[1] + 4 * k), (box[2] - 2 * k, box[1] + r * 0.9)], fill=255)
    else:     # 左上にしっぽ
        d.polygon([(box[0] + r * 0.9, box[1]), (box[0] - tail, box[1] + 4 * k), (box[0] + 2 * k, box[1] + r * 0.9)], fill=255)
    col = S.SPEAKER[who]
    img = S.outlined_shape(mask, col["fill"], lw, shadow=(0, 6 * k), shadow_alpha=150)
    td = ImageDraw.Draw(img)
    y = box[1] + PAD_Y * k
    for l in lines:
        td.text((box[0] + PAD_X * k, y), l, font=fnt, fill=col["text"] + (255,))
        y += lh
    img = img.resize((img.width // k, img.height // k), Image.LANCZOS)
    img.info["pad"] = m // k
    img.info["tail"] = tail // k
    return img


def _phone_layer(cfg) -> Image.Image:
    """背景（部屋）＋スマホ本体＋画面の動かない部分。"""
    bg_path = cfg.get("background")
    if bg_path and not os.path.isabs(bg_path):
        bg_path = os.path.join(ROOT, bg_path)
    img = S.room_background(bg_path).convert("RGBA")
    k = SS
    # スマホ本体（輪郭線つき）
    big = Image.new("L", (W * k, H * k), 0)
    ImageDraw.Draw(big).rounded_rectangle([v * k for v in PHONE], PHONE_R * k, fill=255)
    body = S.outlined_shape(big, CASE, (S.LINE_W + 2) * k, shadow=(16 * k, 22 * k), shadow_alpha=170)
    img.alpha_composite(body.resize((W, H), Image.LANCZOS))
    d = ImageDraw.Draw(img)
    sx0, sy0, sx1, sy1 = screen_box()
    # 画面
    scr = S.night_background(vignette=0.25).crop((sx0, sy0, sx1, sy1)).convert("RGBA")
    smask = Image.new("L", scr.size, 0)
    ImageDraw.Draw(smask).rounded_rectangle((0, 0, scr.width - 1, scr.height - 1), PHONE_R - BEZEL, fill=255)
    img.paste(scr, (sx0, sy0), smask)
    d.rounded_rectangle((sx0, sy0, sx1, sy1), PHONE_R - BEZEL, outline=C["ink"] + (255,), width=4)
    # 画面上部のカメラ穴
    cx = (sx0 + sx1) // 2
    d.rounded_rectangle((cx - 70, sy0 + 22, cx + 70, sy0 + 58), 18, fill=C["ink"] + (255,))
    # ヘッダー（相手の名前）
    hy0, hy1 = sy0 + 80, sy0 + 80 + HEADER_H
    d.rectangle((sx0 + 4, hy0, sx1 - 4, hy1), fill=C["night_2"] + (255,))
    d.line((sx0 + 4, hy1, sx1 - 4, hy1), fill=C["ink"] + (255,), width=S.LINE_W)
    cy = (hy0 + hy1) // 2
    d.line([(sx0 + 58, cy - 24), (sx0 + 36, cy), (sx0 + 58, cy + 24)], fill=C["cream"] + (255,), width=8, joint="curve")
    partner = CHARS[cfg["partner"]]
    icon = S.circle_icon(os.path.join(ROOT, partner["icon"]), ICON, bg=partner["icon_bg"])
    img.alpha_composite(icon, (sx0 + 84, cy - ICON // 2))
    d.text((sx0 + 84 + ICON + 22, cy), cfg.get("partner_name", partner["name"]), font=S.font("ui_bold", 46),
           fill=C["cream"] + (255,), anchor="lm")
    # 日付ラベル
    label = cfg.get("day_label", "")
    if label:
        f = S.font("ui_bold", 30)
        tw = f.getlength(label)
        mx = (sx0 + sx1) / 2
        y0 = hy1 + 36
        d.rounded_rectangle((mx - tw / 2 - 28, y0, mx + tw / 2 + 28, y0 + 52), 26, fill=C["night_3"] + (255,))
        d.text((mx, y0 + 26), label, font=f, fill=C["cream_dim"] + (255,), anchor="mm")
    # 入力欄
    iy = sy1 - 150
    d.line((sx0 + 4, iy - 24, sx1 - 4, iy - 24), fill=C["night_3"] + (255,), width=3)
    d.rounded_rectangle((sx0 + 36, iy, sx1 - 36, iy + 84), 42, fill=C["night_2"] + (255,),
                        outline=C["ink"] + (255,), width=S.LINE_W)
    d.text((sx0 + 76, iy + 42), "メッセージを入力", font=S.font("ui", 32), fill=C["cream_dim"] + (255,), anchor="lm")
    return img


def _timings(cfg):
    t, out = cfg.get("start", 0.25), []
    for m in cfg["messages"]:
        at = m.get("at", t)
        out.append(at)
        t = at + cfg.get("interval", 0.6)
    return out


def render(cfg_path: str, out_dir: str):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    owner = cfg.get("owner", "gonbe")
    cfg.setdefault("partner", "johndoe" if owner == "gonbe" else "gonbe")
    times = _timings(cfg)
    read_at = cfg.get("read_at", times[-1] + 0.45)
    duration = cfg.get("duration", max(3.0, read_at + 0.6))
    clock = cfg.get("time", "19:42")

    base = _phone_layer(cfg)
    sx0, sy0, sx1, sy1 = screen_box()
    area_top = sy0 + 80 + HEADER_H + 110
    area_bottom = sy1 - 200
    x_left, x_right = sx0 + 26, sx1 - 22
    small = S.font("ui", 26)

    bubbles = []
    for m in cfg["messages"]:
        who = m.get("from", owner)
        bubbles.append({"img": _bubble(m["text"], who, who == owner), "mine": who == owner})
    p_icon = CHARS[cfg["partner"]]
    icon_s = S.circle_icon(os.path.join(ROOT, p_icon["icon"]), 70, bg=p_icon["icon_bg"])

    def frame(t: float) -> Image.Image:
        img = base.copy()
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        y = area_bottom
        shown = [i for i in range(len(bubbles)) if S.progress(t, times[i], POP) > 0]
        placed = []
        for i in reversed(shown):
            p = S.progress(t, times[i], POP)
            b = bubbles[i]["img"]
            pad = b.info["pad"]
            y -= (b.height - pad * 2) * S.ease_out_cubic(p) + GAP
            placed.append((i, y - pad, p))
        last_mine = max([i for i in shown if bubbles[i]["mine"]], default=None)
        for i, top, p in placed:
            b = bubbles[i]
            im = b["img"]
            pad = im.info["pad"]
            sc = 0.55 + 0.45 * S.ease_out_back(p)
            alpha = S.clamp(p * 3)
            if b["mine"]:
                right = x_right + pad
                S.paste_scaled(layer, im, (right, top), sc, origin=(1.0, 0.0), alpha=alpha)
                if i == last_mine and p >= 1:
                    tx = right - im.width + pad - 10
                    by = top + im.height - pad - 4
                    d.text((tx, by), clock, font=small, fill=C["cream_dim"] + (255,), anchor="rd")
                    if t >= read_at:
                        a = int(255 * S.progress(t, read_at, 0.15))
                        d.text((tx, by - 32), "既読", font=small, fill=C["cream_dim"] + (a,), anchor="rd")
            else:
                layer.alpha_composite(icon_s, (x_left, int(top + pad)))
                S.paste_scaled(layer, im, (x_left + 70 + 4 - pad, top), sc, origin=(0.0, 0.0), alpha=alpha)
        # 画面の外にはみ出さないように切り抜く
        clip = Image.new("L", img.size, 0)
        ImageDraw.Draw(clip).rectangle((sx0, sy0 + 80 + HEADER_H + 4, sx1, sy1 - 180), fill=255)
        from PIL import ImageChops
        layer.putalpha(ImageChops.multiply(layer.getchannel("A"), clip))
        img.alpha_composite(layer)
        return img

    n = int(round(duration * S.FPS))
    S.save_video((frame(i / S.FPS) for i in range(n)), os.path.join(out_dir, "chat.mp4"))
    frame(duration).convert("RGB").save(os.path.join(out_dir, "chat_last.png"))
    frame(times[0] + POP).convert("RGB").save(os.path.join(out_dir, "chat_first.png"))
    cues = [{"t": round(times[i], 3), "sfx": "brand/chat_send" if bubbles[i]["mine"] else "brand/chat_receive"}
            for i in range(len(times))]
    cues.append({"t": round(read_at, 3), "sfx": None, "note": "既読がつく"})
    json.dump({"duration": duration, "cues": cues}, open(os.path.join(out_dir, "cues.json"), "w"),
              ensure_ascii=False, indent=2)
    print(f"書き出し完了: {out_dir}（{duration:.1f}秒）")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    render(sys.argv[1], sys.argv[2])
