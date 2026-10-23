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

---

## ⑥ 白衣のじょんどぅー（立ち絵）
映画紹介の画面（`docs/movie-card.md`）の右下に出す。**新しいチャット**で、`johndoe/sit_source.png`（無地Tシャツのじょんどぅー）を添付。

```
Draw the character from the attached image as a STANDING full-body pose, wearing a doctor's outfit.
Keep his design exactly the same: the round black fluffy dog with big curly fur that completely hides his eyes, the small dark nose, a short straight closed mouth, grey shorts, the same proportions, colors and thick dark-brown outlines (2D flat cartoon, American cartoon style).
Outfit: an open white doctor's lab coat over his plain cream T-shirt, a stethoscope around his neck, a pen in the chest pocket. No text, no logos, no name tag.
Pose: standing facing the viewer, body turned slightly to the left, one paw raised a little as if explaining something.
Output a PNG with a fully transparent background. Vertical image, full body visible from head to feet.
```

うまくいかないとき（貼り足す一文）
- 目が出てしまった → `His eyes must stay completely hidden by the fur.`
- 体型が変わった → `Keep him short and round, the same body shape as the attached image.`

---

## ⑦ ごんべぇの立ち姿（部屋に入ってくる）
入りのひと言の場面で使う。**新しいチャット**で、`gonbe/sit_source.png`（座りのごんべぇ・透明背景）を添付。

```
Draw the character from the attached image as a STANDING full-body pose, walking in from the left and just stopping, as if entering a friend's room.
Keep his design exactly the same: brown dog, dark-brown knit beanie, red hoodie, navy pants, his usual sleepy half-closed eyes, same proportions, colors and thick dark-brown outlines (2D flat cartoon, American cartoon style).
Pose: body facing slightly to the right, one paw raised casually in greeting, the other paw in the hoodie pocket, mouth slightly open as if saying something. A small plastic convenience-store bag hanging from his wrist.
No text, no logos. Output a PNG with a fully transparent background. Vertical image, full body visible from head to feet.
```

うまくいかないとき（貼り足す一文）
- 目が変わった → `Keep his usual sleepy half-closed eyes exactly as in the attached image.`
- 袋に文字やロゴが入った → `The plastic bag must be plain, with no text or logo.`

---

## ⑧ 記号シート（汗・怒りマークなど9個。新しいチャット・`keyvisual.png` を添付）
添付：`keyvisual.png`
できた画像はそのままClaudeに送る（自動で9個に切り分けて、スタジオの記号が画像に切り替わる）。絵柄のルールは `docs/style-bible.md`。

```
STYLE LOCK — follow exactly, same art style as the attached reference image:
- Flat 2D cartoon cel style. Bold, uniform-weight dark brown-black outlines (#1f150f), slightly hand-inked.
- Flat color fills with only ONE simple shadow tone. NO gradients, NO airbrush, NO glow, NO bloom, NO texture, NO glossy highlights, NO lens effects.
- Muted warm palette: browns, dark brown, mustard, dusty red, cream, olive green, navy.
- Simple rounded shapes, low detail. No tiny patterns, no text, no logos, no watermarks, no signatures.
- Every object fully visible and separated by wide empty space. Background: solid flat pure magenta (#FF00FF), no shadows on the background, no floor.

Make a sprite sheet of 9 Japanese manga emotion symbols for this cartoon, arranged in a clean 3x3 grid, each centered in its own cell, same size, with wide empty magenta space between them. Square image.
Row 1: (1) a single sweat drop, pale blue; (2) a dusty-red "anger vein" cross mark; (3) a block of 6 vertical gloomy lines ("gaan" shock lines), dark blue-gray.
Row 2: (4) a small dark wavy gloom cloud with drips; (5) two music notes; (6) a cluster of three mustard-yellow sparkles.
Row 3: (7) a bold exclamation mark "!" in mustard yellow; (8) a bold question mark "?" in cream; (9) a small puff of sigh smoke, pale gray-cream.
No characters, only the symbols.
```

## ⑨ 小物シート（部屋に置くもの9個。新しいチャット・`keyvisual.png` を添付）
添付：`keyvisual.png`
下の「Row」の中身を、その回に置きたい物に書き換えて使う（例は「ファイト・クラブ」の回）。実在のロゴ・パッケージ・ポスターは描かせない。
送るときに「1:soap:石けん 2:… 」のように番号と名前を一緒に書いてもらえると、その名前で棚に入れる（無ければこちらで付ける）。

```
STYLE LOCK — follow exactly, same art style as the attached reference image:
- Flat 2D cartoon cel style. Bold, uniform-weight dark brown-black outlines (#1f150f), slightly hand-inked.
- Flat color fills with only ONE simple shadow tone. NO gradients, NO airbrush, NO glow, NO bloom, NO texture, NO glossy highlights, NO lens effects.
- Muted warm palette: browns, dark brown, mustard, dusty red, cream, olive green, navy.
- Simple rounded shapes, low detail. No tiny patterns, no text, no logos, no watermarks, no signatures.
- Every object fully visible and separated by wide empty space. Background: solid flat pure magenta (#FF00FF), no shadows on the background, no floor.

Make a sprite sheet of 9 small props for the apartment room in the reference image, arranged in a clean 3x3 grid, each centered in its own cell, front view, same scale as they would appear in the room. Square image.
Row 1: (1) a pink bar of soap; (2) a stack of three blank VHS tapes; (3) a crumpled paper cup of coffee.
Row 2: (4) a cracked smartphone face down; (5) a small potted cactus; (6) an empty pizza box, closed, plain.
Row 3: (7) a desk lamp; (8) a pair of worn sneakers; (9) a framed blank picture (empty frame, no image).
No characters, no text or labels on anything.
```
