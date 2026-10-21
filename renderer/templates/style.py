"""シネマホリックのトーン（色・線・フォント）と描画の共通部品。

全テンプレート（トーク画面・タイトル・処方箋など）はここの値だけを使う。
色やフォントを変えたいときは、このファイルだけを直せば全部に反映される。
基準は docs/tone.md。
"""
from __future__ import annotations

import os
import random
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---- 画面 -------------------------------------------------------------
W, H = 1080, 1920
FPS = 30
SS = 2  # 部品は2倍で描いて縮小する（輪郭をなめらかにするため）

# SNSのUIと重なる場所（ここに大事な文字を置かない）
SAFE_TOP = 230      # 上：アカウント名・検索など
SAFE_BOTTOM = 1560  # 下：キャプション・音源名など
SAFE_RIGHT = 900    # 右：いいね・コメントのボタン列

# ---- 色（キャラと部屋の絵から取った色） ---------------------------------
C = {
    "ink": (31, 21, 15),          # 輪郭線（こげ茶に近い黒）
    "night": (27, 21, 17),        # 夜の部屋の暗さ（背景）
    "night_2": (44, 34, 27),      # 一段明るい暗色（ヘッダー・入力欄）
    "night_3": (61, 48, 38),      # さらに明るい暗色（日付のラベル）
    "cream": (240, 228, 204),     # じょんどぅーのTシャツのクリーム
    "cream_dim": (176, 160, 136), # 小さい文字（時刻・既読）
    "parka": (176, 66, 46),       # ごんべぇの赤パーカー
    "parka_dark": (128, 45, 31),
    "denim": (36, 52, 74),        # ごんべぇの紺のズボン
    "khaki": (122, 116, 94),      # じょんどぅーの短パン
    "fur_brown": (139, 78, 38),   # ごんべぇの毛
    "lamp": (226, 176, 96),       # 間接照明の黄色
    "gold": (201, 163, 90),       # ロゴの英字
    "pill_red": (196, 70, 47),    # 錠剤（赤）
}

# 話者ごとの色（テロップ・吹き出しで共通）
SPEAKER = {
    "gonbe": {"fill": C["parka"], "text": C["cream"]},
    "johndoe": {"fill": C["cream"], "text": C["ink"]},
}

LINE_W = 6  # 輪郭線の太さ（1080px基準）

# ---- フォント -----------------------------------------------------------
_NOTO = "/usr/share/fonts/opentype/noto"
FONT_FILES = {
    "ui": f"{_NOTO}/NotoSansCJK-Medium.ttc",
    "ui_bold": f"{_NOTO}/NotoSansCJK-Bold.ttc",
    "heavy": f"{_NOTO}/NotoSansCJK-Black.ttc",
    "serif_heavy": f"{_NOTO}/NotoSerifCJK-Black.ttc",
}
FONT_INDEX_JP = 0  # .ttc の中の日本語版


@lru_cache(maxsize=None)
def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONT_FILES[kind]
    if not os.path.exists(path):
        raise FileNotFoundError(f"フォントが見つかりません: {path}（docs/tone.md のフォント欄を参照）")
    return ImageFont.truetype(path, size, index=FONT_INDEX_JP)


# ---- 動きのカーブ -------------------------------------------------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out_cubic(t):
    t = clamp(t)
    return 1 - (1 - t) ** 3


def ease_out_back(t, s=1.6):
    t = clamp(t)
    t -= 1
    return t * t * ((s + 1) * t + s) + 1


def progress(t, start, dur):
    return clamp((t - start) / dur) if dur > 0 else float(t >= start)


