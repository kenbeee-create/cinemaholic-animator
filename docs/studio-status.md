# スタジオの進捗

| 土台 | 状態 | メモ |
|---|---|---|
| 品質基準の実測化（参考動画） | 完了（5本） | ギャル猫2・クソメガネ2・サク山チョコ次郎1を分析し quality-bar.md を改訂（2026-10-21） |
| 完成図（キービジュアル） | 完了 | assets/keyvisual/keyvisual.png（ChatGPTで生成、2026-10-22）。9:16に合わせてもSNSのボタン・説明文と重ならないことを確認 |
| 部屋の土台（完成図から） | 素材受領 | assets/backgrounds/room_base_source.png（ChatGPT）。層分けと9:16化はこれから |
| ごんべぇ素材ライブラリ | 座りポーズ受領 | sit_source.png（透過）。表情差分の生成待ち |
| じょんどぅー素材ライブラリ | 座りポーズ受領 | sit_source.png（Tシャツのマークと周りの光をこちらで除去。元は sit_source_with_reel.png）。表情差分の生成待ち |
| 部屋の土台（層に分けた作り直し） | 未着手 | 今の部屋はGeminiのマーク入り・低解像度。テンプレートの背景は仮でこれを使用 |
| 合成エンジン（renderer） | 未着手 | 最初の目標：5秒の口パクMP4 |
| 画面のトーン（色・線・文字） | 完了 | docs/tone.md・renderer/templates/style.py（2026-10-22） |
| 冒頭テンプレート（トーク画面・タイトル・ロゴ） | 完了 | トーク画面メーカー（tools/chat-maker/、ブラウザ）＋ chat.py・title.py。ネオンのタイトルアイコン（assets/brand/logo_neon.png）（2026-10-22） |
| テロップ・エフェクトのプリセット | 未着手 | トーンは style.py を使う |
| 音素材ライブラリ | 未着手 | |
| 15秒テスト動画 | 未着手 | |

| 文字の画面メーカー（バックボーン・名言・処方箋） | 完了 | tools/card-maker/（2026-10-23） |
| 仮の効果音・BGM | 完了（仮） | assets/sound/placeholder/。本番素材が来たら差し替え |
| 1本につなぐ処理 | 完了 | renderer/assemble.py。試作：episodes/ep00-sample（約50秒） |
