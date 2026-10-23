"""1話ぶんの場面をつないで、音（効果音・BGM・声）を乗せた1本の動画にする。

使い方：
    python3 renderer/assemble.py episodes/epXX-<slug>/episode.json [出力.mp4]          … 本番（1080×1920・30fps）
    python3 renderer/assemble.py episodes/epXX-<slug>/episode.json --draft              … 下書き（540×960・15fps・「下書き」の透かし）

下書きは「テンポ・間・カメラ・字幕」を確かめるためのもの（docs/production-flow.md の段階2）。速く書き出せる。
どちらも、前回から変わっていない場面は書き出し直さずに使い回す（設定・道具・素材のどれかが変わった場面だけ作り直す）。

episode.json の形（パスは episode.json からの相対パスか、リポジトリからのパス）：
{
  "segments": [
    {"tool": "chat-maker",        "cfg": "chat.json"},
    {"tool": "title",             "cfg": "title.json"},
    {"tool": "studio",            "cfg": "scene_a.json"},
    {"tool": "movie-card-maker",  "cfg": "movie.json"},
    {"tool": "card-maker",        "cfg": {"type": "quote", ...}},   ← 中に直接書いてもよい
  ],
  "bgm": {"file": "bgm/lofi_loop.wav", "db": -20},
  "voice": "voice.wav"        ← 任意。あれば重ね、BGMを声の下で小さくする
}

音の探し方：assets/sound/<名前>.wav があればそれ（本番素材）、無ければ assets/sound/placeholder/<名前>.wav（仮）。
最後に音量を -14 LUFS にそろえる（docs/quality-bar.md）。
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import subprocess
import sys
import wave

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "renderer/templates"))
from web_render import Renderer  # noqa: E402

SR = 44100


def resolve(base_dir, p):
    if isinstance(p, dict):
        return p
    for cand in (os.path.join(base_dir, p), os.path.join(ROOT, p)):
        if os.path.exists(cand):
            return json.load(open(cand, encoding="utf-8"))
    raise FileNotFoundError(p)


def sound_path(name):
    for base in ("assets/sound", "assets/sound/placeholder"):
        for ext in (".wav", ".mp3"):
            p = os.path.join(ROOT, base, name + ext)
            if os.path.exists(p):
                return p
    return None


def read_audio(path):
    """どんな音声ファイルも 44.1kHz・ステレオの配列にする（ffmpeg で変換）。"""
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, "<i2").reshape(-1, 2).astype(np.float32) / 32768


def write_wav(path, y):
    y = np.clip(y, -1, 1)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((y * 32767).astype("<i2").tobytes())


def assets_stamp():
    """素材（キャラ・背景・記号・小物・UI）が変わったかを見分けるための印。"""
    h = hashlib.sha1()
    for d in ("assets/characters", "assets/backgrounds", "assets/fx", "assets/props", "assets/ui"):
        for f in sorted(glob.glob(os.path.join(ROOT, d, "**", "*.png"), recursive=True) +
                        glob.glob(os.path.join(ROOT, d, "**", "*.json"), recursive=True)):
            h.update(f.encode())
            h.update(str(os.path.getmtime(f)).encode())
    return h.hexdigest()


def seg_key(tool, cfg, fps, stamp):
    h = hashlib.sha1()
    h.update(json.dumps([tool, cfg, fps, stamp], sort_keys=True, ensure_ascii=False).encode())
    for f in (f"tools/{tool}/index.html", "renderer/templates/title.py", "renderer/templates/style.py") if tool == "title" else (f"tools/{tool}/index.html",):
        p = os.path.join(ROOT, f)
        if os.path.exists(p):
            h.update(open(p, "rb").read())
    return h.hexdigest()


def render_title(cfg, out_dir):
    import title as title_tpl
    p = os.path.join(out_dir, "title_cfg.json")
    json.dump(cfg, open(p, "w"), ensure_ascii=False)
    title_tpl.render(p, out_dir)
    return os.path.join(out_dir, "title.mp4"), json.load(open(os.path.join(out_dir, "cues.json")))


class LazyRenderer:
    """ブラウザは、本当に書き出す場面が出てきたときだけ開く（全部使い回せるときは開かない）。"""

    def __init__(self):
        self.r = None

    def render(self, *a, **k):
        if self.r is None:
            self.r = Renderer().__enter__()
        return self.r.render(*a, **k)

    def close(self):
        if self.r:
            self.r.__exit__(None, None, None)


def main(ep_path, out=None, draft=False):
    ep = json.load(open(ep_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(ep_path))
    slug = os.path.basename(base)
    work = os.path.join(ROOT, "output", slug, "segments_draft" if draft else "segments")
    os.makedirs(work, exist_ok=True)
    out = out or os.path.join(ROOT, "output", slug, f"{slug}{'_draft' if draft else ''}.mp4")
    fps = 15 if draft else 30
    stamp = assets_stamp()

    clips, cues, t0 = [], [], 0.0
    reused = 0
    r = LazyRenderer()
    try:
        for i, seg in enumerate(ep["segments"]):
            cfg = resolve(base, seg["cfg"])
            mp4 = os.path.join(work, f"{i:02d}_{seg['tool']}.mp4")
            key = seg_key(seg["tool"], cfg, fps, stamp)
            meta_p = mp4 + ".json"
            meta = json.load(open(meta_p)) if os.path.exists(meta_p) and os.path.exists(mp4) else {}
            if meta.get("key") == key:
                info = meta["info"]
                reused += 1
                print(f"  {i + 1}/{len(ep['segments'])} {seg['tool']}（{float(info['duration']):.1f}秒）… 変更なし・使い回し")
            else:
                if seg["tool"] == "title":
                    d = os.path.join(work, f"{i:02d}_title")
                    os.makedirs(d, exist_ok=True)
                    src, info = render_title(cfg, d)
                    os.replace(src, mp4)
                else:
                    info = r.render(seg["tool"], cfg, mp4, fps=fps, quality=0.8 if draft else 0.95)
                json.dump({"key": key, "info": info}, open(meta_p, "w"), ensure_ascii=False)
                print(f"  {i + 1}/{len(ep['segments'])} {seg['tool']}（{float(info['duration']):.1f}秒）… 書き出し")
            dur = float(info["duration"])
            for c in info.get("cues", []):
                if c.get("sfx"):
                    cues.append((t0 + float(c["t"]), c["sfx"]))
            for c in seg.get("sfx", []):  # episode.json 側で足す効果音
                cues.append((t0 + float(c["t"]), c["sfx"]))
            clips.append((mp4, dur))
            t0 += dur
    finally:
        r.close()
    print(f"  使い回し {reused} / {len(clips)} 場面")

    # 映像をつなぐ（下書きは、小さくして「下書き」の透かしを入れる）
    lst = os.path.join(work, "concat.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p, _ in clips))
    video = os.path.join(work, "video.mp4")
    if draft:
        font = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
        vf = (f"fps={fps},scale=540:960,drawtext=fontfile={font}:text='下書き':fontsize=30:fontcolor=white@0.85:"
              f"box=1:boxcolor=black@0.45:boxborderw=8:x=14:y=14,"
              f"drawtext=fontfile={font}:text='%{{pts\\:hms}}':fontsize=24:fontcolor=white@0.85:box=1:boxcolor=black@0.45:boxborderw=6:x=w-tw-14:y=14")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-vf", vf,
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "26", "-pix_fmt", "yuv420p", video], check=True)
    else:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video], check=True)
    total = t0

    # 音をつくる
    n = int(total * SR) + SR
    mixbuf = np.zeros((n, 2), np.float32)
    voice = None
    if ep.get("voice"):
        vp = os.path.join(base, ep["voice"])
        if os.path.exists(vp):
            voice = read_audio(vp)[:n]
            mixbuf[:len(voice)] += voice
    b = ep.get("bgm")
    if b:
        bp = sound_path(os.path.splitext(b["file"])[0])
        if bp:
            loop = read_audio(bp)
            reps = int(np.ceil(n / len(loop)))
            bgm = np.tile(loop, (reps, 1))[:n] * (10 ** (b.get("db", -20) / 20))
            fade = int(1.5 * SR)
            end = int(total * SR)
            bgm[end - fade:end] *= np.linspace(1, 0, fade)[:, None]
            bgm[end:] = 0
            bgm[:int(.3 * SR)] *= np.linspace(0, 1, int(.3 * SR))[:, None]
            if voice is not None:  # 声の下でBGMを小さく（ダッキング）
                envv = np.convolve(np.abs(voice).mean(1), np.ones(4410) / 4410, "same")
                duck = 1 - 0.55 * np.clip(envv / (envv.max() + 1e-9) * 4, 0, 1)
                bgm[:len(duck)] *= duck[:, None]
            mixbuf += bgm
    missing = set()
    for tt, name in cues:
        p = sound_path(name)
        if not p:
            missing.add(name)
            continue
        s = read_audio(p) * 0.8
        i = int(tt * SR)
        s = s[: max(0, n - i)]
        mixbuf[i:i + len(s)] += s
    audio = os.path.join(work, "audio.wav")
    write_wav(audio, mixbuf[: int(total * SR)])

    # 音量を -14 LUFS にそろえる（1回目で測って、2回目でぴったり合わせる）
    pre = "acompressor=threshold=-20dB:ratio=3:attack=5:release=150:makeup=2,alimiter=limit=0.8:level=false,"
    meas = subprocess.run(["ffmpeg", "-hide_banner", "-i", audio, "-af", pre + "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json",
                           "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(meas[meas.rindex("{"):meas.rindex("}") + 1])
    af = pre + (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", audio, "-c:v", "copy", "-af", af,
                    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-shortest", out], check=True)
    if missing:
        print("見つからなかった音：", ", ".join(sorted(missing)))
    print(f"書き出し完了: {out}（{total:.1f}秒）")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        sys.exit(1)
    main(args[0], args[1] if len(args) > 1 else None, draft="--draft" in sys.argv)
