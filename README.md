# 🎬 CINEMA HOLIC（シネマホリック）

> 映画は、作った人間の痛みから生まれている。だから、見た人間の痛みに効く。

日常の悩みに「映画」を処方するショートアニメのプロジェクト。
ごんべぇ（悩む会社員）とじょんどぅー（映画オタクの処方医）の会話で、60秒の縦型動画を作ります。

## このリポジトリでできること
Claude Code のサブエージェントがチームとして動き、
**悩みと映画を渡すだけで「台本 → 事実確認 → 絵コンテ → 素材 → 音声 → 動画」まで**進めます。
人間がやるのは「台本の承認」と「最終確認」の2回だけ。

```
/new-episode <悩み> <映画>
```

## フォルダ構成
```
index.html                パーツ確認ツール（GitHub Pagesで公開）
CLAUDE.md                 プロジェクトの憲法（Claudeが毎回読む）
.claude/agents/           サブエージェント7名の定義
.claude/commands/         /new-episode コマンド
docs/
  team.md                 チーム構成と制作フロー
  brand.md                ターゲット・ペルソナ・インサイト
  lore.md                 伏線台帳
  mobile-setup.md         スマホでClaude Codeを使う手順
assets/
  characters/gonbe/       ごんべぇ（ベース画像・パーツ・character.json）
  characters/johndoe/     じょんどぅー
  backgrounds/            じょんどぅーの部屋
  posters/ props/ sound/  回ごとの素材・効果音・BGM
episodes/
  _template/              台本テンプレート
  ep01-fight-club/        第1話
schemas/timeline.schema.json  絵コンテ（タイムライン）の形式
renderer/                 合成エンジン（これから作る）
output/                   書き出した動画（git管理外）
```

## 現在の状況
- [x] コンセプト・ターゲット・キャラ設定
- [x] 第1話台本（改訂版・ファクトチェック前）
- [x] 背景（じょんどぅーの部屋 v1）
- [x] エージェント定義・制作フロー
- [ ] ごんべぇのパーツを透過PNGで1枚ずつ用意
- [ ] renderer（口パク＋揺れの合成）を実装 ← **次にやること**
- [ ] ブランド音・BGMの確定
- [ ] じょんどぅーのパーツ化

## パーツ確認ツール（Animator）
ルートの `index.html` はスマホで使えるパーツ確認ツールです（GitHub Pagesで公開）。
https://kenbeee-create.github.io/cinemaholic-animator/

## スマホから作業する
`docs/mobile-setup.md` を参照。
