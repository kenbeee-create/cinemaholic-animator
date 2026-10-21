"""タイトル（Scene2）「〇〇な そこの君に、いい薬を処方します。／シネマホリック」を書き出すテンプレート。

使い方：
    python3 renderer/templates/title.py <title.json> <出力フォルダ>

出力：
    title.mp4       … 動くタイトル（音なし、1080x1920・30fps）
    title_last.png  … 最後のコマ（確認用）
    cues.json       … 錠剤音「カラン」と低音「ジャン」を鳴らすタイミング
    logo.png / pill.png … ロゴと錠剤アイコンの透過PNG（ほかの場面でも使う部品）

〇〇の部分は JSON の "worry" を書き換えるだけ。
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
CENTER_X = 480  # 右のボタン列を避けて、少し左寄せ

T_PILL = 0.10     # 錠剤が落ち始める
T_CLINK = 0.42    # 錠剤が着地（カラン）
T_SLAM = 0.80     # 悩みの文字がドン（ジャン）
T_REST = 1.05     # 残りの文字
T_LOGO = 1.30     # ロゴ


def text_block(text: str, kind: str, size: int, fill, stroke_w: int, max_w: int, shadow: int = 0,
               rim: int = 0) -> Image.Image:
    """輪郭線（＋ずらした影）つきの文字を透過PNGで作る。長いときは自動で縮める。
    rim を指定すると、輪郭線の外側にクリーム色のふちを足す（暗い背景で目立たせる）。"""
    k = SS
    while True:
        fnt = S.font(kind, size * k)
        if fnt.getlength(text) <= max_w * k or size <= 24:
            break
        size -= 2
    sw = stroke_w * k
    rw = (stroke_w + rim) * k
    bbox = fnt.getbbox(text, stroke_width=max(sw, rw))
    w, h = bbox[2] - bbox[0] + shadow * k + 8, bbox[3] - bbox[1] + shadow * k + 8
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ox, oy = -bbox[0] + 4, -bbox[1] + 4
    if shadow:
        d.text((ox + shadow * k, oy + shadow * k), text, font=fnt, fill=C["ink"] + (255,),
               stroke_width=max(sw, rw), stroke_fill=C["ink"] + (255,))
    if rim:
        d.text((ox, oy), text, font=fnt, fill=C["cream"] + (255,), stroke_width=rw, stroke_fill=C["cream"] + (255,))
    d.text((ox, oy), text, font=fnt, fill=tuple(fill) + (255,), stroke_width=sw, stroke_fill=C["ink"] + (255,))
    return img.resize((max(1, w // k), max(1, h // k)), Image.LANCZOS)


def make_logo() -> Image.Image:
    """ロゴ：錠剤アイコン＋「シネマホリック」＋「CINEMA HOLIC」。"""
    jp = text_block("シネマホリック", "heavy", 96, C["cream"], 8, 760, shadow=7)
    en_f = S.font("ui_bold", 34)
    en_text = "C I N E M A   H O L I C"
    en_w = int(en_f.getlength(en_text)) + 8
    pill = S.pill_icon(120, angle=-30)
    w = max(jp.width + pill.width + 10, en_w)
    h = jp.height + 56
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    img.alpha_composite(pill, (0, max(0, (jp.height - pill.height) // 2 - 6)))
    img.alpha_composite(jp, (pill.width + 10, 0))
    d = ImageDraw.Draw(img)
    d.text((pill.width + 10 + jp.width // 2, jp.height + 10), en_text, font=en_f, fill=C["gold"] + (255,), anchor="mt")
    return img


def render(cfg_path: str, out_dir: str):
    cfg = json.load(open(cfg_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    duration = cfg.get("duration", 2.0)
    bg_path = cfg.get("background")
    if bg_path and not os.path.isabs(bg_path):
        bg_path = os.path.join(ROOT, bg_path)
    base = S.room_background(bg_path, darken=0.62, blur=14).convert("RGBA")

    worry = cfg["worry"]                       # 例：上司を〇したい
    lead = cfg.get("lead", "そこの君に、")
    rest = cfg.get("rest", "いい薬を処方します。")
    big = text_block(worry, "heavy", 120, C["pill_red"], 9, 860, shadow=12, rim=6)
    mid = text_block(lead, "heavy", 70, C["cream"], 7, 860, shadow=6)
    low = text_block(rest, "heavy", 70, C["cream"], 7, 860, shadow=6)
    logo = make_logo()
    pill = S.pill_icon(150, angle=-28)
    logo.save(os.path.join(out_dir, "logo.png"))
    S.pill_icon(400, angle=-28).save(os.path.join(out_dir, "pill.png"))

    gap = 26
    total_h = pill.height + 40 + big.height + gap + mid.height + gap + low.height + 90 + logo.height
    y0 = (H - total_h) // 2 - 40
    y_pill = y0 + pill.height // 2
    y_big = y0 + pill.height + 40
    y_mid = y_big + big.height + gap
    y_low = y_mid + mid.height + gap
    y_logo = y_low + low.height + 90

    def frame(t: float) -> Image.Image:
        img = base.copy()
        # 錠剤：上から落ちて、カランと跳ねる
        if t >= T_PILL:
            p = S.progress(t, T_PILL, T_CLINK - T_PILL)
            fall = (1 - S.ease_out_cubic(p) if p < 1 else 0)
            bounce = 0
            if t > T_CLINK:
                q = S.progress(t, T_CLINK, 0.3)
                bounce = -40 * (4 * q * (1 - q))  # 小さく1回跳ねる
            yy = y_pill - 700 * fall ** 2 + bounce
            rot = pill.rotate(-25 * (1 - p), resample=Image.BICUBIC, expand=True)
            S.paste_scaled(img, rot, (CENTER_X, yy), 1.0)
        # 悩み：ドンと大きく出て、少し縮んで止まる＋画面がわずかに揺れる
        if t >= T_SLAM:
            p = S.progress(t, T_SLAM, 0.18)
            sc = 1.35 - 0.35 * S.ease_out_back(p, 2.2)
            S.paste_scaled(img, big, (CENTER_X, y_big + big.height / 2), sc, alpha=S.clamp(p * 4))
        if t >= T_REST:
            p = S.progress(t, T_REST, 0.2)
            dy = 30 * (1 - S.ease_out_cubic(p))
            S.paste_scaled(img, mid, (CENTER_X, y_mid + mid.height / 2 + dy), 1.0, alpha=p)
            p2 = S.progress(t, T_REST + 0.1, 0.2)
            dy2 = 30 * (1 - S.ease_out_cubic(p2))
            S.paste_scaled(img, low, (CENTER_X, y_low + low.height / 2 + dy2), 1.0, alpha=p2)
        if t >= T_LOGO:
            p = S.progress(t, T_LOGO, 0.25)
            S.paste_scaled(img, logo, (CENTER_X, y_logo + logo.height / 2), 0.92 + 0.08 * S.ease_out_back(p), alpha=p)
        # ジャンの瞬間の小さな揺れ
        shake = 0
        if T_SLAM <= t < T_SLAM + 0.15:
            shake = int(10 * (1 - (t - T_SLAM) / 0.15)) * (1 if int(t * 60) % 2 else -1)
        if shake:
            img = img.transform(img.size, Image.AFFINE, (1, 0, shake, 0, 1, 0), resample=Image.BILINEAR,
                                fillcolor=C["night"] + (255,))
        return img

    n = int(round(duration * S.FPS))
    S.save_video((frame(i / S.FPS) for i in range(n)), os.path.join(out_dir, "title.mp4"))
    frame(duration).convert("RGB").save(os.path.join(out_dir, "title_last.png"))
    json.dump({"duration": duration, "cues": [
        {"t": T_CLINK, "sfx": "brand/pill_clink", "note": "錠剤が着地（カラン）"},
        {"t": T_SLAM, "sfx": "brand/low_hit", "note": "悩みの文字が出る（ジャン）"},
    ]}, open(os.path.join(out_dir, "cues.json"), "w"), ensure_ascii=False, indent=2)
    print(f"書き出し完了: {out_dir}（{duration:.1f}秒）")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    render(sys.argv[1], sys.argv[2])
