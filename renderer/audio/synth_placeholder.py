"""仮の効果音とBGMを、プログラムで合成して作る（本番の音素材が届くまでの代わり）。

使い方：
    python3 renderer/audio/synth_placeholder.py
出力：assets/sound/placeholder/
    brand/chat_receive.wav  通知音（ポロン）
    brand/chat_send.wav     送信音（シュッ）
    brand/pill_clink.wav    錠剤（カラン）
    brand/low_hit.wav       低音（ジャン）
    brand/stamp.wav         はんこ（ドン）
    sfx/pop.wav             ポン
    sfx/typing.wav          タイプ音（1秒）
    sfx/whoosh.wav          シュッ（画面切り替え）
    bgm/lofi_loop.wav       暗めのLo-fiのループ（約17秒）
本番の素材を assets/sound/brand/ などに同じ名前で置くと、そちらが優先される（renderer/assemble.py）。
"""
from __future__ import annotations

import os
import wave

import numpy as np

SR = 44100
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets/sound/placeholder")
rng = np.random.default_rng(7)


def t(d):
    return np.arange(int(SR * d)) / SR


def env(n, a=0.005, r=0.2, sustain=0.0):
    x = np.arange(n) / SR
    e = np.minimum(1, x / max(a, 1e-4)) * np.exp(-np.maximum(0, x - a) / max(r, 1e-4))
    return e


def save(path, y, gain=0.9):
    y = np.asarray(y, float)
    if y.ndim == 1:
        y = np.stack([y, y], 1)
    peak = np.abs(y).max() or 1
    y = y / peak * gain
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((y * 32767).astype("<i2").tobytes())


def tone(f, d, r=0.25, a=0.004, harm=(1, 0.3, 0.12)):
    x = t(d)
    y = sum(h * np.sin(2 * np.pi * f * (k + 1) * x) for k, h in enumerate(harm))
    return y * env(len(x), a, r)


def noise(d):
    return rng.standard_normal(int(SR * d))


def lowpass(y, cut):
    # 1次のローパス
    a = np.exp(-2 * np.pi * cut / SR)
    out = np.zeros_like(y)
    acc = 0.0
    for i, v in enumerate(y):
        acc = (1 - a) * v + a * acc
        out[i] = acc
    return out


def mix(*parts, d=None):
    n = max(len(p[1]) + int(p[0] * SR) for p in parts) if d is None else int(d * SR)
    y = np.zeros(n)
    for off, s in parts:
        i = int(off * SR)
        s = s[: max(0, n - i)]
        y[i:i + len(s)] += s
    return y


