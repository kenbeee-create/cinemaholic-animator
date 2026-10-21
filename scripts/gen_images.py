"""素材画像を、画像生成API（OpenAI）で順番に作るスクリプト。

assets/keyvisual/PROMPTS.md の ①〜⑤ をそのまま使い、前の結果を次の参考画像にして進める。

使い方：
    python3 scripts/gen_images.py keyvisual      # ① 完成図（候補を3枚）
    python3 scripts/gen_images.py room           # ② 2人がいない部屋（①で選んだ完成図から）
    python3 scripts/gen_images.py chars          # ③④ ごんべぇだけ・じょんどぅーだけ（透過背景）
    python3 scripts/gen_images.py expressions    # ⑤ 表情の差分（最低限の6枚ずつ）

必要なもの：
    - 環境変数 OPENAI_API_KEY（クラウド環境のシークレットに置く。絶対にコミットしない）
    - この作業環境から api.openai.com への通信が許可されていること（環境のネットワーク設定）
    - 任意：IMAGE_MODEL（既定 gpt-image-1）

できた画像は assets/keyvisual/out/ に置かれる。採用する絵は人間が選び、
assets/keyvisual/keyvisual.png などの決まった名前で保存してから次の段階に進む。
"""
from __future__ import annotations

import base64
import json
import os
import re
import sys
import urllib.request
import uuid

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PROMPTS = os.path.join(ROOT, "assets/keyvisual/PROMPTS.md")
OUT = os.path.join(ROOT, "assets/keyvisual/out")
MODEL = os.environ.get("IMAGE_MODEL", "gpt-image-1")
SIZE = "1024x1536"  # 縦長（2:3）。9:16 へは合成時に上下を足す／切る

REF_GONBE = "assets/characters/gonbe/gonbe_base.png"
REF_JOHNDOE = "assets/characters/johndoe/johndoe_base.png"
REF_ROOM = "assets/backgrounds/johndoe_room_v1.png"
KEYVISUAL = "assets/keyvisual/keyvisual.png"
GONBE_SIT = "assets/characters/gonbe/sit_source.png"
JOHNDOE_SIT = "assets/characters/johndoe/sit_source.png"


def prompt_blocks() -> dict[str, str]:
    """PROMPTS.md から ①〜④ の英文プロンプトを取り出す。"""
    text = open(PROMPTS, encoding="utf-8").read()
    out = {}
    for mark in "①②③④⑤":
        m = re.search(rf"^## {mark}.*?```\n(.*?)```", text, re.S | re.M)
        if m:
            out[mark] = m.group(1).strip()
    return out


def expression_rows() -> list[tuple[str, str, str]]:
    """⑤ の表から（番号, 場所, 指示）を取り出す。"""
    text = open(PROMPTS, encoding="utf-8").read()
    rows = re.findall(r"^\| (目\d|口\d) \| (EYES|MOUTH) \| ([^|]+?) \|", text, re.M)
    return [(n, p, re.sub(r"（.*?）", "", d).strip()) for n, p, d in rows]


def call_edit(prompt: str, images: list[str], n: int = 1, background: str | None = None) -> list[bytes]:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("OPENAI_API_KEY がありません（クラウド環境のシークレットに登録してください）")
    boundary = uuid.uuid4().hex
    parts = []

    def field(name, value):
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())

    field("model", MODEL)
    field("prompt", prompt)
    field("size", SIZE)
    field("n", str(n))
    field("quality", "high")
    if background:
        field("background", background)
    for path in images:
        data = open(os.path.join(ROOT, path), "rb").read()
        parts.append((f'--{boundary}\r\nContent-Disposition: form-data; name="image[]"; '
                      f'filename="{os.path.basename(path)}"\r\nContent-Type: image/png\r\n\r\n').encode() + data + b"\r\n")
    parts.append(f"--{boundary}--\r\n".encode())
    req = urllib.request.Request("https://api.openai.com/v1/images/edits", data=b"".join(parts), method="POST",
                                 headers={"Authorization": f"Bearer {key}",
                                          "Content-Type": f"multipart/form-data; boundary={boundary}"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            res = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"APIエラー {e.code}: {e.read().decode(errors='ignore')[:500]}")
    except urllib.error.URLError as e:
        sys.exit(f"api.openai.com に届きません（作業環境のネットワーク設定で許可が必要）: {e}")
    return [base64.b64decode(d["b64_json"]) for d in res["data"]]


def save(blobs: list[bytes], name: str) -> list[str]:
    os.makedirs(OUT, exist_ok=True)
    paths = []
    for i, b in enumerate(blobs, 1):
        p = os.path.join(OUT, f"{name}_{i}.png" if len(blobs) > 1 else f"{name}.png")
        open(p, "wb").write(b)
        paths.append(os.path.relpath(p, ROOT))
    print("\n".join(paths))
    return paths


def need(path: str, step: str):
    if not os.path.exists(os.path.join(ROOT, path)):
        sys.exit(f"{path} がありません。先に「{step}」の候補から1枚選んで、この名前で保存してください。")


def main(stage: str):
    P = prompt_blocks()
    if stage == "keyvisual":
        save(call_edit(P["①"], [REF_GONBE, REF_JOHNDOE, REF_ROOM], n=3), "keyvisual_candidate")
    elif stage == "room":
        need(KEYVISUAL, "keyvisual")
        save(call_edit(P["②"], [KEYVISUAL], n=2), "room_base_candidate")
    elif stage == "chars":
        need(KEYVISUAL, "keyvisual")
        transparent = "Use a fully transparent background instead of green."
        save(call_edit(P["③"] + "\n" + transparent, [KEYVISUAL, REF_GONBE], n=2, background="transparent"),
             "gonbe_sit_candidate")
        save(call_edit(P["④"] + "\n" + transparent, [KEYVISUAL, REF_JOHNDOE], n=2, background="transparent"),
             "johndoe_sit_candidate")
    elif stage == "expressions":
        minimum = {"目2", "目3", "目4", "目7", "口2", "口3"}
        for cid, src in (("gonbe", GONBE_SIT), ("johndoe", JOHNDOE_SIT)):
            need(src, "chars")
            for num, place, desc in expression_rows():
                if num not in minimum:
                    continue
                prompt = (f"Edit the attached image. Change ONLY the {place} to: {desc}.\n"
                          "Keep everything else pixel-identical: same pose, same position, same size, same colors, "
                          "same transparent background.")
                save(call_edit(prompt, [src], n=1, background="transparent"), f"{cid}_{num}")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "")
