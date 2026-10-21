# ChatGPT用 プロンプト集（コピペ用）

ChatGPT（画像生成）に**手動で**投げるためのプロンプト。上から順番に進める。
できた画像は**そのままこのチャット（Claude）に送る**。切り抜き・層分け・登録はこちらでやる。

## 進め方
| 段階 | ChatGPTのどこで | 添付するもの |
|---|---|---|
| ① 完成図 | **新しいチャット** | gonbe_base.png・johndoe_base.png・johndoe_room_v1.png |
| ② 部屋だけ | ①と**同じチャット**で続けて | なし（直前の完成図を使う） |
| ③ ごんべぇだけ | ①と**同じチャット**で続けて | なし |
| ④ じょんどぅーだけ | ①と**同じチャット**で続けて | なし |
| ⑤ 表情（ごんべぇ） | **新しいチャット** | ③でできた画像 |
| ⑤ 表情（じょんどぅー） | **新しいチャット** | ④でできた画像 |

## コツ
- 画像は「＋」から添付してからプロンプトを貼る
- ①は気に入るまで何回か作り直してよい（「もう1枚」「〇〇だけ直して」）。**①が全部の土台**なので、ここだけは妥協しない
- 直すときは作り直すより「〇〇だけ直して、ほかは同じで」と頼む方が安定する
- 縦長（2:3）で出てくる。動画の9:16にはこちらで合わせる
- ③④で背景が透明にならず白や市松模様になったら、「背景を透明にして」と1回だけ頼む。それでもダメなら気にせず送ってOK（こちらで抜く）
- ダウンロードは画像を長押し（スマホ）か、右上の保存ボタン（PC）

---

## ① 完成図（新しいチャット）
添付：`gonbe_base.png`・`johndoe_base.png`・`johndoe_room_v1.png`

```
Vertical portrait illustration (2:3), highest quality.
2D flat-color cartoon, thick dark-brown outlines, American cartoon style, muted warm palette — match the style of the attached character images exactly.

Scene: a dim, cozy bedroom-living room in a family house at night (use the attached room only as a mood reference). Warm indirect light from a floor lamp. The room is designed with clear, EMPTY display spots so that props can be added later — keep every spot below empty and clearly visible:
1. Back wall, above the sofa, slightly left of center: a large EMPTY vertical poster frame (no picture, no text).
2. Back wall, right of the poster: a long floating wall shelf with three empty spaces (for figures and small objects).
3. Back wall, left: a tall DVD/book shelf, densely packed (spines are plain colors, no readable titles).
4. Small window on the upper left wall showing plain night sky (the view will be replaced later).
5. Left of the sofa: a small side table next to the floor lamp, with an empty top.
6. Foreground: a low wooden coffee table in the center bottom of the frame, large and close to the camera, with a completely empty top (the main spot for props).
7. Front-left floor: an empty open space on the rug where a box or bag can be placed.
A few DVDs and magazines scattered on the floor near the sofa, nothing else.

Camera: placed where the TV is, at seated eye level, looking straight at a green two-seater sofa against the back wall. A low wooden coffee table in the foreground at the bottom of the frame (empty table top).

Two characters sit side by side on the sofa, relaxed, facing the camera (as if watching TV), bodies turned very slightly toward each other:
- LEFT: the brown dog from the first attached image (dark-brown knit beanie, red hoodie, navy pants, sleepy half-closed eyes). Keep his face, colors and proportions exactly the same. Mouth closed, neutral.
- RIGHT: the round black fluffy dog from the second attached image (big black curly fur, grey shorts). Replace the T-shirt print with a PLAIN cream T-shirt with a small simple film-reel icon (no poster, no text, no real movie). Mouth closed, neutral.

Both characters fully visible from head to feet (feet may be hidden behind the table), heads at about 40–60% of the image height, both within the central 80% of the width. Leave the top 15% of the image as calm background (wall/ceiling). Keep all display spots inside the central 80% of the width. Nothing important in the bottom-right corner.
No text, no logos, no watermarks, no real movie posters.
```

**チェック**：2人の顔が元の絵と同じ／じょんどぅーのTシャツが無地＋小さなマーク／2人が画面の真ん中寄り／小物を置く7つの場所（ポスター枠・壁の棚・DVD棚・窓・サイドテーブル・手前のテーブル・手前の床）が空いている

