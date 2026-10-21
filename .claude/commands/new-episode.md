---
description: 新しい回を制作する（例：/new-episode 休日が虚しい ロスト・イン・トランスレーション）
argument-hint: <悩み> <映画>
---

新しい回を作ります。悩みと映画：$ARGUMENTS

ディレクターとして次の順で進めてください。各担当は `.claude/agents/` のサブエージェントです。品質基準は `docs/quality-bar.md`。

### 企画
1. `episodes/` を見て次の回番号を決め、`episodes/epXX-<英語slug>/` を `_template` から作る
2. **scriptwriter** に台本を書かせる
3. **fact-checker** に検証させる。❌があれば scriptwriter に直させ、再検証
4. **ここで止まり**、台本とファクトチェック結果の要約を人間に見せて承認を待つ

### 制作
5. `_template/look.json` をコピーし、**art-director** と相談して部屋と服の方向を決める（`docs/episode-look.md`）。**storyboarder** で `timeline.json`（カット・表情・ポーズ・反応・間）を作る
6. 並行で進める：
   - **character-rigger**：timeline で使う表情・ポーズがライブラリに揃っているか確認し、足りなければ追加
   - **art-director**：映画に合わせた部屋の模様替え（`look.json` の room：照明・窓・ポスター・小道具・飾り）
   - **character-rigger** は look.json の outfits（その回の服）も用意する
   - **voice**：音声と口パク用エンベロープ（録音が必要なら人間に依頼して止まる）
7. **motion-fx** でテロップ書式とエフェクトを配置
8. **sound-designer** で効果音・BGMを配置し、ミックス
9. **animator** で `output/epXX.mp4` を書き出す

### 検品
10. **qa-reviewer** で検品。参考動画の分析があれば **reference-analyst** に比較させる
11. 差し戻しがあれば該当担当に戻す（最大2周）
12. 完成動画と qa.md の要約を人間に渡す。投稿用のキャプション案とハッシュタグも添える

外部APIのキーが無い・素材が足りないなど自分では進められないことがあれば、何が必要かを具体的に書いて止まること。
