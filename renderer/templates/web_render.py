"""ブラウザで作る道具（tools/*/index.html）を裏で動かし、JSONから高画質の動画・画像に書き出す共通部品。

どの道具も次の決まりで作ってある：
    ?headless=1 で開くと window.__ready = true になる
    window.loadCfg(cfg) → {duration, cues}
    window.frameAt(t)   → その時刻の画面（data URL）

使い方：
    python3 renderer/templates/web_render.py <道具の名前> <設定.json> <出力.mp4> [最後のコマ.png]
    道具の名前：studio / movie-card-maker / card-maker / chat-maker
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
FPS = 30


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a, **k):
            pass
    srv = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=ROOT))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


class Renderer:
    """1つのブラウザを開いたまま、いくつもの場面を続けて書き出す。"""

    def __enter__(self):
        from playwright.sync_api import sync_playwright
        self.srv = serve()
        self.pw = sync_playwright().start()
        exe = "/opt/pw-browsers/chromium"
        self.browser = self.pw.chromium.launch(**({"executable_path": exe} if os.path.exists(exe) else {}))
        self.pages = {}
        return self

    def page(self, tool):
        if tool not in self.pages:
            p = self.browser.new_page(viewport={"width": 1080, "height": 1920})
            p.goto(f"http://127.0.0.1:{self.srv.server_address[1]}/tools/{tool}/index.html?headless=1")
            p.wait_for_function("window.__ready === true", timeout=60000)
            self.pages[tool] = p
        return self.pages[tool]

    def render(self, tool, cfg, out_mp4, last_png=None, fps=FPS, quality=0.95):
        p = self.page(tool)
        info = p.evaluate("c => window.loadCfg(c)", cfg)
        dur = float(info["duration"])
        n = max(1, int(round(dur * fps)))
        os.makedirs(os.path.dirname(os.path.abspath(out_mp4)), exist_ok=True)
        ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(fps), "-i", "-",
                               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "17", "-r", str(fps), out_mp4],
                              stdin=subprocess.PIPE)
        last = None
        for i in range(n):
            last = base64.b64decode(p.evaluate("([t, q]) => window.frameAt(t, q)", [min(i / fps, dur - 1e-3), quality]).split(",", 1)[1])
            ff.stdin.write(last)
        ff.stdin.close()
        if ff.wait() != 0:
            raise RuntimeError("ffmpeg の書き出しに失敗しました")
        if last_png and last:
            open(last_png, "wb").write(last)
        return info

    def __exit__(self, *a):
        self.browser.close()
        self.pw.stop()
        self.srv.shutdown()


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    with Renderer() as r:
        info = r.render(sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8")), sys.argv[3],
                        sys.argv[4] if len(sys.argv) > 4 else None)
    print("書き出し完了:", sys.argv[3], f"（{info['duration']:.1f}秒）")