def main():
    b = os.path.join(OUT, "brand")
    s = os.path.join(OUT, "sfx")
    # 通知音：2音のやわらかいチャイム
    save(f"{b}/chat_receive.wav", mix((0, tone(1318, .35, .18)), (.09, tone(1760, .45, .22))), .6)
    # 送信音：短い上向きのシュッ
    x = t(.18)
    sw = np.sin(2 * np.pi * np.cumsum(np.linspace(700, 1500, len(x))) / SR) * env(len(x), .005, .06)
    save(f"{b}/chat_send.wav", sw, .45)
    # 錠剤：小さな硬い物が2回はねる（金属っぽい高い成分）
    def clink(dd=.25):
        return sum(tone(f, dd, .06, .001, (1,)) * g for f, g in [(3100, 1), (4870, .6), (6720, .35)])
    save(f"{b}/pill_clink.wav", mix((0, clink()), (.11, clink() * .55), (.19, clink() * .25)), .7)
    # 低音：サブのドーン＋少し歪んだ倍音
    x = t(1.4)
    f = 55 * np.exp(-x * 0.6)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(x), .004, .55)
    boom += 0.25 * np.tanh(3 * boom)
    save(f"{b}/low_hit.wav", boom + .15 * lowpass(noise(1.4), 300) * env(len(x), .001, .08), .95)
    # はんこ：ドン（低い打撃＋紙の音）
    x = t(.5)
    thump = np.sin(2 * np.pi * np.cumsum(140 * np.exp(-x * 9)) / SR) * env(len(x), .002, .09)
    paper = lowpass(noise(.5), 2500) * env(len(x), .001, .03)
    save(f"{b}/stamp.wav", thump + .5 * paper, .9)
    # ポン
    x = t(.2)
    pop = np.sin(2 * np.pi * np.cumsum(np.linspace(900, 420, len(x))) / SR) * env(len(x), .002, .05)
    save(f"{s}/pop.wav", pop, .6)
    # タイプ音：不規則なカチカチ（1秒）
    y = np.zeros(SR)
    k = 0.0
    while k < .95:
        c = lowpass(noise(.03), 4000) * env(int(.03 * SR), .0005, .008)
        i = int(k * SR)
        y[i:i + len(c)] += c[: len(y) - i]
        k += rng.uniform(.06, .13)
    save(f"{s}/typing.wav", y, .45)
    # シュッ（画面切り替え）
    x = t(.35)
    wh = lowpass(noise(.35), 1800) * np.sin(np.pi * x / .35) ** 2
    save(f"{s}/whoosh.wav", wh, .4)

    # ---- BGM：暗めのLo-fi（Am7 - Fmaj7 - Dm7 - E7、70BPM、4小節ループ） ----
    bpm = 70
    beat = 60 / bpm
    bars = 4
    dur = bars * 4 * beat
    n = int(dur * SR)
    y = np.zeros(n)
    chords = [[57, 60, 64, 67], [53, 57, 60, 64], [50, 53, 57, 60], [52, 56, 59, 62]]
    mtof = lambda m: 440 * 2 ** ((m - 69) / 12)
    for bi, ch in enumerate(chords):
        st = bi * 4 * beat
        for m in ch:  # エレピ風のやわらかいコード
            note = tone(mtof(m), 4 * beat, 1.6, .02, (1, .25, .08)) * .16
            i = int(st * SR)
            y[i:i + len(note)] += note[: n - i]
        bass = tone(mtof(ch[0] - 12), 2 * beat, .8, .01, (1, .4)) * .5
        for k in (0, 2):
            i = int((st + k * beat) * SR)
            y[i:i + len(bass)] += bass[: n - i]
    # ドラム：キック・スネア（ブラシ風）・ハイハット、少しずらしてゆるく
    for bt in range(bars * 4):
        tt = bt * beat
        if bt % 4 in (0, 2) or bt % 8 == 7:
            x = t(.35)
            k = np.sin(2 * np.pi * np.cumsum(90 * np.exp(-x * 14)) / SR) * env(len(x), .002, .12) * .8
            i = int(tt * SR)
            y[i:i + len(k)] += k[: n - i]
        if bt % 4 in (1, 3):
            sn = lowpass(noise(.25), 3000) * env(int(.25 * SR), .002, .07) * .25
            i = int((tt + .015) * SR)
            y[i:i + len(sn)] += sn[: n - i]
        for h in (0, .5):
            hh = (noise(.05) - lowpass(noise(.05), 6000)) * env(int(.05 * SR), .001, .015) * .08
            i = int((tt + h * beat + (.02 if h else 0)) * SR)
            y[i:i + len(hh)] += hh[: n - i]
    # レコードのノイズ
    crackle = np.zeros(n)
    idx = rng.integers(0, n, 260)
    crackle[idx] = rng.uniform(-.25, .25, len(idx))
    y += lowpass(crackle, 3000) + lowpass(noise(dur), 1200) * .006
    y = lowpass(y, 5200)  # こもらせる
    save(os.path.join(OUT, "bgm", "lofi_loop.wav"), y, .7)
    print("書き出し完了:", OUT)


if __name__ == "__main__":
    main()
