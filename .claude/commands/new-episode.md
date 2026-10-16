---
description: 新しい回を制作する（例：/new-episode 休日が虚しい ロスト・イン・トランスレーション）
argument-hint: <悩み> <映画>
---

新しい回を作ります。悩みと映画：$ARGUMENTS

ディレクターとして次の順で進めてください。各担当は `.claude/agents/` のサブエージェントです。

1. `episodes/` を見て次の回番号を決め、`episodes/epXX-<英語slug>/` を `_template` から作る
2. **scriptwriter** に台本を書かせる
3. **fact-checker** に検証させる。❌があれば scriptwriter に直させ、再検証
4. **ここで止まり**、台本とファクトチェック結果の要約を人間に見せて承認を待つ
5. 承認後、**storyboarder** で `timeline.json` を作る
6. **art-director** と **voice** を並行で動かす（音声の録音が必要なら、人間に依頼して止まる）
7. **animator** で `output/epXX.mp4` を書き出す
8. **qa-reviewer** で検品。差し戻しがあれば該当担当に戻す（最大2周）
9. 完成動画と qa.md の要約を人間に渡す。投稿用のキャプション案とハッシュタグも添える

途中で外部APIのキーが無い・素材が足りないなど自分では進められないことがあれば、何が必要かを具体的に書いて止まること。
