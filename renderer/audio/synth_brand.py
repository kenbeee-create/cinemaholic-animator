"""シネマホリックの音（ブランド音・効果音・BGM）を、プログラムで一から作る（自作なので権利の心配がない）。

使い方：
    python3 renderer/audio/synth_brand.py
出力：assets/sound/（仮の音 assets/sound/placeholder/ より優先して使われる）
    brand/chat_receive.wav  通知音（やわらかい2音の「ポロン」）
    brand/chat_send.wav     送信音（短い「シュッ」）
    brand/pill_clink.wav    錠剤「カラン」（カプセルが2回はねる）
    brand/low_hit.wav       低音「ジャン」（映画の予告のような深いドン）
    brand/stamp.wav         はんこ「ドン」（紙に押す重い音）
    sfx/pop.wav             ポン（テロップ・記号）
    sfx/whoosh.wav          シュッ（場面の切り替え）
    sfx/typing.wav          タイプ音
    bgm/lofi_loop.wav       暗めのLo-fi（BPM 76・8小節のループ・つなぎ目なし）
気に入らない音は、同じ名前の本番素材を置けば差し替わる。
"""
from __future__ import annotations

import os
import wave

import numpy as np
from scipy import signal

SR = 44100
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "assets/sound")
R = np.random.default_rng(11)


def tt(d):
    return np.arange(int(SR * d)) / SR


def adsr(n, a=0.005, d=0.1, s=0.0, r=0.1):
    x = np.arange(n) / SR
    e = np.where(x < a, x / a, s + (1 - s) * np.exp(-(x - a) / d))
    tail = int(r * SR)
    if tail and tail < n:
        e[-tail:] *= np.linspace(1, 0, tail)
    return e


