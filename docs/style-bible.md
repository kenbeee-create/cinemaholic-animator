# 絵柄のルール（スタイルバイブル）

シネマホリックの絵は、**全部この1つのルールで作る**。キャラ・部屋・小物・記号のどれを新しく作るときも同じ。
「AIで作った感」の正体は、ほとんどが **色・線・光のばらつき**。ルールで固定し、切り抜き時の仕上げで最後にそろえる。

## 決まりごと
| 項目 | ルール |
|---|---|
| 線 | こげ茶に近い黒（#1f150f）の、**太さが一定の**輪郭線。手描きのような少しの揺れはOK。線の強弱・かすれ・スケッチ線はなし |
| 塗り | **ベタ塗り＋影1段**（アニメ塗り）。グラデーション・エアブラシ・ぼかし・発光・テクスチャ・反射のハイライトは使わない |
| 色 | くすんだ暖色が基本（茶・こげ茶・からし色・くすんだ赤・クリーム・オリーブ・紺）。鮮やかすぎる色・ネオンは「その回の映画の色」のときだけ。色の一覧は `assets/style/palette.json` |
| 形 | 丸みのあるシンプルな形。細かすぎる描き込み（木目・文字・模様をびっしり）はしない |
| 光 | 部屋の明かりはスタジオ側（照明の色・ランプのゆらぎ）でつける。**素材そのものには光や影の演出を入れない** |
| 文字 | 素材に文字・ロゴを入れない（実在のロゴやポスターは使わない：CLAUDE.md）。必要な文字はこちらで後から入れる |
| 背景 | 部品は**無地のマゼンタ（#FF00FF）**の上に、間隔をあけて格子状に並べる（あとで自動で切り抜く） |

## 毎回プロンプトの頭に付ける文章（STYLE LOCK）
```
STYLE LOCK — follow exactly, same art style as the attached reference image:
- Flat 2D cartoon cel style. Bold, uniform-weight dark brown-black outlines (#1f150f), slightly hand-inked.
- Flat color fills with only ONE simple shadow tone. NO gradients, NO airbrush, NO glow, NO bloom, NO texture, NO glossy highlights, NO lens effects.
- Muted warm palette: browns, dark brown, mustard, dusty red, cream, olive green, navy.
- Simple rounded shapes, low detail. No tiny patterns, no text, no logos, no watermarks, no signatures.
- Every object fully visible and separated by wide empty space. Background: solid flat pure magenta (#FF00FF), no shadows on the background, no floor.
```

## 仕上げ（Claude 側で自動）
`scripts/slice_sheet.py` が切り抜くときに：
1. 背景のマゼンタを抜き、小さなゴミを消す
2. 色を少ない数（既定8色）の平らな塗りにまとめる → グラデーションや光のにじみが消える
3. 色を `palette.json` に半分くらい寄せる → 部屋やキャラと色味がそろう
4. 外側の輪郭線を、同じ色・同じ太さで描き直す → 線の太さがそろう

## 作り方のコツ
- **毎回、完成図（keyvisual.png）を添付する**。言葉より絵のほうが絵柄がそろう
- 1枚に9個（3×3）まで。多すぎると1個ずつが雑になる
- 気に入らない1個だけを作り直すときも、シートで頼んで良いものだけ使う（「〇番だけ描き直して、ほかは同じで」）
- 同じチャットで続けて頼むと絵柄がそろいやすい。日をまたぐときは新しいチャットに STYLE LOCK と完成図を付け直す
