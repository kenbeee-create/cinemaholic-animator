"""動画フォーマット（9シーン・60秒）の絵コンテを、実際の素材で描いて1枚のシートにする。

使い方：
    python3 renderer/preview/storyboard.py <出力フォルダ>
出力：
    storyboard.png        … 全コマを並べたシート
    panels/pXX.png        … 1コマずつ（1080x1920）
例の内容は「上司に怒られた回」。映画・監督・名言は 〇〇 のまま（台本ができたら差し替える）。
"""
from __future__ import annotations

import os
import sys
from collections import deque

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "renderer"))
sys.path.insert(0, os.path.join(ROOT, "renderer/rig"))
sys.path.insert(0, os.path.join(ROOT, "renderer/preview"))
from extract_patch import extract  # noqa: E402
from johndoe_reactions import PLACE, place, room, to_screen, fx  # noqa: E402
from motion.reactions import pose  # noqa: E402

W, H = 1080, 1920
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
FONT_B = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
SERIF = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Black.ttc"
INK = (31, 21, 15, 255)
CREAM = (240, 228, 204, 255)
PARKA = (176, 66, 46, 255)
RED = (196, 70, 47, 255)
G = os.path.join(ROOT, "assets/characters/gonbe")
J = os.path.join(ROOT, "assets/characters/johndoe")
TMP = os.path.join(ROOT, "output/_sb_tmp")


def f(path, size):
    return ImageFont.truetype(path, size, index=0)


# ---------- キャラの絵 ----------
def gonbe(eyes=None, mouth=None):
    img = Image.open(os.path.join(G, "sit_source.png")).convert("RGBA")
    if eyes:
        os.makedirs(TMP, exist_ok=True)
        tmp = os.path.join(TMP, f"eyes_{eyes}.png")
        if not os.path.exists(tmp):
            extract(os.path.join(G, "sit_source.png"), os.path.join(G, f"expressions_source/{eyes}.png"), tmp,
                    (330, 360, 820, 560))
        img.alpha_composite(Image.open(tmp))
    if mouth:
        img.alpha_composite(Image.open(os.path.join(G, f"parts/{mouth}.png")))
    return img


def johndoe_layers(mouth=None):
    head = Image.open(os.path.join(J, "parts/head.png")).convert("RGBA")
    if mouth:
        head = head.copy()
        head.alpha_composite(Image.open(os.path.join(J, f"parts/{mouth}.png")))
    return head, Image.open(os.path.join(J, "parts/body.png"))


def put_johndoe(fr, reaction="idle", t=0.6, mouth=None):
    import json
    rig = json.load(open(os.path.join(J, "rig.json")))
    pivot = tuple(rig["layers"][1]["pivot"])
    feet = (pivot[0], 1343)
    head, body = johndoe_layers(mouth)
    p = pose(reaction, t)
    place(fr, body, "johndoe", (p["body_sx"], p["body_sy"]), anchor_src=feet, offset=(p["body_dx"], p["body_dy"]))
    hs = p["head_s"]
    neck = (pivot[1] - feet[1]) * (p["body_sy"] - 1)
    place(fr, head, "johndoe", (p["body_sx"] * hs, p["body_sy"] * hs), anchor_src=pivot,
          offset=(p["body_dx"] + p["head_dx"], p["body_dy"] + p["head_dy"] + neck), rot=p["head_rot"], pivot_src=pivot)
    if p["fx"]:
        hb = rig["head_bbox"]
        hx, hy = to_screen("johndoe", (hb[0] + hb[2]) / 2, hb[1])
        fx(ImageDraw.Draw(fr), p["fx"], hx + 150, hy + 10, t)


def standing_gonbe():
    """入ってくるごんべぇ（仮）：オーナー提供の参考画像（立ち姿）の白背景を抜いたもの。"""
    im = Image.open(os.path.join(G, "reference/mouth_half_ref.png")).convert("RGBA")
    a = np.array(im)
    white = a[..., :3].min(axis=2) > 235
    h, w = white.shape
    seen = np.zeros_like(white)
    q = deque([(0, 0), (0, w - 1), (h - 1, 0), (h - 1, w - 1)])
    while q:
        y, x = q.popleft()
        if 0 <= y < h and 0 <= x < w and white[y, x] and not seen[y, x]:
            seen[y, x] = True
            q.extend([(y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)])
    a[..., 3] = np.where(seen, 0, 255)
    out = Image.fromarray(a)
    return out.crop(out.getbbox())


# ---------- 画面づくり ----------
_ROOM = None


