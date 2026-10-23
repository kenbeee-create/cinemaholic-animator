"""1話ぶんの場面をつないで、音（効果音・BGM・声）を乗せた1本の動画にする。

使い方：
    python3 renderer/assemble.py episodes/epXX-<slug>/episode.json [出力.mp4]

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


def render_title(cfg, out_dir):
    import title as title_tpl
    p = os.path.join(out_dir, "title_cfg.json")
    json.dump(cfg, open(p, "w"), ensure_ascii=False)
    title_tpl.render(p, out_dir)
    return os.path.join(out_dir, "title.mp4"), json.load(open(os.path.join(out_dir, "cues.json")))


def main(ep_path, out=None):
    ep = json.load(open(ep_path, encoding="utf-8"))
    base = os.path.dirname(os.path.abspath(ep_path))
    slug = os.path.basename(base)
    work = os.path.join(ROOT, "output", slug, "segments")
    os.makedirs(work, exist_ok=True)
    out = out or os.path.join(ROOT, "output", slug, f"{slug}.mp4")

    clips, cues, t0 = [], [], 0.0
    with Renderer() as r:
        for i, seg in enumerate(ep["segments"]):
            cfg = resolve(base, seg["cfg"])
            mp4 = os.path.join(work, f"{i:02d}_{seg['tool']}.mp4")
            if seg["tool"] == "title":
                d = os.path.join(work, f"{i:02d}_title")
                os.makedirs(d, exist_ok=True)
                src, info = render_title(cfg, d)
                os.replace(src, mp4)
            else:
                info = r.render(seg["tool"], cfg, mp4)
            dur = float(info["duration"])
            for c in info.get("cues", []):
                if c.get("sfx"):
                    cues.append((t0 + float(c["t"]), c["sfx"]))
            for c in seg.get("sfx", []):  # episode.json 側で足す効果音
                cues.append((t0 + float(c["t"]), c["sfx"]))
            clips.append((mp4, dur))
            print(f"  {i + 1}/{len(ep['segments'])} {seg['tool']}（{dur:.1f}秒）")
            t0 += dur

    # 映像をつなぐ
    lst = os.path.join(work, "concat.txt")
    open(lst, "w").write("".join(f"file '{p}'\n" for p, _ in clips))
    video = os.path.join(work, "video.mp4")
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
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