困ったとき（貼り足す一文）
- 顔が変わった → `Keep both characters' faces exactly the same as the attached character images.`
- 小物が置かれてしまった → `Remove all objects from the poster frame, wall shelf, side table, coffee table and floor space. Keep them empty.`
- 文字が入った → `Remove all text and logos.`

---

## ② 部屋だけ（①と同じチャットで）
```
Using the key visual you just made, remove both characters completely and show the empty sofa.
Keep EVERYTHING else exactly the same: same camera, same composition, same room, same lighting, same colors, same size.
All display spots stay empty: the poster frame, the wall shelf, the side table, the coffee table and the open floor space.
Same vertical size. No text, no logos.
```

## ③ ごんべぇだけ（①と同じチャットで）
```
From the previous key visual image, keep ONLY the brown dog on the left (beanie, red hoodie).
Same pose, same size, same position in the frame, exactly the same drawing.
Remove the room, the sofa, the table and the other character.
Output a PNG with a fully TRANSPARENT background (no floor, no shadow).
Any parts of his body that were hidden by the table or sofa should be drawn completely.
Same vertical size.
```

## ④ じょんどぅーだけ（①と同じチャットで）
```
From the previous key visual image, keep ONLY the round black fluffy dog on the right.
Same pose, same size, same position in the frame, exactly the same drawing.
Remove the room, the sofa, the table and the other character.
Output a PNG with a fully TRANSPARENT background (no floor, no shadow).
Any parts of his body that were hidden by the table or sofa should be drawn completely.
Same vertical size.
```

---

## ⑤ 表情の差分
キャラごとに**新しいチャット**を開き、③（または④）の画像を添付して、下を**1つずつ**送る。
**★が最低限**（各キャラ6枚）。余裕があれば残りも。

### ごんべぇ（③の画像を添付）

**★ 目2 驚き**
```
Edit the attached image. Change ONLY the eyes to: wide open surprised eyes.
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

**★ 目3 ジト目**
```
Edit the attached image. Change ONLY the eyes to: flat unimpressed "jito-me" eyes, looking sideways.
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

**★ 目4 落ち込み**
```
Edit the attached image. Change ONLY the eyes to: sad droopy eyes looking down.
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

**目5 笑顔**
```
Edit the attached image. Change ONLY the eyes to: happy closed curved eyes (smiling).
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

**目6 真顔**
```
Edit the attached image. Change ONLY the eyes to: serious focused eyes.
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

**★ 目7 まばたき（目を閉じる）**
```
Edit the attached image. Change ONLY the eyes to: fully closed eyes (blink).
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

**★ 口2 口を少し開ける**
```
Edit the attached image. Change ONLY the mouth to: slightly open mouth, talking.
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

**★ 口3 口を大きく開ける**
```
Edit the attached image. Change ONLY the mouth to: wide open mouth, talking loudly.
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

### じょんどぅー（④の画像を添付）

**★ 目2 驚き**
```
Edit the attached image. Change ONLY the eyes to: wide open surprised eyes.
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

**★ 目3 ジト目**
```
Edit the attached image. Change ONLY the eyes to: flat unimpressed "jito-me" eyes, looking sideways.
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

**★ 目4 落ち込み**
```
Edit the attached image. Change ONLY the eyes to: sad droopy eyes looking down.
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

**目5 笑顔**
```
Edit the attached image. Change ONLY the eyes to: happy closed curved eyes (smiling).
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

**目6 真顔**
```
Edit the attached image. Change ONLY the eyes to: serious focused eyes.
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

**★ 目7 まばたき（目を閉じる）**
```
Edit the attached image. Change ONLY the eyes to: fully closed eyes (blink).
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

**★ 口2 口を少し開ける**
```
Edit the attached image. Change ONLY the mouth to: slightly open mouth, talking.
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

**★ 口3 口を大きく開ける**
```
Edit the attached image. Change ONLY the mouth to: wide open mouth, talking loudly.
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness.
Keep the transparent background.
```

---

## 送るときの名前（わかれば。わからなければそのまま送ってOK）
- ① `keyvisual.png`　② `room_base.png`　③ `gonbe_sit.png`　④ `johndoe_sit.png`
- ⑤ `gonbe_目2.png`・`johndoe_口3.png` のように「キャラ_番号」
