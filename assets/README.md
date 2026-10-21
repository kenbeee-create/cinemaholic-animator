# 素材の置き方

| フォルダ | 中身 | ルール |
|---|---|---|
| characters/<id>/ | ベース画像・パーツ・character.json | キャラは毎回生成しない。差し替えたら character.json も更新 |
| characters/<id>/parts/ | 1パーツ1枚の透過PNG | 同じキャンバスサイズで書き出すと位置合わせが楽 |
| backgrounds/ | じょんどぅーの部屋の土台（層に分ける）と windows/（窓の外） | 骨格は毎回同じ。照明の色・窓・ポスター・小物を映画ごとに差し替える（docs/episode-look.md） |
| posters/ | 回ごとの壁ポスター | **実在ポスターの再現は禁止**。オリジナルのみ |
| props/library/ | 使い回す飾りの小物 | 回をまたいで再利用 |
| props/epXX/ | テーブルの小道具・伏線アイテム | 使ったプロンプトは PROMPTS.md に残す |
| sound/ | brand_pill.wav / brand_low.wav / stamp.wav / bgm.mp3 | 商用利用可の素材のみ。入手元を sound/CREDITS.md に記録 |

## 既知の課題
- `characters/gonbe/parts/_sheet_gemini.png` は透過ではなく市松模様が描き込まれている → 出し直しが必要
- じょんどぅーのTシャツ柄は実在映画のポスターに見えるため、オリジナル柄に差し替える
- `backgrounds/johndoe_room_v1.png` は 768×1376（右下にGeminiのマークあり）→ 高解像度・マーク無しで作り直すとよい
