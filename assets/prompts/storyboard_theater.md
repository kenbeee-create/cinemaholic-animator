# 絵コンテ用プロンプト：新作予習（映画館）エモーショナル版

ChatGPTで**イメージ絵コンテ**（1コマずつの絵）を作るためのプロンプト。**新しいチャット**で、最初に `keyvisual.png` と `gonbe/sit_source.png`・`johndoe/sit_source.png` の3枚を添付してから「共通の前置き」を送り、そのあと①から順に1つずつ送る。
スクリーンには**本物の映画・予告は描かない**（光と色、またはオリジナルのモチーフだけ）。

## エモーションの作り方（このシリーズの決まり）
| 要素 | やり方 |
|---|---|
| 光 | 部屋は暗く、光源は**スクリーンだけ**。光が顔と毛の輪郭に当たり、背中側は闇に沈む |
| 色 | 1コマに主役の色は2つまで（スクリーンの色＋暗い赤茶）。気持ちが動くコマだけ色が変わる |
| 構図 | 2人を画面の下3分の1に小さく置き、上に大きな空間（光・闇）を残す。孤独と期待が同時に出る |
| 間 | 何も起きないコマ（光の粒が漂うだけ・ポップコーンを持つ手が止まる）を必ず1つ入れる |
| 顔 | 正面からのアップは1回だけ（スクリーン側から2人の顔を見る「切り返し」）。ここが山場 |

## 共通の前置き（最初に1回だけ送る）
```
You will draw storyboard frames for a short anime-style video, one frame per message, all in ONE consistent look.
Characters (exactly as in the attached images): Gonbe — brown floppy-eared dog, dark-brown knit beanie (always on), red hoodie, navy pants, sleepy half-closed bored eyes (never wide, never teary). Johndoe — round fluffy black dog whose curly fur COMPLETELY hides his eyes, plain cream T-shirt, grey shorts.
Look: the same flat 2D cartoon style and bold dark outlines as the attached key visual, but CINEMATIC and EMOTIONAL: a dark old movie theater lit ONLY by the screen; soft colored light from the screen spills onto their fur and rims their outlines; deep shadows; visible dust floating in the projector beam; quiet, lonely-but-warm mood, like a late weeknight show with almost nobody there.
Rules: vertical 9:16. The screen NEVER shows a real movie, real characters, logos or text — only soft blurry colored light or simple original abstract shapes. No text or letters anywhere in the image. Keep the characters' designs identical in every frame.
Reply "OK" and wait for frame 1.
```

## ① 0–2秒 フック：ほぼ誰もいない映画館
```
Frame 1. Wide shot from the back of the theater, high and far. Rows of empty dark-red seats. Only Gonbe and Johndoe sit in the middle of the room, small in the lower third of the frame, seen from behind. The big screen glows deep magenta and cyan, filling the top half with light; a long projector beam cuts diagonally through the dark with floating dust. Their outlines glow faintly in the screen color. Mood: two people alone in a huge dark room, about to see something.
```

## ② 2–4秒 後ろ姿に寄る：ささやく
```
Frame 2. Medium shot from directly behind their seats, at head height. Gonbe leans his head toward Johndoe, whispering; Johndoe's big fluffy head tilts slightly to listen. Between them a striped popcorn bucket on the armrest catches the light. The screen beyond them is a soft out-of-focus wash of warm orange. Strong rim light on the fur edges of both heads, faces unseen.
```

## ③ 4–6秒 光の中：スクリーンの色が変わる瞬間
```
Frame 3. Over-the-shoulder shot from behind Gonbe's left shoulder (the back of his beanie and ear soft and dark in the foreground). The screen fills most of the frame: blurry original abstract shapes suggesting a rainy neon city at night (pink and blue blobs, vertical streaks of light, no buildings in detail, no text). The colored light just changed and floods over Gonbe's ear and beanie. Projector dust sparkles.
```

## ④ 6–8秒 間：何も起きないコマ
```
Frame 4. Extreme close-up of Gonbe's paw holding a single piece of popcorn, frozen halfway to his mouth, lit only by flickering blue screen light. Everything else is soft darkness. A quiet, suspended moment.
```

## ⑤ 8–11秒 山場：スクリーン側からの切り返し
```
Frame 5. Reverse shot from the screen's point of view looking back at the audience. Gonbe and Johndoe sit side by side facing us in the dark seats, their faces fully washed in soft glowing screen light (warm gold fading to blue). Gonbe keeps his usual sleepy half-closed eyes, but his brows lift slightly and his mouth is slightly open in quiet wonder; the screen light reflects as a tiny highlight in his pupils. Johndoe's fur glows at the edges, mouth slightly open. Empty seats fade into darkness behind them. This is the emotional peak: two people quietly moved.
```

## ⑥ 11–13秒 じょんどぅーの横顔
```
Frame 6. Side profile close-up of Johndoe in the dark, facing right toward the screen. The screen light draws a thin bright line along the curls of his fur, the tip of his nose and his small mouth. Behind him, out of focus, Gonbe's beanie silhouette. Calm, knowing mood, as if he has seen this many times and still loves it.
```

## ⑦ 13–16秒 余韻：エンドロールの光
```
Frame 7. Wide shot from behind again, the same angle as frame 1 but closer. The screen is now nearly dark with thin white vertical lines of light slowly scrolling (like end credits, but no readable text). The theater is darker; the two silhouettes sit still, not leaving yet. A single soft beam from the projector. Bittersweet, quiet.
```

## ⑧ 16–20秒 外へ：夜の街
```
Frame 8. Outside the old cinema at night after the show. Light rain, wet street reflecting the warm marquee lights (the marquee has no letters, just glowing bulbs). Gonbe and Johndoe walk away side by side under one plain umbrella, seen from behind, small in the frame. Gonbe's red hoodie is the only strong color. Lonely streets but they are together.
```

## うまくいかないとき（貼り足す一文）
- スクリーンに映画の場面や文字が出た → `The screen must show only blurry colored light, no images, no text.`
- ごんべぇの目が大きく・うるうるになった → `Keep Gonbe's eyes sleepy and half-closed, exactly like the reference.`
- じょんどぅーの目が見えた → `Johndoe's eyes must stay completely hidden by his fur.`
- 明るすぎる → `Make it much darker; the only light source is the screen.`
- 絵柄がリアルになった → `Keep the flat 2D cartoon style with bold outlines from the key visual.`

## できたら
8枚をClaudeに送る（名前は `sb_theater_01.png` 〜 `08.png`。違っていても大丈夫）。セリフ・秒数・カメラの動きを書き込んだ絵コンテのシートにまとめ、そのまま下書き動画にする。
