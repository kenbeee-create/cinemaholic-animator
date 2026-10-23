"""スタジオ（tools/studio/）で作った会話シーン（scene.json）を、高画質のMP4に書き出す。

使い方：
    python3 renderer/templates/studio.py <scene.json> <出力.mp4>
見た目と動きはスタジオのプレビューと同じ（同じページを裏で動かして1コマずつ描く）。音は入らない。
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from chat import _serve  # noqa: E402

PAGE = "tools/studio/index.html?headless=1"
FPS = 30


def render(scene_path: str, out: str):
    from playwright.sync_api import sync_playwright

    scene = json.load(open(scene_path, encoding="utf-8"))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    srv = _serve()
    with sync_playwright() as p:
        exe = "/opt/pw-browsers/chromium"
        b = p.chromium.launch(**({"executable_path": exe} if os.path.exists(exe) else {}))
        page = b.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(f"http://127.0.0.1:{srv.server_address[1]}/{PAGE}")
        page.wait_for_function("window.__ready === true")
        dur = page.evaluate("c => window.loadCfg(c)", scene)["duration"]
        n = int(round(dur * FPS))
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg",
                               "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", out], stdin=subprocess.PIPE)
        for i in range(n):
            ff.stdin.write(base64.b64decode(page.evaluate("t => window.frameAt(t)", i / FPS).split(",", 1)[1]))
        ff.stdin.close()
        ff.wait()
        b.close()
    srv.shutdown()
    print(f"書き出し完了: {out}（{dur:.1f}秒・{n}コマ）")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    render(sys.argv[1], sys.argv[2])
