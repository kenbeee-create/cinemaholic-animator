# renderer（未実装）

animator エージェントが実装する合成エンジン。

## 最初のマイルストーン
「ごんべぇのパーツ ＋ 録音1セリフ ＋ 部屋の背景 → 5秒の口パクMP4」が出ること。

## 要件
- 入力：`episodes/epXX/timeline.json`、`audio/lines.json`、`assets/characters/*/character.json`
- 出力：`output/epXX.mp4`（1080×1920 / 30fps / H.264 / AAC）
- 方式：Remotion（Node）推奨。セットアップが重ければ Python＋Pillow でフレーム生成 → ffmpeg で結合
- 詳細な動きの仕様は `.claude/agents/animator.md`

## 実装を頼むときの一言
「renderer の最初のマイルストーンを実装して。パーツが足りなければ gonbe_base.png を仮で使って口だけ動かして」
