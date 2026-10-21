# 素材生成プロンプト（完成図 → 部屋 → キャラ → 表情）

Gemini か ChatGPT の画像生成で使う。**上から順番に**作る（前の絵を次の参考画像にするため）。
できた画像はそのままチャットに送ればよい。切り抜き・層分け・登録は AI がやる。

共通のコツ
- 毎回「縦長 9:16、できるだけ高解像度」を指定する
- 参考画像は、指示どおりに必ず添付する（キャラの顔がぶれないように）
- うまくいかないときは、同じ会話の中で「〇〇だけ直して」と頼む方が、作り直すより安定する
- 右下にAIのマークが入っても構わない（大事なものは右下に置かない構図にしてある）

---

## ① 完成図（いちばん大事）
**添付：** `gonbe_base.png`（ごんべぇ）・`johndoe_base.png`（じょんどぅー）・`johndoe_room_v1.png`（部屋）

```
Vertical 9:16 illustration, highest resolution.
2D flat-color cartoon, thick dark-brown outlines, American cartoon style, muted warm palette — match the style of the attached character images exactly.

Scene: a dim, cozy bedroom-living room in a family house at night (use the attached room as reference). Warm indirect light from a floor lamp. Back wall: a tall shelf packed with DVDs and books, an EMPTY vertical poster frame on the wall (no picture, no text), a small window with night outside. DVDs and magazines scattered on the floor.

Camera: placed where the TV is, at seated eye level, looking straight at a green two-seater sofa against the back wall. A low wooden coffee table in the foreground at the bottom of the frame (empty table top).

Two characters sit side by side on the sofa, relaxed, facing the camera (as if watching TV), bodies turned very slightly toward each other:
- LEFT: the brown dog from the first attached image (dark-brown knit beanie, red hoodie, navy pants, sleepy half-closed eyes). Keep his face, colors and proportions exactly the same. Mouth closed, neutral.
- RIGHT: the round black fluffy dog from the second attached image (big black curly fur, grey shorts). Replace the T-shirt print with a PLAIN cream T-shirt with a small simple film-reel icon (no poster, no text, no real movie). Mouth closed, neutral.

Both characters fully visible from head to feet (feet may be hidden behind the table), heads at about 40–60% of the image height, both within the central 80% of the width. Leave the top 20% of the image as calm background (wall). Nothing important in the bottom-right corner.
No text, no logos, no watermarks, no real movie posters.
```

**チェック：** 2人の顔が元の絵と同じか／じょんどぅーのTシャツが無地＋小さなマークか／2人が画面の中央80%に入っているか

---

## ② 2人がいない部屋
**添付：** ①でできた完成図

```
Using the attached image, remove both characters completely and show the empty sofa.
Keep EVERYTHING else exactly the same: same camera, same composition, same room, same lighting, same colors, same size.
The poster frame stays empty. The coffee table top stays empty.
Vertical 9:16, same resolution. No text, no logos.
```

---

## ③ ごんべぇだけ
**添付：** ①の完成図

```
From the attached image, keep ONLY the brown dog on the left (beanie, red hoodie).
Same pose, same size, same position in the frame, exactly the same drawing.
Remove the room, the sofa, the table and the other character: replace everything else with a flat solid pure green background (#00FF00).
No shadow on the background. Any parts of his body that were hidden by the table should be drawn completely.
Vertical 9:16, same resolution.
```

## ④ じょんどぅーだけ
**添付：** ①の完成図

```
From the attached image, keep ONLY the round black fluffy dog on the right.
Same pose, same size, same position in the frame, exactly the same drawing.
Remove the room, the sofa, the table and the other character: replace everything else with a flat solid pure green background (#00FF00).
No shadow on the background. Any parts of his body that were hidden by the table should be drawn completely.
Vertical 9:16, same resolution.
```

---

## ⑤ 表情の差分（③と④それぞれで）
**添付：** ③（または④）の絵。**1回に1か所だけ**変えてもらう。

```
Edit the attached image. Change ONLY the [EYES / MOUTH] to: [下の表から]
Keep everything else pixel-identical: same pose, same position, same size, same colors, same green background.
```

| 番号 | 変える場所 | 指示（[ ]に入れる英語） |
|---|---|---|
| 目1 | EYES | normal sleepy half-closed eyes（いつもの目。①と同じなら省略可） |
| 目2 | EYES | wide open surprised eyes |
| 目3 | EYES | flat unimpressed "jito-me" eyes, looking sideways |
| 目4 | EYES | sad droopy eyes looking down |
| 目5 | EYES | happy closed curved eyes (smiling) |
| 目6 | EYES | serious focused eyes |
| 目7 | EYES | fully closed eyes (blink) |
| 口1 | MOUTH | closed mouth（①と同じなら省略可） |
| 口2 | MOUTH | slightly open mouth, talking |
| 口3 | MOUTH | wide open mouth, talking loudly |

ごんべぇ・じょんどぅー合わせて最大20枚。最低限は **目2・目3・目4・目7・口2・口3** の6枚ずつ。

---

## ⑥（後で）入ってくるときの立ちポーズ
入りのひと言の場面を作るときに用意する。プロンプトはそのときに作る。