def two_shot(g=None, jd="idle", jd_t=0.6, jd_mouth=None, tint=None):
    global _ROOM
    if _ROOM is None:
        _ROOM = room()
    fr = _ROOM.copy()
    if g is not None:
        place(fr, g, "gonbe")
    put_johndoe(fr, jd, jd_t, jd_mouth)
    if tint:
        layer = Image.new("RGBA", fr.size, tint)
        fr = Image.alpha_composite(fr, layer)
    return fr


def closeup(fr, who, zoom=1.9, focus=0.33):
    p = PLACE[who]
    sb = p["src_bbox"]
    cx, cy = to_screen(who, (sb[0] + sb[2]) / 2, sb[1] + (sb[3] - sb[1]) * focus)
    w, h = W / zoom, H / zoom
    box = (cx - w / 2, cy - h * 0.42, cx + w / 2, cy + h * 0.58)
    return fr.crop(tuple(int(v) for v in box)).resize((W, H), Image.LANCZOS)


def caption(fr, text, who, pos="auto", big=False):
    d = ImageDraw.Draw(fr)
    size = 110 if big else 60
    fnt = f(FONT, size)
    if who == "gonbe":
        bg, fg = PARKA, CREAM
    elif who == "johndoe":
        bg, fg = CREAM, INK
    else:
        bg, fg = None, CREAM
    tw = fnt.getlength(text)
    if pos == "auto":
        pos = (W * 0.46, 1380)
    x, y = pos
    if big:
        d.text((x, y), text, font=fnt, fill=fg if bg is None else bg, anchor="mm", stroke_width=10, stroke_fill=INK)
        return
    pad = 22
    d.rectangle((x - tw / 2 - pad, y - size * 0.7, x + tw / 2 + pad, y + size * 0.7), fill=bg, outline=INK, width=5)
    d.text((x, y), text, font=fnt, fill=fg, anchor="mm")


def text_card(lines, key=None, serif=False, sub=None):
    fr = Image.new("RGBA", (W, H), (12, 9, 7, 255))
    d = ImageDraw.Draw(fr)
    fnt = f(SERIF if serif else FONT, 76)
    y = H / 2 - len(lines) * 60
    for ln in lines:
        if key and key in ln:
            a, b = ln.split(key, 1)
            total = fnt.getlength(ln)
            x = W * 0.46 - total / 2
            d.text((x, y), a, font=fnt, fill=CREAM, anchor="lm")
            x += fnt.getlength(a)
            d.text((x, y), key, font=fnt, fill=RED, anchor="lm")
            x += fnt.getlength(key)
            d.text((x, y), b, font=fnt, fill=CREAM, anchor="lm")
        else:
            d.text((W * 0.46, y), ln, font=fnt, fill=CREAM, anchor="mm")
        y += 120
    if sub:
        d.text((W * 0.46, y + 40), sub, font=f(FONT_B, 36), fill=(176, 160, 136, 255), anchor="mm")
    return fr


def prescription(base):
    fr = base.copy()
    fr = Image.alpha_composite(fr, Image.new("RGBA", fr.size, (0, 0, 0, 140)))
    d = ImageDraw.Draw(fr)
    x0, y0, x1, y1 = 110, 430, 850, 1360
    d.rounded_rectangle((x0 + 14, y0 + 18, x1 + 14, y1 + 18), 26, fill=(0, 0, 0, 160))
    d.rounded_rectangle((x0, y0, x1, y1), 26, fill=(244, 236, 214, 255), outline=INK, width=7)
    d.text(((x0 + x1) / 2, y0 + 80), "処 方 箋", font=f(FONT, 72), fill=INK, anchor="mm")
    d.text(((x0 + x1) / 2, y0 + 140), "CINEMA HOLIC", font=f(FONT_B, 30), fill=(150, 120, 70, 255), anchor="mm")
    d.line((x0 + 50, y0 + 185, x1 - 50, y0 + 185), fill=INK, width=4)
    rows = [("今週の処方", "〇〇〇〇（20XX）"), ("用量", "一人で、深夜に"), ("副作用", "〇〇したくなる")]
    yy = y0 + 270
    for k, v in rows:
        d.text((x0 + 60, yy), k, font=f(FONT_B, 38), fill=(120, 100, 80, 255), anchor="lm")
        d.text((x0 + 60, yy + 70), v, font=f(FONT, 56), fill=INK, anchor="lm")
        yy += 200
    cx, cy = x1 - 130, y1 - 140
    d.ellipse((cx - 95, cy - 95, cx + 95, cy + 95), outline=RED, width=10)
    d.text((cx, cy), "処方", font=f(FONT, 62), fill=RED, anchor="mm")
    return fr


def from_file(path):
    im = Image.open(path).convert("RGBA")
    return im.resize((W, H), Image.LANCZOS) if im.size != (W, H) else im


