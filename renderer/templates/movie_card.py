"""映画紹介の画面（処方箋ふう）を、movie.json から高画質に書き出す。

見た目と動きは「映画紹介メーカー」（tools/movie-card-maker/index.html）と同じ。
メーカーで作って「JSONをコピー」したもの、または各話の movie.json をそのまま渡せばよい。

使い方：
    python3 renderer/templates/movie_card.py <movie.json> <出力フォルダ>
出力：
    movie_card.mp4   … 要素が順に出てくる動き（音なし、約4秒）
    movie_card.png   … 完成した1枚
    cues.json        … 効果音のタイミング（はんこ等）
"""
from __future__ import annotations

import base64
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(__file__))
from chat import _serve, ROOT  # noqa: E402  （同じローカルサーバーの仕組みを使う）

PAGE = "tools/movie-card-maker/index.html?headless=1"
FPS = 30


def render(cfg_path: str, out_dir: str):
    from playwright.sync_api import sync_playwright

    cfg = json.load(open(cfg_path, encoding="utf-8"))
    os.makedirs(out_dir, exist_ok=True)
    srv = _serve()
    url = f"http://127.0.0.1:{srv.server_address[1]}/{PAGE}"
    with sync_playwright() as p:
        exe = "/opt/pw-browsers/chromium"
        browser = p.chromium.launch(**({"executable_path": exe} if os.path.exists(exe) else {}))
        page = browser.new_page(viewport={"width": 1080, "height": 1920})
        page.goto(url)
        page.wait_for_function("window.__ready === true")
        info = page.evaluate("c => window.loadCfg(c)", cfg)
        dur = info["duration"]
        n = int(round(dur * FPS))
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "png",
                               "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16",
                               os.path.join(out_dir, "movie_card.mp4")], stdin=subprocess.PIPE)

        def grab(t):
            return base64.b64decode(page.evaluate("t => window.frameAt(t)", t).split(",", 1)[1])

        for i in range(n):
            ff.stdin.write(grab(i / FPS))
        ff.stdin.close()
        ff.wait()
        open(os.path.join(out_dir, "movie_card.png"), "wb").write(grab(dur))
        browser.close()
    srv.shutdown()
    json.dump(info, open(os.path.join(out_dir, "cues.json"), "w"), ensure_ascii=False, indent=2)
    print(f"書き出し完了: {out_dir}（{dur:.1f}秒）")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    render(sys.argv[1], sys.argv[2])
