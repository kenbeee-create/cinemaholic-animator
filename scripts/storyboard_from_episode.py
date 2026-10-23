"""書き出した回（episode.json と output/<回>/segments/）から、実際のコマで絵コンテのシートを作る。

使い方：
    python3 scripts/storyboard_from_episode.py episodes/epXX-<slug>/episode.json [出力.png]
先に `python3 renderer/assemble.py episodes/epXX-<slug>/episode.json` で書き出しておくこと。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BLACK = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
f = lambda p, s: ImageFont.truetype(p, s, index=0)
CREAM, DIM, GOLD, PARKA = (240, 228, 204), (176, 160, 136), (201, 163, 90), (176, 66, 46)

TOOL_LABEL = {"chat-maker": "トーク画面", "title": "タイトル", "studio": "会話（スタジオ）",
              "movie-card-maker": "映画紹介", "card-maker": "文字の画面"}
CARD_LABEL = {"text": "バックボーン", "quote": "名言", "rx": "処方箋"}
CAM = {"two": "2ショット", "gonbe": "ごんべぇアップ", "johndoe": "じょんどぅーアップ", "gonbe_face": "ごんべぇの顔",
       "johndoe_face": "じょんどぅーの顔", "wide": "部屋全体"}
EYES = {"normal": "半目", "jito": "ジト目", "closed": "目を閉じる", "angry": "真顔"}
REACT = {"idle": "待機", "nod": "うなずく", "tilt": "首かしげ", "shake": "首を振る", "bounce": "ノる", "lean_in": "乗り出す",
         "slump": "しょんぼり", "puff": "ゾワッ", "freeze": "固まる", "look_away": "そっぽ"}
SPK = {"gonbe": "ごんべぇ", "johndoe": "じょんどぅー"}


def grab(mp4, t, path):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0, t):.3f}", "-i", mp4, "-frames:v", "1", path], check=True)
    return Image.open(path).convert("RGB")


def dur(mp4):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", mp4],
                                capture_output=True, text=True).stdout)


def load(base, c):
    if isinstance(c, dict):
        return c
    for p in (os.path.join(base, c), os.path.join(ROOT, c)):
        if os.path.exists(p):
            return json.load(open(p, encoding="utf-8"))


def cam_label(c):
    if not c:
        return "2ショット"
    fr, to = c.get("from", {}), c.get("to", c.get("from", {}))
    a = CAM.get(fr.get("preset"), "手で調整")
    b = CAM.get(to.get("preset"), "手で調整")
    return a if a == b else f"{a}→{b}"


def main(ep_path, out=None):
    ep = json.load(open(ep_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(ep_path))
    slug = os.path.basename(base)
    seg_dir = os.path.join(ROOT, "output", slug, "segments")
    tmp = os.path.join(seg_dir, "_sb")
    os.makedirs(tmp, exist_ok=True)
    panels, t0 = [], 0.0
    for i, seg in enumerate(ep["segments"]):
        mp4 = os.path.join(seg_dir, f"{i:02d}_{seg['tool']}.mp4")
        d = dur(mp4)
        cfg = load(base, seg["cfg"])
        tool = seg["tool"]
        if tool == "studio":
            st = 0.0
            for k, s in enumerate(cfg["shots"]):
                sd = float(s.get("dur", 1))
                img = grab(mp4, st + sd * 0.7, os.path.join(tmp, f"{i}_{k}.jpg"))
                cap = (s.get("caption") or "").replace("/", "")
                who = SPK.get(s.get("speaker"), "")
                g, j = s.get("gonbe", {}), s.get("johndoe", {})
                lines = [cam_label(s.get("cam")) + ("・グッと寄る" if s.get("punch") else "")]
                if cap:
                    lines.append(f"{who}「{cap}」" + ("（特大）" if s.get("big") else ""))
                lines.append(f"ごんべぇ：{EYES.get(g.get('eyes', 'normal'))}{'・話す' if g.get('talk') else ''}"
                             f"／じょんどぅー：{REACT.get(j.get('reaction', 'idle'))}{'・話す' if j.get('talk') else ''}")
                panels.append(dict(img=img, kind="会話", t=(t0 + st, t0 + st + sd), lines=lines, who=s.get("speaker")))
                st += sd
        else:
            label = CARD_LABEL.get(cfg.get("type"), "文字") if tool == "card-maker" else TOOL_LABEL[tool]
            img = grab(mp4, d - 0.05, os.path.join(tmp, f"{i}.jpg"))
            if tool == "chat-maker":
                lines = ["「" + "」「".join(m["text"] for m in cfg["messages"]) + "」"]
            elif tool == "title":
                lines = [f"{cfg.get('worry')} {cfg.get('lead', '')}{cfg.get('rest', '')}"]
            elif tool == "movie-card-maker":
                lines = [f"{cfg.get('title')}（{cfg.get('year')}）", "ポスター・効きめ・もらえる薬局・白衣のじょんどぅー"]
            elif cfg.get("type") == "text":
                lines = [cfg.get("lines", "").replace("\n", " ").replace("【", "").replace("】", "")]
            elif cfg.get("type") == "quote":
                lines = [cfg.get("quote", "").replace("【", "").replace("】", ""), "— " + cfg.get("who", "")]
            else:
                lines = [f"処方：{cfg.get('title')}／用量：{cfg.get('dose')}／副作用：{cfg.get('side')}"]
            panels.append(dict(img=img, kind=label, t=(t0, t0 + d), lines=lines, who=None))
        t0 += d

    # シート
    cols, tw, th = 4, 300, 533
    cell_h = th + 190
    rows = (len(panels) + cols - 1) // cols
    head = 130
    W = cols * (tw + 24) + 24
    sheet = Image.new("RGB", (W, head + rows * (cell_h + 24) + 24), (27, 21, 17))
    d = ImageDraw.Draw(sheet)
    d.text((24, 26), f"シネマホリック 絵コンテ（{slug}・{t0:.0f}秒・{len(panels)}コマ）", font=f(BLACK, 38), fill=CREAM)
    d.text((24, 80), "実際に書き出した動画のコマ。〇〇は台本で確定するところ。声・ポスター・照れ笑いなどは素材待ち",
           font=f(BOLD, 22), fill=DIM)
    for n, p in enumerate(panels):
        x = 24 + (n % cols) * (tw + 24)
        y = head + (n // cols) * (cell_h + 24)
        sheet.paste(p["img"].resize((tw, th), Image.LANCZOS), (x, y))
        col = PARKA if p["who"] == "gonbe" else (CREAM if p["who"] == "johndoe" else (61, 48, 38))
        d.rectangle((x, y, x + tw, y + th), outline=col, width=3)
        d.rounded_rectangle((x + 8, y + 8, x + 58, y + 42), 8, fill=PARKA)
        d.text((x + 33, y + 25), str(n + 1), font=f(BLACK, 24), fill=CREAM, anchor="mm")
        ty = y + th + 8
        d.text((x, ty), f"{p['kind']}  {p['t'][0]:.1f}–{p['t'][1]:.1f}秒", font=f(BLACK, 21), fill=GOLD)
        yy = ty + 32
        fnt = f(BOLD, 19)
        for ln in p["lines"]:
            cur = ""
            for ch in ln:
                if fnt.getlength(cur + ch) > tw:
                    d.text((x, yy), cur, font=fnt, fill=(214, 202, 180))
                    yy += 26
                    cur = ch
                else:
                    cur += ch
            if yy > ty + 175:
                break
            d.text((x, yy), cur, font=fnt, fill=(214, 202, 180))
            yy += 28
    out = out or os.path.join(ROOT, "output", slug, "storyboard.png")
    sheet.save(out)
    print("書き出し完了:", out, f"（{len(panels)}コマ）")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
