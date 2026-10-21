# 画面テンプレート

キャラ以外の画面（トーク画面・タイトルなど）を、JSONを書き換えるだけで作り直せるテンプレート。
トーン（色・線・文字）は `style.py` に集約していて、`docs/tone.md` が説明。

| テンプレート | 場面 | 実行 |
|---|---|---|
| `chat.py` | Scene1 トーク画面 | `python3 renderer/templates/chat.py <chat.json> <出力フォルダ>` |
| `title.py` | Scene2 タイトル | `python3 renderer/templates/title.py <title.json> <出力フォルダ>` |

例：`examples/chat_example.json`・`examples/title_example.json`（できあがりは `examples/preview/`）

## chat.json（トーク画面）
```json
{
  "owner": "gonbe",
  "background": "assets/backgrounds/johndoe_room_v1.png",
  "day_label": "金曜日",
  "time": "19:42",
  "messages": [
    { "text": "今日上司にめっちゃ怒られた" },
    { "text": "俺まったく関係ないのに" },
    { "text": "上司〇してぇー" },
    { "text": "今日行くわ" }
  ]
}
```
| 項目 | 意味 | 省略したとき |
|---|---|---|
| owner | 誰のスマホか。この人のメッセージが右側 | gonbe |
| background | スマホの後ろに映る部屋（その回の部屋を入れる） | 夜の暗い背景 |
| day_label / time | 日付のラベル・時刻 | なし / 19:42 |
| messages[].text | メッセージ本文。長いと自動で折り返す | — |
| messages[].from | 送った人（`johndoe` にすると左側に相手の返信として出る） | owner |
| messages[].at | 出る時刻（秒） | 0.25秒から0.6秒おき |
| interval | メッセージの間隔（秒） | 0.6 |
| read_at | 「既読」がつく時刻 | 最後のメッセージの0.45秒後 |
| duration | 全体の長さ（秒） | 既読の0.6秒後（最低3秒） |

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
