# 制作チーム構成（サブエージェント11名）

## 基本方針
- 目標品質：ギャル猫・クソメガネのような「少し動く会話ショートアニメ」。基準は `docs/quality-bar.md`
- **動画生成AIは使わず、パーツ画像をコードで動かす**（毎回キャラがブレない）
- **キャラの一貫性は素材ライブラリで守る**。キャラごとにエージェントは分けず、character-rigger が両キャラを管理
- 品質の差は「常にどこかが小さく動いているか」「テンポ」「テロップ」「効果音」で決まる。そのための専門担当を置く
- 人間（廉）が関わるのは **台本の承認** と **最終確認** の2回だけ

## 体制図
```
🎬 ディレクター（メインのClaude）
 │
 ├─ 企画 ──────────────────────────────
 │   ① scriptwriter      悩み→インサイト→台本
 │   ② fact-checker      バックボーン・名言の出典確認
 │          ↓ 👤 廉が台本を承認
 │
 ├─ 演出 ──────────────────────────────
 │   ③ storyboarder      カット割り・カメラ・表情・反応・間（テンポの責任者）
 │
 ├─ 素材（並行） ───────────────────────
 │   ④ character-rigger  キャラの透過パーツ・表情・口形・ポーズ・リグ  ★新
 │   ⑤ art-director      壁ポスター（オリジナル）・小道具・背景
 │   ⑥ voice             音声・口パク用の音量データ・実測の尺
 │
 ├─ 仕上げ ─────────────────────────────
 │   ⑦ motion-fx         テロップの書式と動き・漫画的エフェクト      ★新
 │   ⑧ sound-designer    効果音・BGM・ミックス                       ★新
 │   ⑨ animator          合成エンジン（口パク・まばたき・揺れ）→ MP4
 │
 └─ 品質 ──────────────────────────────
     ⑩ qa-reviewer       チェックリストで検品・差し戻し
     ⑪ reference-analyst 参考動画を数値化し、品質基準と完成品の差を出す ★新
            ↓ 👤 廉が最終確認 → 投稿
```

## 担当ごとの入出力
| # | 担当 | 主な出力 |
|---|---|---|
| ① | scriptwriter | `episodes/epXX/script.md` |
| ② | fact-checker | `factcheck.md` |
| ③ | storyboarder | `timeline.json`（カット・表情・ポーズ・反応・間） |
| ④ | character-rigger | `assets/characters/<id>/`（パーツ・表情・`character.json`・コンタクトシート） |
| ⑤ | art-director | `assets/posters/`・`assets/props/epXX/` |
| ⑥ | voice | `audio/lines/*.wav`・`audio/lines.json`（音量エンベロープ） |
| ⑦ | motion-fx | `renderer/presets/`・`assets/fx/`・timeline へのテロップ書式とエフェクト |
| ⑧ | sound-designer | `assets/sound/`・timeline の `sfx`・ミックス結果 |
| ⑨ | animator | `renderer/`・`output/epXX.mp4` |
| ⑩ | qa-reviewer | `qa.md` |
| ⑪ | reference-analyst | `references/analysis/*.md`・`benchmark.md`・品質基準の更新 |

## 2つのコマンド
| コマンド | いつ使う | 何が起きる |
|---|---|---|
| `/setup-studio` | 最初に1回（素材を増やしたいときも） | キャラ素材・テロップとエフェクト・音素材・合成エンジンの「土台」を作る |
| `/new-episode <悩み> <映画>` | 毎回 | 台本 → 承認 → 制作 → 検品まで進める |

## 立ち上げの順番
1. **参考動画を3本 `references/videos/` に入れる** → reference-analyst が品質基準を実測値に更新
2. `/setup-studio` で土台を作る（ここが一番重い。最初は数セッションかかる想定）
3. テスト用の15秒動画で品質を確認し、qa-reviewer と reference-analyst で差分を潰す
4. `/new-episode` で本番の制作へ

## 外部サービス（Claude単体ではできない部分）
| 用途 | 候補 | 必要なもの |
|---|---|---|
| 新しい表情・ポーズ・小道具の画像生成 | Gemini 画像API | `GEMINI_API_KEY`（無ければ人間が手動生成） |
| 音声 | 自分で録音 / ElevenLabs / VOICEVOX | 録音なら不要。TTSならキー |
| 効果音・BGM | 商用利用可のフリー素材 | 人間がダウンロードして置く場合あり |
| 合成・書き出し | Remotion または Python＋ffmpeg | 不要 |