# ---------- 絵コンテの中身 ----------
def panels():
    P = []
    S = "renderer/templates/examples/preview/"

    def add(scene, sec, img, shot, what, sound=""):
        P.append(dict(scene=scene, sec=sec, img=img, shot=shot, what=what, sound=sound))

    chat_first = from_file(os.path.join(ROOT, S, "chat_first.jpg"))
    chat_last = from_file(os.path.join(ROOT, S, "chat_last.jpg"))
    title = from_file(os.path.join(ROOT, S, "title_last.jpg"))
    add("S1 トーク画面", "0.0-1.5", chat_first, "スマホの画面に寄る",
        "ごんべぇの不満が「…」→届く。1通目で手を止める", "通知音")
    add("S1 トーク画面", "1.5-3.0", chat_last, "スマホ（ゆっくり寄る）",
        "続けて届く→「今日行くわ」", "通知音×3")
    add("S2 タイトル", "3.0-5.0", title, "タイトルカード",
        "錠剤が落ちる→悩みの文字がドン→ロゴ", "カラン→ジャン")

    # S3 入り
    fr = two_shot(None, "idle")
    st = standing_gonbe()
    th = 470  # 立ち姿の高さ（画面上）
    st2 = st.resize((int(st.width * th / st.height), th), Image.LANCZOS)
    fr.alpha_composite(st2, (40, 1190 - th))
    caption(fr, "Here's Johnny!", "gonbe", (300, 470))
    add("S3 入り", "5.0-6.5", fr, "引き（部屋は映画仕様）",
        "ごんべぇが入ってきて、入りのひと言（立ち姿は仮）", "ドア")
    fr = closeup(two_shot(gonbe(), "look_away", 0.6, "mouth_half"), "johndoe")
    caption(fr, "…働きすぎ。", "johndoe")
    add("S3 入り", "6.5-8.0", fr, "じょんどぅーのアップ",
        "振り向かずにぼそっと返す（そっぽ＋汗）", "")
    fr = closeup(two_shot(gonbe("eyes_closed", "mouth_small"), "idle"), "gonbe")
    caption(fr, "…はぁ。上司マジで無理", "gonbe")
    add("S3 悩み", "8.0-10.0", fr, "ごんべぇのアップ",
        "ため息で悩みを言う（ため息の顔は作成中）", "ため息")

    # S4 返し
    fr = two_shot(gonbe(), "tilt", 0.6, "mouth_half")
    caption(fr, "〇〇、見た？", "johndoe", (700, 470))
    add("S4 返し", "10.0-11.5", fr, "2ショット",
        "じょんどぅーが首をかしげて聞く", "")
    fr = closeup(two_shot(gonbe("eyes_jito", "mouth_half"), "idle"), "gonbe")
    caption(fr, "〇〇なやつじゃん", "gonbe")
    add("S4 返し", "11.5-13.0", fr, "ごんべぇのアップ", "ジト目で、ありがちな決めつけ", "")
    fr = closeup(two_shot(gonbe(), "lean_in", 0.6, "mouth_open"), "johndoe", 1.7)
    caption(fr, "そう思ってるやつ", None, (W * 0.46, 1150), big=True)
    caption(fr, "損してる", None, (W * 0.46, 1300), big=True)
    add("S4 返し", "13.0-15.0", fr, "じょんどぅーのアップ（寄る）",
        "乗り出して決めゼリフ。テロップ特大", "ドン")

    # S5 バックボーン
    add("S5 バックボーン", "15.0-18.0", text_card(["監督の〇〇は", "〇〇だった"], key="〇〇だった", sub="（事実確認ずみの1行）"),
        "黒背景テキスト", "監督の過去を1行ずつ", "タイプ音")
    fr = two_shot(gonbe(), "nod", 0.3, "mouth_half")
    caption(fr, "その人が撮ったのが、これ", "johndoe", (W * 0.46, 1380))
    add("S5 バックボーン", "18.0-22.0", fr, "2ショット",
        "じょんどぅーがだらだら語る。ごんべぇは半目で聞く", "")
    add("S5 バックボーン", "22.0-25.0", text_card(["〇〇年、〇〇の時代"], sub="（時代背景）"),
        "黒背景テキスト", "時代背景を1行", "タイプ音")

    # S6 核心
    fr = closeup(two_shot(gonbe(None, "mouth_half"), "idle"), "gonbe")
    caption(fr, "…えぐいな", "gonbe")
    add("S6 核心", "25.0-29.0", fr, "ごんべぇのアップ", "引き込まれていく", "")
    fr = closeup(two_shot(gonbe(), "nod", 0.3, "mouth_half"), "johndoe")
    caption(fr, "〇〇、全部入ってるよ", "johndoe")
    add("S6 核心", "29.0-33.0", fr, "じょんどぅーのアップ", "うなずきながら、ぽろっと核心", "")
    fr = two_shot(gonbe("eyes_jito", "mouth_small"), "look_away", 0.6)
    caption(fr, "…なんで知ってんの", "gonbe", (360, 470))
    add("S6 核心", "33.0-37.0", fr, "2ショット", "ごんべぇのツッコミ未満。じょんどぅーはそらす", "")
    fr = closeup(two_shot(gonbe(), "freeze", 0.6), "gonbe", 4.2, focus=0.27)
    add("S6 核心", "37.0-40.0", fr, "ごんべぇの大アップ", "黙る。間（…）", "無音0.5秒")

    # S7 名言
    add("S7 名言", "40.0-48.0", text_card(["「〇〇〇〇〇〇」"], key="〇〇〇〇〇〇", serif=True, sub="— 〇〇（監督）"),
        "黒背景テキスト", "名言。キーワードだけ赤", "低音")

    # S8 処方箋
    add("S8 処方箋", "48.0-54.0", prescription(two_shot(gonbe(), "idle")), "処方箋カード",
        "今週の処方・用量・副作用→スタンプ", "スタンプ「ドン」")
    fr = two_shot(gonbe(None, "mouth_small"), "bounce", 0.3, tint=(40, 90, 140, 70))
    caption(fr, "…こわ。", "gonbe", (360, 470))
    add("S8 処方箋", "54.0-57.0", fr, "2ショット（照明が映画の色に）",
        "電気を消してテレビをつける→部屋が映画の色に", "")

    # S9 締め
    fr = title.copy()
    d = ImageDraw.Draw(fr)
    caption(fr, "…おれも、同じ感じの時だったな", "johndoe", (W * 0.46, 1420))
    d.text((W * 0.46, 1520), "あなたの悩み、コメントに書いて", font=f(FONT_B, 44), fill=CREAM, anchor="mm",
           stroke_width=5, stroke_fill=INK)
    add("S9 締め", "57.0-60.0", fr, "タイトルカード＋声だけ",
        "伏線のひと言（声）＋コメント募集", "BGMフェードアウト")
    return P


