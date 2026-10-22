# ChatGPT用 プロンプト集（コピペ用）

ChatGPT（画像生成）に**手動で**投げるためのプロンプト。上から順番に進める。
できた画像は**そのままこのチャット（Claude）に送る**。切り抜き・層分け・登録はこちらでやる。

## 進め方
| 段階 | ChatGPTのどこで | 添付するもの |
|---|---|---|
| ① 完成図 | **新しいチャット** | gonbe_base.png・johndoe_base.png・johndoe_room_v1.png |
| ② 部屋だけ | **新しいチャット** | `keyvisual.png`（Tシャツを無地に直した完成図） |
| ③ ごんべぇだけ | ②と**同じチャット**で続けて | `keyvisual.png` をもう一度 |
| ④ じょんどぅーだけ | ②と**同じチャット**で続けて | `keyvisual.png` をもう一度 |
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
- RIGHT: the round black fluffy dog from the second attached image (big black curly fur, grey shorts). Replace the T-shirt with a completely PLAIN cream T-shirt (no print, no icon, no text). Mouth closed, neutral.

Both characters fully visible from head to feet (feet may be hidden behind the table), heads at about 40–60% of the image height, both within the central 80% of the width. Leave the top 15% of the image as calm background (wall/ceiling). Keep all display spots inside the central 80% of the width. Nothing important in the bottom-right corner.
No text, no logos, no watermarks, no real movie posters.
```

**チェック**：2人の顔が元の絵と同じ／じょんどぅーのTシャツが無地／2人が画面の真ん中寄り／小物を置く7つの場所（ポスター枠・壁の棚・DVD棚・窓・サイドテーブル・手前のテーブル・手前の床）が空いている

困ったとき（貼り足す一文）
- 顔が変わった → `Keep both characters' faces exactly the same as the attached character images.`
- 小物が置かれてしまった → `Remove all objects from the poster frame, wall shelf, side table, coffee table and floor space. Keep them empty.`
- 文字が入った → `Remove all text and logos.`

---

## ② 部屋だけ（新しいチャット・`keyvisual.png` を添付）
```
Using the attached key visual, remove both characters completely and show the empty sofa.
Keep EVERYTHING else exactly the same: same camera, same composition, same room, same lighting, same colors, same size.
All display spots stay empty: the poster frame, the wall shelf, the side table, the coffee table and the open floor space.
Same vertical size. No text, no logos.
```

## ③ ごんべぇだけ（`keyvisual.png` を添付）
```
From the attached key visual, keep ONLY the brown dog on the left (beanie, red hoodie).
Same pose, same size, same position in the frame, exactly the same drawing.
Remove the room, the sofa, the table and the other character.
Output a PNG with a fully TRANSPARENT background (no floor, no shadow).
Any parts of his body that were hidden by the table or sofa should be drawn completely.
Same vertical size.
```

## ④ じょんどぅーだけ（`keyvisual.png` を添付）
```
From the attached key visual, keep ONLY the round black fluffy dog on the right.
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
**ルール：目はいつもの眠そうな半目を崩さない**（^^の笑顔・うるんだ大きな目はNG）

**★ 照れ笑い（口を閉じたまま）**
```
Edit the attached image. Keep his usual sleepy half-closed eyes EXACTLY as they are (same eye shape, same eyelids) — do not close or curve the eyes.
Change ONLY: a small embarrassed smirk — one corner of the closed mouth slightly raised, a light pink blush on the cheek, pupils looking slightly to the side.
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness. Keep the transparent background.
```

**★ 照れ笑い（「へへ」と少し口を開けて）**
```
Edit the attached image. Keep his usual sleepy half-closed eyes EXACTLY as they are — do not close or curve the eyes.
Change ONLY: a shy little laugh — mouth slightly open in a crooked smile showing a bit of the tongue, a light pink blush on the cheek, pupils looking slightly away.
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness. Keep the transparent background.
```

**★ ため息（へこんだとき）**
```
Edit the attached image. Keep his usual eye SHAPE (sleepy, half-closed) — do NOT make the eyes bigger, rounder or teary, and do not close them into curves.
Make the upper eyelids droop a little lower, as if exhausted, pupils looking slightly down.
Change the mouth to a sigh: lips slightly parted, a small open mouth breathing out ("haah").
Keep everything else exactly identical: same pose, same position, same size, same colors, same line thickness. Keep the transparent background.
```
（ため息の白いもや・顔の縦線などの記号は、こちらで動画の上に足します）

### じょんどぅー
**目は毛で隠れているので、目の表情は作らない。** 口（閉・半開き・開き）はこちらで作成済み。
リアクションは動き（うなずく・首をかしげる・跳ねる・しょんぼり など）で出すので、追加の画像は不要。

---

## 送るときの名前（わかれば。わからなければそのまま送ってOK）
- ① `keyvisual.png`　② `room_base.png`　③ `gonbe_sit.png`　④ `johndoe_sit.png`
- ⑤ `gonbe_目2.png`・`johndoe_口3.png` のように「キャラ_番号」
