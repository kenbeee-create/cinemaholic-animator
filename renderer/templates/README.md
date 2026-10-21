# 画面テンプレート

キャラ以外の画面（トーク画面・タイトルなど）を、JSONを書き換えるだけで作り直せるテンプレート。
トーン（色・線・文字）は `style.py` に集約していて、`docs/tone.md` が説明。

## トーク画面メーカー（人が触る道具）
`tools/chat-maker/index.html`。スマホでもPCでも、ブラウザで開くだけで使える。
公開URL：https://kenbeee-create.github.io/cinemaholic-animator/tools/chat-maker/
- メッセージを打つ → その場で動く画面になる（受け取る側／送る側、入力中「…」、打ち込み、既読、通知、スマホへの寄り、速さ）
- 「動画で保存」でそのまま動画になる（iPhoneのSafariはMP4、PCのChromeはMP4かWebM）
- 「JSONをコピー」して各話のフォルダに `chat.json` として置けば、下の `chat.py` が同じ見た目で高画質に書き出す
- アイコンは画像を選んで差し替えられる（その端末にだけ保存）

| テンプレート | 場面 | 実行 |
|---|---|---|
| `chat.py` | Scene1 トーク画面（メーカーと同じ描画をブラウザで動かして書き出す） | `python3 renderer/templates/chat.py <chat.json> <出力フォルダ>` |
| `neon_logo.py` | タイトルアイコン（ネオン） | `python3 renderer/templates/neon_logo.py` |
| `title.py` | Scene2 タイトル | `python3 renderer/templates/title.py <title.json> <出力フォルダ>` |

例：`examples/chat_example.json`・`examples/title_example.json`（できあがりは `examples/preview/`）

## chat.json（トーク画面）
メーカーの「JSONをコピー」で出てくる形。手で書いてもよい。
```json
{
  "view": "receive",
  "day_label": "金曜日",
  "time": "19:42",
  "messages": [
    { "from": "gonbe", "text": "今日上司にめっちゃ怒られた" },
    { "from": "gonbe", "text": "俺まったく関係ないのに", "gap": 0.35 },
    { "from": "gonbe", "text": "上司〇してぇー", "gap": 0.35 },
    { "from": "gonbe", "text": "今日行くわ", "gap": 0.45 }
  ],
  "options": { "typing": true, "typed": true, "read": true, "notify": false, "zoom": 0.06, "speed": 1.0 }
}
```
| 項目 | 意味 |
|---|---|
| view | `receive`＝じょんどぅーのスマホ（ごんべぇのメッセージが届く）／`send`＝ごんべぇのスマホ（打ち込んで送る） |
| messages[].from | `gonbe` か `johndoe`。スマホの持ち主のメッセージが右側 |
| messages[].gap | 前のメッセージから次までの秒数 |
| options.typing | 相手の入力中「…」を出す（話し手が変わったときだけ） |
| options.typed | 自分のメッセージを入力欄に打ち込んでから送る（キーボードも出る） |
| options.read | 自分のメッセージに「既読」をつける |
| options.notify | 最初に通知が上から降りてくる |
| options.zoom | スマホへのゆっくりした寄り（0〜0.2） |
| options.speed | 全体の速さ（0.6〜1.6） |

## title.json（タイトル）
```json
{
  "worry": "上司を〇したい",
  "lead": "そこの君に、",
  "rest": "いい薬を処方します。",
  "background": "assets/backgrounds/johndoe_room_v1.png",
  "duration": 2.0
}
```
`worry` だけ毎回変える。長いときは自動で文字が小さくなる。

## 出力
- `*.mp4`：音なしの動画（1080×1920・30fps）。音は sound-designer が `cues.json` のタイミングで乗せる
- `*_last.png` など：確認用の静止画
- 各話では `episodes/epXX-<slug>/chat.json` と `title.json` を置き、出力は `output/epXX/` へ（git管理外）