def sheet(P, out_dir):
    os.makedirs(os.path.join(out_dir, "panels"), exist_ok=True)
    cols, tw, th = 4, 300, 533
    cell_h = th + 210
    rows = (len(P) + cols - 1) // cols
    head_h = 120
    sh = Image.new("RGB", (cols * (tw + 24) + 24, head_h + rows * (cell_h + 24) + 24), (27, 21, 17))
    d = ImageDraw.Draw(sh)
    d.text((24, 30), "シネマホリック 絵コンテ（フォーマット・例：上司に怒られた回）", font=f(FONT, 40), fill=CREAM)
    d.text((24, 82), "〇〇は台本ができたら差し替え。キャラ・部屋・トーク画面・タイトルは実際の素材", font=f(FONT_B, 24),
           fill=(176, 160, 136))
    for i, p in enumerate(P):
        p["img"].convert("RGB").save(os.path.join(out_dir, "panels", f"p{i + 1:02d}.png"))
        x = 24 + (i % cols) * (tw + 24)
        y = head_h + (i // cols) * (cell_h + 24)
        sh.paste(p["img"].convert("RGB").resize((tw, th), Image.LANCZOS), (x, y))
        d.rectangle((x, y, x + tw, y + th), outline=(61, 48, 38), width=2)
        d.rounded_rectangle((x + 8, y + 8, x + 62, y + 44), 8, fill=(176, 66, 46))
        d.text((x + 35, y + 26), f"{i + 1}", font=f(FONT, 26), fill=CREAM, anchor="mm")
        ty = y + th + 10
        d.text((x, ty), f"{p['scene']}  {p['sec']}秒", font=f(FONT, 22), fill=(201, 163, 90))
        d.text((x, ty + 34), p["shot"], font=f(FONT_B, 21), fill=CREAM)
        # 説明（折り返し）
        fnt = f(FONT_B, 20)
        line, yy = "", ty + 66
        for ch in p["what"]:
            if fnt.getlength(line + ch) > tw:
                d.text((x, yy), line, font=fnt, fill=(210, 198, 176))
                yy += 28
                line = ch
            else:
                line += ch
        d.text((x, yy), line, font=fnt, fill=(210, 198, 176))
        if p["sound"]:
            d.text((x, yy + 36), "♪ " + p["sound"], font=f(FONT_B, 20), fill=(150, 170, 200))
    sh.save(os.path.join(out_dir, "storyboard.png"))
    print("書き出し完了:", os.path.join(out_dir, "storyboard.png"), f"（{len(P)}コマ）")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "output/storyboard")
    sheet(panels(), out)