# ---- 描画の部品 ---------------------------------------------------------
def night_background(seed: int = 7, vignette: float = 0.55) -> Image.Image:
    """夜の部屋っぽい暗い背景（上から間接照明がほんのり当たる＋粒子）。"""
    base = Image.new("RGB", (W, H), C["night"])
    glow = Image.new("L", (W, H), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse((-300, -500, W + 300, 900), fill=70)
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    lamp = Image.new("RGB", (W, H), C["night_3"])
    base = Image.composite(lamp, base, glow)
    base = add_vignette(base, vignette)
    return add_grain(base, seed=seed)


def add_vignette(img: Image.Image, strength: float = 0.5) -> Image.Image:
    mask = Image.new("L", img.size, 0)
    d = ImageDraw.Draw(mask)
    w, h = img.size
    d.ellipse((-w * 0.25, -h * 0.15, w * 1.25, h * 1.15), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(min(w, h) * 0.18))
    dark = Image.new("RGB", img.size, (8, 6, 5))
    out = Image.composite(img, dark, mask)
    return Image.blend(img, out, strength)


def add_grain(img: Image.Image, amount: int = 7, seed: int = 7) -> Image.Image:
    rnd = random.Random(seed)
    small = Image.new("L", (img.width // 3, img.height // 3))
    small.putdata([128 + rnd.randint(-amount, amount) for _ in range(small.width * small.height)])
    noise = small.resize(img.size, Image.NEAREST).convert("RGB")
    from PIL import ImageChops
    return Image.blend(img, ImageChops.overlay(img, noise), 0.5)


def outlined_shape(mask: Image.Image, fill, line_w: int, shadow=(0, 0), shadow_alpha: int = 0) -> Image.Image:
    """白黒の形（mask）から、塗り＋太い輪郭線（＋ずらした影）の透過画像を作る。
    しっぽ付きの吹き出しなど、形を組み合わせても輪郭が1本につながる。"""
    from PIL import ImageFilter as F
    size = mask.size
    out = Image.new("RGBA", size, (0, 0, 0, 0))
    grown = mask.filter(F.MaxFilter(line_w * 2 + 1)) if line_w > 0 else mask
    if shadow_alpha:
        sh = Image.new("RGBA", size, C["ink"] + (shadow_alpha,))
        out.paste(sh, shadow, grown)
    ink = Image.new("RGBA", size, C["ink"] + (255,))
    out.paste(ink, (0, 0), grown)
    out.paste(Image.new("RGBA", size, tuple(fill) + (255,)), (0, 0), mask)
    return out


def room_background(path: str | None, darken: float = 0.3, blur: int = 10, zoom: float = 1.12) -> Image.Image:
    """その回の部屋の絵を、ぼかして暗くした背景にする（無ければ夜の背景）。"""
    if not path or not os.path.exists(path):
        return night_background()
    src = Image.open(path).convert("RGB")
    sc = max(W / src.width, H / src.height) * zoom  # 少し寄せる（端のロゴなどを画面外へ）
    src = src.resize((int(src.width * sc) + 1, int(src.height * sc) + 1), Image.LANCZOS)
    x, y = (src.width - W) // 2, int((src.height - H) * 0.4)
    img = src.crop((x, y, x + W, y + H)).filter(ImageFilter.GaussianBlur(blur))
    img = Image.blend(img, Image.new("RGB", img.size, C["night"]), darken)
    return add_grain(add_vignette(img, 0.5))


def balance_lines(lines: list[str], fnt, max_w: int) -> list[str]:
    """最後の行が1〜2文字だけになるのを防ぐ（「怒られ／た」を「めっちゃ／怒られた」にする）。"""
    if len(lines) >= 2 and len(lines[-1]) <= 2:
        text = "".join(lines)
        n = len(lines)
        per = -(-len(text) // n)
        out = [text[i:i + per] for i in range(0, len(text), per)]
        if all(fnt.getlength(l) <= max_w * 1.02 for l in out):
            return out
    return lines


def outlined_text(draw: ImageDraw.ImageDraw, xy, text, fnt, fill, stroke=None, stroke_w=0, anchor="la"):
    draw.text(xy, text, font=fnt, fill=fill, anchor=anchor,
              stroke_width=stroke_w, stroke_fill=stroke if stroke else fill)


def wrap_text(text: str, fnt: ImageFont.FreeTypeFont, max_w: int) -> list[str]:
    """日本語向けの折り返し（1文字ずつ見て、はみ出したら改行。句読点は行頭に来ないように）。"""
    no_head = set("、。，．・ー〜！？!?）」』…")
    lines, cur = [], ""
    for ch in text:
        if ch == "\n":
            lines.append(cur)
            cur = ""
            continue
        trial = cur + ch
        if fnt.getlength(trial) <= max_w or not cur:
            cur = trial
        elif ch in no_head:
            cur = trial  # 句読点はぶら下げる
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


def paste_scaled(dst: Image.Image, src: Image.Image, anchor_xy, scale: float, origin=(0.5, 0.5), alpha: float = 1.0):
    """src を scale 倍にして、origin（src内の割合）が anchor_xy に来るように貼る。"""
    if scale <= 0.01 or alpha <= 0.01:
        return
    w, h = max(1, int(src.width * scale)), max(1, int(src.height * scale))
    s = src.resize((w, h), Image.LANCZOS)
    if alpha < 1:
        a = s.getchannel("A").point(lambda v: int(v * alpha))
        s.putalpha(a)
    x = int(anchor_xy[0] - origin[0] * w)
    y = int(anchor_xy[1] - origin[1] * h)
    dst.alpha_composite(s, (x, y)) if dst.mode == "RGBA" else dst.paste(s, (x, y), s)


def circle_icon(path: str, size: int, bg=None) -> Image.Image:
    """アイコン画像を丸く切り抜き、輪郭線をつける。"""
    k = SS
    s = size * k
    src = Image.open(path).convert("RGBA")
    side = min(src.size)
    src = src.crop(((src.width - side) // 2, (src.height - side) // 2,
                    (src.width + side) // 2, (src.height + side) // 2)).resize((s, s), Image.LANCZOS)
    canvas = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    mask = Image.new("L", (s, s), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, s - 1, s - 1), fill=255)
    filled = Image.new("RGBA", (s, s), (bg or C["night_3"]) + (255,))
    filled.alpha_composite(src)
    canvas.paste(filled, (0, 0), mask)
    ImageDraw.Draw(canvas).ellipse((k, k, s - k, s - k), outline=C["ink"] + (255,), width=LINE_W * k)
    return canvas.resize((size, size), Image.LANCZOS)


def pill_icon(size: int = 200, angle: float = -32) -> Image.Image:
    """ブランドの錠剤（カプセル）アイコン。赤とクリームの2色。"""
    k = SS * 2
    w, h = int(size * 0.92) * k, int(size * 0.40) * k
    lw = LINE_W * k
    img = Image.new("RGBA", (w + lw * 2, h + lw * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    box = (lw, lw, lw + w, lw + h)
    r = h // 2
    # 右半分クリーム → 左半分赤
    d.rounded_rectangle(box, r, fill=C["cream"] + (255,))
    left = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(left).rounded_rectangle(box, r, fill=C["pill_red"] + (255,))
    cut = Image.new("L", img.size, 0)
    ImageDraw.Draw(cut).rectangle((0, 0, lw + w // 2, img.height), fill=255)
    img.paste(left, (0, 0), Image.composite(left.getchannel("A"), Image.new("L", img.size, 0), cut))
    # 継ぎ目と輪郭
    d.line((lw + w // 2, lw, lw + w // 2, lw + h), fill=C["ink"] + (255,), width=lw)
    d.rounded_rectangle(box, r, outline=C["ink"] + (255,), width=lw)
    # ハイライト
    d.rounded_rectangle((lw + r * 0.6, lw + h * 0.18, lw + w * 0.42, lw + h * 0.34), h * 0.08,
                        fill=(255, 245, 230, 170))
    img = img.rotate(angle, resample=Image.BICUBIC, expand=True)
    bbox = img.getbbox()
    img = img.crop(bbox)
    return img.resize((max(1, img.width // k), max(1, img.height // k)), Image.LANCZOS)


def save_video(frames_iter, out_path: str, fps: int = FPS):
    """RGB画像の列をMP4に書き出す（音なし。音は sound-designer が後で乗せる）。"""
    import subprocess
    p = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{W}x{H}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", "-preset", "medium", out_path,
    ], stdin=subprocess.PIPE)
    for fr in frames_iter:
        p.stdin.write(fr.convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() != 0:
        raise RuntimeError("ffmpeg の書き出しに失敗しました")
