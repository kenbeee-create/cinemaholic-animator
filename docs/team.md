# 制作チーム構成（サブエージェント）

## 基本方針
- **キャラごとにエージェントは分けない。** キャラの一貫性は「固定の素材ライブラリ」で守る
- 動きは動画生成AIではなく **パーツ画像をコードで動かす**（口の差し替え・上下の揺れ・尻尾・ズーム・カット割り）。
  ギャル猫やクソメガネ系の「少し動く」表現はこれで十分作れ、毎回ブレない
- 人間（廉）が関わるのは **台本の承認** と **最終動画の確認** の2回だけ

## 体制図
```
🎬 ディレクター（メインのClaude）
 │  進行管理・各担当への指示・成果物の統合
 │
 ├ ① scriptwriter   悩み→インサイト→台本（P&G型）
 ├ ② fact-checker   バックボーン・名言の真偽を出典付きで確認
 │        ↓ 👤 廉が台本を承認
 ├ ③ storyboarder   台本→タイムラインJSON（セリフ・表情・カット・字幕・効果音）
 ├ ④ art-director   その回のポスター（オリジナル）と小道具を用意 ※キャラは作らない
 ├ ⑤ voice          音声（録音 or TTS）を整え、口パク用の発話区間を出す
 ├ ⑥ animator       パーツ＋背景＋音声をコードで合成し MP4 を書き出す
 └ ⑦ qa-reviewer    チェックリストで検品し、差し戻し先を指定
          ↓ 👤 廉が最終確認 → 投稿
```

## 担当ごとの入出力
| # | 担当 | 入力 | 出力 |
|---|---|---|---|
| ① | scriptwriter | 悩み・映画・`docs/brand.md` | `script.md` |
| ② | fact-checker | `script.md` | `factcheck.md`（判定・出典・修正案） |
| ③ | storyboarder | 承認済み `script.md` | `timeline.json`（`schemas/timeline.schema.json` 準拠） |
| ④ | art-director | `timeline.json` | `assets/props/epXX/*.png`、`assets/posters/epXX.png` |
| ⑤ | voice | `script.md`・録音ファイル | `audio/lines/*.wav`、`audio/lines.json`（発話区間） |
| ⑥ | animator | ③④⑤の成果物・キャラ素材 | `output/epXX.mp4` |
| ⑦ | qa-reviewer | 完成動画・`timeline.json` | `qa.md`（合否・差し戻し先） |

## 外部サービス（Claude単体ではできない部分）
| 用途 | 候補 | 必要なもの |
|---|---|---|
| 画像生成（小道具・ポスター・新しい表情） | Gemini 画像API | `GEMINI_API_KEY` |
| 音声（TTS） | ElevenLabs / VOICEVOX | `ELEVENLABS_API_KEY` など。自分で録音するなら不要 |
| 合成・書き出し | Remotion または ffmpeg＋Python | APIキー不要（Node / Python） |

## 段階的な立ち上げ
1. **⑥ animator を最初に作る**：ごんべぇのパーツ＋録音音声 → 口パク動画が出るか確認（ここが一番のリスク）
2. ③ storyboarder の JSON → animator に流してシーンが切り替わるか確認
3. ① ② を繋いで台本まで自動化
4. ④ ⑤ を繋いで全自動化。⑦ で品質を固定

## 素材ライブラリの注意
- `assets/characters/gonbe/parts/_sheet_gemini.png` は Gemini のパーツ分解シートだが、
  **透過ではなく市松模様が画像に焼き込まれている**。合成に使うには
  透過PNG（1パーツ1ファイル）で出し直すか、単色背景で出力してクロマキー抜きが必要
- じょんどぅーのパーツはまだ無い。ごんべぇで方式が固まってから作る