def lp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def hp(x, f, order=2):
    b, a = signal.butter(order, f / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def bp(x, f1, f2, order=2):
    b, a = signal.butter(order, [f1 / (SR / 2), f2 / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def reverb(x, size=0.35, mix=0.25):
    """短い部屋の響き（遅延の重ね合わせ）。"""
    y = x.copy()
    for k, (d, g) in enumerate([(0.029, .5), (0.037, .45), (0.041, .42), (0.053, .38), (0.067, .3), (0.083, .25)]):
        n = int(d * SR * (1 + size))
        z = np.zeros_like(x)
        z[n:] = x[:-n] * g
        for _ in range(3):
            z2 = np.zeros_like(z)
            z2[n:] = z[:-n] * g
            z = z + z2
        y = y + lp(z, 4000) * mix / 3
    return y


def stereo(x, width=0.0):
    if width == 0:
        return np.stack([x, x], 1)
    d = int(0.012 * SR)
    r = np.concatenate([np.zeros(d), x[:-d]])
    return np.stack([x * (1 - width * .3) + r * width * .3, r * (1 - width * .3) + x * width * .3], 1)


def save(name, y, peak=0.89):
    if y.ndim == 1:
        y = stereo(y)
    y = y / (np.abs(y).max() + 1e-9) * peak
    p = os.path.join(OUT, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with wave.open(p, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((y * 32767).astype("<i2").tobytes())
    print("書き出し:", os.path.relpath(p, ROOT), f"{len(y) / SR:.2f}秒")


# ---------------- 音色 ----------------
def bell(f, d, bright=1.0):
    """やわらかい鉄琴（FM）。"""
    x = tt(d)
    mod = np.sin(2 * np.pi * f * 3.5 * x) * 1.6 * bright * np.exp(-x * 9)
    return np.sin(2 * np.pi * f * x + mod) * adsr(len(x), .002, d * .35)


def rhodes(f, d):
    """エレピ（ローズ）ふうの和音の1音。"""
    x = tt(d)
    mod = np.sin(2 * np.pi * f * x) * 1.1 * np.exp(-x * 3)
    tone = np.sin(2 * np.pi * f * x + mod) + 0.25 * np.sin(2 * np.pi * 2 * f * x) * np.exp(-x * 5)
    trem = 1 + 0.12 * np.sin(2 * np.pi * 4.2 * x)
    return tone * trem * adsr(len(x), .01, d * .6, .25, .25)


def kick(d=0.45):
    x = tt(d)
    f = 45 + 90 * np.exp(-x * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-x * 7) + 0.3 * lp(R.normal(size=len(x)), 1500) * np.exp(-x * 120)


def snare(d=0.3):
    x = tt(d)
    n = bp(R.normal(size=len(x)), 1200, 6000) * np.exp(-x * 18)
    tone = np.sin(2 * np.pi * 190 * x) * np.exp(-x * 25)
    return 0.8 * n + 0.5 * tone


def hat(d=0.06, open_=False):
    x = tt(d if not open_ else 0.25)
    return hp(R.normal(size=len(x)), 7000) * np.exp(-x * (60 if not open_ else 14))


# ---------------- ブランド音・効果音 ----------------
def chat_receive():
    y = np.zeros(int(SR * .7))
    for t0, f in ((0, 1046.5), (.11, 1567.98)):
        b = bell(f, .55)
        i = int(t0 * SR)
        y[i:i + len(b)] += b[:len(y) - i] * (1 if t0 == 0 else .8)
    return reverb(y, .2, .3)


def chat_send():
    x = tt(.22)
    n = R.normal(size=len(x))
    return lp(hp(n, 1500), 9000) * np.sin(np.pi * x / x[-1]) ** 2 * .6


def pill_clink():
    """カプセルが机に落ちて2回はねる「カラン」。"""
    y = np.zeros(int(SR * 1.1))
    for t0, g in ((0.0, 1.0), (0.13, .55), (0.21, .3)):
        x = tt(.5)
        tone = sum(np.sin(2 * np.pi * f * x) * a * np.exp(-x * dk)
                   for f, a, dk in ((2650, 1, 18), (4120, .6, 26), (5980, .35, 34), (7300, .2, 40)))
        click = hp(R.normal(size=len(x)), 5000) * np.exp(-x * 400) * .5
        i = int(t0 * SR)
        y[i:i + len(x)] += (tone + click) * g
    return reverb(y, .4, .35)


def low_hit():
    """映画の予告のような、深い「ジャン」。"""
    x = tt(2.4)
    f = 38 + 50 * np.exp(-x * 12)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 1.6)
    body = lp(R.normal(size=len(x)), 300) * np.exp(-x * 9) * 1.2
    metal = sum(np.sin(2 * np.pi * fr * x) * np.exp(-x * 2.2) for fr in (55, 82.4, 110.7)) * .25
    y = sub + body + metal
    y = np.tanh(y * 1.6)
    return reverb(y, .8, .45)


def stamp():
    """はんこを紙に押す「ドン」。"""
    x = tt(.6)
    thud = np.sin(2 * np.pi * np.cumsum(70 + 80 * np.exp(-x * 40)) / SR) * np.exp(-x * 14)
    slap = bp(R.normal(size=len(x)), 600, 4000) * np.exp(-x * 60) * .7
    wood = np.sin(2 * np.pi * 420 * x) * np.exp(-x * 45) * .3
    return reverb(np.tanh((thud + slap + wood) * 1.4), .3, .25)


def pop():
    x = tt(.18)
    f = 900 * np.exp(-x * 12) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 30)


def whoosh():
    x = tt(.55)
    n = R.normal(size=len(x))
    out = np.zeros_like(n)
    seg = 512
    for i in range(0, len(x) - seg, seg // 2):
        c = 300 + 5000 * np.sin(np.pi * i / len(x)) ** 2
        s = bp(n[i:i + seg], max(80, c * .6), min(18000, c * 1.6))
        out[i:i + seg] += s * np.hanning(seg)
    return out * np.sin(np.pi * x / x[-1]) ** 1.5


def typing():
    y = np.zeros(int(SR * 1.0))
    t0 = 0.0
    while t0 < .9:
        x = tt(.04)
        k = bp(R.normal(size=len(x)), 1500, 5000) * np.exp(-x * 160) * R.uniform(.5, 1)
        i = int(t0 * SR)
        y[i:i + len(x)] += k
        t0 += R.uniform(.07, .14)
    return reverb(y, .1, .15)


# ---------------- BGM ----------------
def lofi(bpm=76, bars=8):
    beat = 60 / bpm
    n = int(SR * beat * 4 * bars)
    mix = np.zeros(n)
    # 暗めの進行：Am9 → Fmaj7 → Dm9 → Esus4/E（2小節ずつ）
    chords = [[220.0, 261.63, 329.63, 392.0, 493.88], [174.61, 220.0, 261.63, 329.63, 392.0],
              [146.83, 174.61, 220.0, 261.63, 329.63], [164.81, 220.0, 246.94, 329.63, 415.30]]
    keys = np.zeros(n)
    for bar in range(bars):
        ch = chords[(bar // 2) % 4]
        for hit, ln in ((0, 2.6), (2.5, 1.4)):  # 1拍目と3拍目の裏
            st = int((bar * 4 + hit) * beat * SR)
            for k, f in enumerate(ch):
                v = rhodes(f, ln * beat) * (.22 if k else .3)
                o = st + int(k * 0.012 * SR)  # 少しずらして弾く
                e = min(n, o + len(v))
                keys[o:e] += v[:e - o]
    # ベース
    bass = np.zeros(n)
    for bar in range(bars):
        root = chords[(bar // 2) % 4][0] / 2
        for hit, ln in ((0, 1.5), (1.75, .5), (2.5, 1.2)):
            st = int((bar * 4 + hit) * beat * SR)
            x = tt(ln * beat)
            v = np.sin(2 * np.pi * root * x) * adsr(len(x), .01, .5, .5, .05)
            e = min(n, st + len(v))
            bass[st:e] += v[:e - st] * .5
    # ドラム（少しハネる）
    drums = np.zeros(n)
    swing = .06 * beat
    for bar in range(bars):
        for b8 in range(8):
            t0 = (bar * 4 + b8 / 2) * beat + (swing if b8 % 2 else 0) + R.normal(0, .004)
            i = int(t0 * SR)
            parts = [hat() * (.28 if b8 % 2 else .2)]
            if b8 in (0, 5) or (b8 == 3 and bar % 2):
                parts.append(kick() * .9)
            if b8 in (2, 6):
                parts.append(snare() * .45)
            for p in parts:
                e = min(n, i + len(p))
                drums[i:e] += p[:e - i]
    drums = lp(drums, 7000)
    mix = keys * .9 + bass * .8 + drums * .7
    # テープの揺れ（ごくわずかなピッチのゆらぎ）と、こもり
    wob = (np.sin(2 * np.pi * .35 * np.arange(n) / SR) * .0006 * SR).astype(int)
    idx = np.clip(np.arange(n) + wob, 0, n - 1)
    mix = lp(mix[idx], 5200)
    # レコードのノイズ
    crackle = np.zeros(n)
    pos = R.integers(0, n, size=int(bars * 4 * beat * 9))
    crackle[pos] = R.uniform(-1, 1, size=len(pos))
    crackle = hp(crackle, 2000) * .25 + lp(R.normal(size=n), 900) * .012
    mix = mix + crackle
    mix = reverb(mix, .5, .3)
    # つなぎ目をなめらかに（最後の少しを頭に重ねる）
    f = int(.08 * SR)
    mix[:f] = mix[:f] * np.linspace(0, 1, f) + mix[-f:] * np.linspace(1, 0, f)
    mix = mix[:-f]
    return stereo(mix, .6)


if __name__ == "__main__":
    save("brand/chat_receive.wav", chat_receive())
    save("brand/chat_send.wav", chat_send(), .6)
    save("brand/pill_clink.wav", pill_clink())
    save("brand/low_hit.wav", low_hit())
    save("brand/stamp.wav", stamp())
    save("sfx/pop.wav", pop(), .7)
    save("sfx/whoosh.wav", whoosh(), .7)
    save("sfx/typing.wav", typing(), .6)
    save("bgm/lofi_loop.wav", lofi(), .8)
