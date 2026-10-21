"""冒頭のトーク画面（Scene1）を、高画質のMP4に書き出す。

見た目と動きは「トーク画面メーカー」（tools/chat-maker/index.html）と完全に同じ。
メーカーで作って「JSONをコピー」したものを、そのまま渡せばよい。

使い方：
    python3 renderer/templates/chat.py <chat.json> <出力フォルダ>

出力：
    chat.mp4        … 動くトーク画面（音なし、1080x1920・30fps）
    chat_first.png  … 最初のメッセージが出たコマ
    chat_last.png   … 最後のコマ
    cues.json       … 効果音を鳴らすタイミング（sound-designer 用）

しくみ：メーカーのページを裏で開き（Playwright＋Chromium）、1コマずつ描かせて ffmpeg でつなぐ。
"""
from __future__ import annotations

import base64
import functools
import http.server
import json
import os
import socketserver
import subprocess
import sys
import threading

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAGE = "tools/chat-maker/index.html?headless=1"
FPS = 30


def _serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a, **k):
            pass
    handler = functools.partial(Quiet, directory=ROOT)
    srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def render(cfg_path: str, out_dir: str):
    from playwright.sync_api import sync_playwright

    cfg = json.load(open(cfg_path, encoding="utf-8"))
    # メーカーで端末から選んだアイコン画像はJSONに入らないので、既定のアイコンに戻す
    for v in (cfg.get("icons") or {}).values():
        if isinstance(v, dict) and v.get("src") and not str(v["src"]).startswith(("data:", "http", "../", "/")):
            v["src"] = None
    os.makedirs(out_dir, exist_ok=True)
    srv = _serve()
    url = f"http://127.0.0.1:{srv.server_address[1]}/{PAGE}"
    exe = "/opt/pw-browsers/chromium" if os.path.exists("/opt/pw-browsers/chromium") else None
    with sync_playwright() as p:
        kw = {"executable_path": exe} if exe and os.path.isfile(exe) else {}
        browser = p.chromium.launch(**kw)
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(url)
        page.wait_for_function("window.__ready === true")
        info = page.evaluate("c => window.loadCfg(c)", cfg)
        dur = info["duration"]
        n = int(round(dur * FPS))
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS),
                               "-c:v", "png", "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                               "-crf", "16", os.path.join(out_dir, "chat.mp4")], stdin=subprocess.PIPE)

        def grab(t):
            return base64.b64decode(page.evaluate("t => window.frameAt(t)", t).split(",", 1)[1])

        for i in range(n):
            ff.stdin.write(grab(i / FPS))
        ff.stdin.close()
        if ff.wait() != 0:
            raise RuntimeError("ffmpeg の書き出しに失敗しました")
        first = next((c["t"] for c in info["cues"] if c.get("sfx")), 0.5)
        open(os.path.join(out_dir, "chat_first.png"), "wb").write(grab(first + 0.3))
        open(os.path.join(out_dir, "chat_last.png"), "wb").write(grab(dur))
        browser.close()
    srv.shutdown()
    json.dump(info, open(os.path.join(out_dir, "cues.json"), "w"), ensure_ascii=False, indent=2)
    print(f"書き出し完了: {out_dir}（{dur:.1f}秒・{n}コマ）")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    render(sys.argv[1], sys.argv[2])
