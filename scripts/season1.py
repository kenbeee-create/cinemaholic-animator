"""本編（シーズン1）10本の台本・回ごとの見た目・素材プロンプトを、1か所のデータから書き出す。

    python3 scripts/season1.py
出力：
    episodes/epXX-<slug>/script.md   … 台本（構成v2・約45秒）と出典
    episodes/epXX-<slug>/look.json   … 服・部屋（照明の色・窓・小物・ポスター）・挿絵
    docs/season1.md                  … 10本の一覧（悩み・映画・服・必要な素材）
    assets/prompts/batch02.md/.json  … 服装・小物・挿絵のChatGPTプロンプト（まとめ作り バッチ2）

裏話・名言は出典で確認できたものだけ（CLAUDE.md）。配信先と上映時間は書き出し前にFilmarksで確認する。
ep01（ファイト・クラブ）・ep02（her）は作成済み。ここでは ep03〜ep11 の9本と、10本ぶんの服をまとめる。
"""
from __future__ import annotations

import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

STYLE = ("STYLE LOCK — follow exactly, same art style as the attached reference image: flat 2D cartoon cel style, "
         "bold uniform-weight dark brown-black outlines (#1f150f) slightly hand-inked, flat color fills with only ONE simple shadow tone, "
         "NO gradients, NO airbrush, NO glow, NO texture, NO glossy highlights. Muted warm palette. Simple rounded shapes, low detail. "
         "No text, no letters, no logos, no watermarks.")
GONBE = ("Gonbe: brown floppy-eared dog, dark-brown knit beanie (always on), sleepy half-closed bored eyes "
         "(never wide, never teary), big dark nose")
JOHN = ("Johndoe: round fluffy black dog whose big curly fur COMPLETELY hides his eyes, small dark nose, small mouth, short round body")
MAGENTA = "Background: solid flat pure magenta (#FF00FF), no shadow on the background."
EDIT_KEEP = ("Keep his face, eyes, fur, body shape, pose, position, size and canvas EXACTLY identical; change only the clothes. "
             "Same colors style and line thickness. Transparent background.")

# ---------------- 服（10本ぶん） ----------------
# id: (キャラ, 日本語, 英語の服の説明, 使う回)
OUTFITS = {
    "gonbe_hoodie":   ("gonbe", "赤パーカー（いつもの）", None, ["ep02"]),
    "gonbe_suit":     ("gonbe", "くたびれたスーツ＋ゆるいネクタイ", None, ["ep01", "ep03"]),
    "gonbe_jacket":   ("gonbe", "紺のジャケット＋白T（オフィスカジュアル）",
                       "an unstructured navy blazer over a plain white T-shirt, beige chino trousers", ["ep04"]),
    "gonbe_cardigan_shirt": ("gonbe", "白シャツ＋グレーのカーディガン",
                       "a white button-up shirt with a thin grey cardigan, navy trousers", ["ep05"]),
    "gonbe_vest":     ("gonbe", "ワイシャツ＋ニットベスト＋社員証",
                       "a light-blue dress shirt with a brown knit sweater vest and a plain ID badge on a lanyard (blank badge, no text), navy trousers", ["ep06"]),
    "gonbe_knit":     ("gonbe", "マスタードのざっくりニット",
                       "a chunky mustard-yellow cable-knit sweater, dark olive cargo pants", ["ep07"]),
    "gonbe_flannel":  ("gonbe", "ネルシャツ＋黒T", None, ["ep08"]),
    "gonbe_border":   ("gonbe", "ボーダーT＋デニムジャケット",
                       "a navy-and-cream striped long-sleeve T-shirt under a faded denim jacket, black pants", ["ep09"]),
    "gonbe_coverall": ("gonbe", "紺のカバーオール（作業着ふう）",
                       "a plain navy work coverall jacket over a grey T-shirt, navy work pants (no logos, no name tag)", ["ep10"]),
    "gonbe_sweat":    ("gonbe", "古着のくすんだ緑スウェット",
                       "a faded dusty-green vintage crewneck sweatshirt (plain, no print), light-blue jeans", ["ep11"]),
    "johndoe_tee":    ("johndoe", "無地のクリームT（いつもの）", None, ["ep01", "ep02", "ep03", "ep04", "ep06", "ep08", "ep09"]),
    "johndoe_aloha":  ("johndoe", "派手めのアロハシャツ",
                       "a loose short-sleeved Hawaiian shirt with a simple pattern of big mustard and dusty-red flowers (no text), grey shorts", ["ep05"]),
    "johndoe_hoodie": ("johndoe", "マスタードのパーカー", None, ["ep07"]),
    "johndoe_jersey": ("johndoe", "紺のジャージ", None, ["ep10"]),
    "johndoe_turtle": ("johndoe", "黒のタートルネック",
                       "a fitted black turtleneck sweater, grey shorts — like a serious film critic", ["ep11"]),
}

# ---------------- 9本の台本 ----------------
# beats: (秒, 場面, セリフ・テロップ, 動き・音)
EPS = [
 dict(id="ep03", slug="rocky", title="ロッキー", year=1976, director="ジョン・G・アヴィルドセン（脚本・主演 シルヴェスター・スタローン）",
  worry="1. 同期の昇進を、Slackの全体連絡で知った", insight="負けたことより、「勝負に出なかった自分」のほうがつらい",
  gonbe="gonbe_suit", john="johndoe_tee", tint="#b0603a", window="rain", poster="（オリジナル）朝焼けの階段",
  props="Row 1: (1) a pair of worn boxing gloves hanging by laces; (2) a jump rope; (3) a carton of eggs. Row 2: (4) a plain grey sweatshirt folded; (5) a small dumbbell; (6) a plain alarm clock. Row 3: (7) a plain trophy with no text; (8) a hand towel; (9) a pair of old running shoes.",
  cuts=[("cut_slack", "会社のパソコンに昇進のお知らせ、拍手の絵文字が並ぶ（文字は読めない）",
         "a laptop screen in a dim office showing a blank chat window full of tiny confetti and clapping-hand icons (no readable text), Gonbe's paw frozen over the keyboard, in a navy suit sleeve"),
        ("cut_typewriter", "安アパートの夜、タイプライターに向かう影（3日半）",
         "a cheap small apartment at night, a lone figure drawn only as a dark featureless silhouette typing on a typewriter by a desk lamp, crumpled papers everywhere, a TV in the corner glowing (no image on it)")],
  beats=[("0–2", "ごんべぇの顔", "ごんべぇ「おめでとうスタンプ、押す指が重い」（特大）", "沈む・ガーン・低音"),
         ("2–4", "挿絵：昇進のお知らせ", "「同期、課長だって。」", "シュッ"),
         ("4–6", "じょんどぅー → ごんべぇ", "「…悔しい？」／「…悔しがる資格ない。本気出してないし」", "首かしげ／目をそらす"),
         ("6–8", "じょんどぅーの顔", "「…それ、効くやつあるよ」", "乗り出す・カラン→ジャン"),
         ("8–10", "映画紹介", "ロッキー（1976）", "はんこ"),
         ("10–12", "ごんべぇ", "「筋肉のやつでしょ」", "ジト目"),
         ("12–16", "挿絵：タイプライターの影", "「これ書いたの、主演のスタローン本人。ボクシングの試合を見て、3日半で書いた」〔出典1〕", "シュッ"),
         ("16–20", "じょんどぅー → 2ショット", "「脚本を買いたいって言われた。でも“主役は俺じゃなきゃ売らない”」〔出典1〕→「断った」（特大）", "ノる→グッと寄る・低音"),
         ("20–22", "ごんべぇの顔", "「…金、ほしかったろ」", "汗"),
         ("22–25", "じょんどぅー", "「予算は100万ドルくらい。ほぼ賭け」〔出典1〕", "うなずく"),
         ("25–27", "ごんべぇの顔（暗く）", "（無言）", "目を閉じる・ため息の煙"),
         ("27–31", "名言", "「おれはただ、最後まで【立って】いたいんだ」— ロッキー〔出典2〕", "止め"),
         ("31–36", "処方箋", "用量：昇進の通知が来た夜に。／副作用：翌朝、階段を駆け上がりたくなる。", "はんこ「ドン」"),
         ("36–41", "会話", "「…勝てる気しない」／「…ロッキーも、勝つ気で戦ってない」／「…じゃあ何」／「…最後まで立つ気」", "うなずく・キラキラ"),
         ("41–44", "挿絵：本棚のアップ", "「次の処方、わかった？」", "次回ヒントの小物")],
  sources=["スタローンはアリ対ウェプナーの試合を映画館で見て脚本を書き、「3日半で書いた」。脚本だけを買う話を断り、自分が主演する条件にした。予算は約100万ドル — [Philadelphia Magazine「Rocky oral history」](https://www.phillymag.com/ticket/2016/12/03/rocky-oral-history/)",
           "原文 \"All I wanna do is go the distance.\"（試合前夜、エイドリアンに）。訳はこちらでつけた短い引用 — [Rocky (1976) 引用](https://adolfoacosta.substack.com/p/rocky-1976)"]),
 dict(id="ep04", slug="up-in-the-air", title="マイレージ、マイライフ", year=2009, director="ジェイソン・ライトマン",
  worry="7. 4年目、仕事は回せるのに「これ俺じゃなくてよくない？」", insight="ほしいのは評価ではなく、「自分がやった意味」",
  gonbe="gonbe_jacket", john="johndoe_tee", tint="#4a6a8a", window="stars", poster="（オリジナル）雲の上の飛行機",
  props="Row 1: (1) a small carry-on suitcase; (2) a neck pillow; (3) a plain boarding pass with no text. Row 2: (4) a backpack; (5) an airline-style coffee cup, plain; (6) a hotel key card, plain. Row 3: (7) a laptop closed; (8) a toy airplane; (9) a plain luggage tag.",
  cuts=[("cut_shiryou", "誰も見ない会議の資料",
         "a meeting room where everyone's faces are dark featureless silhouettes looking at their phones, while Gonbe (in a navy blazer) holds up a neat chart on a screen that no one is looking at (chart with simple shapes, no text)"),
        ("cut_audition", "廊下で待つ、仕事を失った人たち（影）",
         "a plain office interview room, a single chair, a row of different ordinary people drawn only as dark featureless silhouettes waiting on chairs in a hallway, cold light, quiet and sad")],
  beats=[("0–2", "ごんべぇの顔", "ごんべぇ「仕事できるのに、空っぽ」（特大）", "沈む・どんより・低音"),
         ("2–4", "挿絵：誰も見ない資料", "「完ぺきな資料、誰も見てない」", "シュッ"),
         ("4–6", "じょんどぅー → ごんべぇ", "「…それ、才能では」／「才能の無駄づかい」", "首かしげ／ジト目"),
         ("6–8", "じょんどぅーの顔", "「…それ、効くやつあるよ」", "乗り出す・カラン→ジャン"),
         ("8–10", "映画紹介", "マイレージ、マイライフ（2009）", "はんこ"),
         ("10–13", "じょんどぅー", "「主人公は、出張でクビを言い渡す仕事。夢は1000万マイル」〔出典1〕", "ノる・キラキラ"),
         ("13–15", "ごんべぇ", "「最悪の仕事じゃん」", "目をそらす"),
         ("15–19", "挿絵：廊下で待つ人たち（影）", "「クビを言われる人たち、何人かは本物。最近仕事を失った人を新聞広告で募った」〔出典2〕", "シュッ"),
         ("19–21", "2ショット", "「映ってるのは22人」（特大）〔出典2〕", "ごんべぇビクッ・！・低音"),
         ("21–23", "ごんべぇの顔", "「…演技じゃない顔、か」", "沈む"),
         ("23–26", "じょんどぅー", "「だからこの映画、“仕事って何”が刺さる」", "うなずく"),
         ("26–28", "ごんべぇの顔（暗く）", "（無言）", "目を閉じる・ため息の煙"),
         ("28–32", "名言", "「きみの人生は、どれくらい【重い】？」— ライアン〔出典3〕", "止め"),
         ("32–37", "処方箋", "用量：資料を出した日の夜に。／副作用：リュックの中身を全部出したくなる。", "はんこ「ドン」"),
         ("37–42", "会話", "「…俺のリュック、軽すぎるかも」／「…ポテチ入れとく？」／「いらない」", "ポテチ・ポン"),
         ("42–45", "挿絵：本棚のアップ", "「次の処方、わかった？」", "次回ヒントの小物")],
  sources=["主人公ライアンは1000万マイルを目標にしている — [Wikipedia: Up in the Air (2009 film)](https://en.wikipedia.org/wiki/Up_in_the_Air_(2009_film))",
           "ライトマンは「最近仕事を失った人」を新聞広告で募り、映画には22人が映っている — 同上／[AwardsDaily](https://www.awardsdaily.com/2010/01/11/up-in-the-airs-real-firings/)",
           "原文 \"How much does your life weigh?\"（リュックの講演）。訳はこちらでつけた短い引用 — [Rod Dreher「Carrying That Weight」](https://roddreher.substack.com/p/carrying-that-weight)"]),
 dict(id="ep05", slug="truman-show", title="トゥルーマン・ショー", year=1998, director="ピーター・ウィアー",
  worry="8. 上司のつまらない話に、反射で愛想笑いしている", insight="上司が嫌いなのではなく、「合わせてばかりの自分」が嫌い",
  gonbe="gonbe_cardigan_shirt", john="johndoe_aloha", tint="#7aa0b8", window="none", poster="（オリジナル）空に描かれた雲の壁",
  props="Row 1: (1) a small toy sailboat; (2) a plain studio spotlight; (3) a vintage TV camera on a tripod. Row 2: (4) a plain lunchbox; (5) a sun hat; (6) a small model of a cute pastel house. Row 3: (7) a plain coffee mug; (8) a briefcase; (9) a clapperboard with no writing.",
  cuts=[("cut_aisowarai", "上司の話に笑うごんべぇ（上司は影）",
         "an office break room: Gonbe in a white shirt and grey cardigan forcing a big fake smile with sweat, while his boss is drawn only as a dark featureless silhouette talking with big gestures"),
        ("cut_seaside", "パステルの家が並ぶ、作り物みたいに完ぺきな海辺の町",
         "a too-perfect pastel seaside small town with neat white picket fences and identical cute houses under a clear blue sky, a faint grid line visible in the sky like a painted backdrop, no people, no text")],
  beats=[("0–2", "ごんべぇの顔", "ごんべぇ「今日の俺の笑い、全部ウソ」（特大）", "汗・グッと寄る・低音"),
         ("2–4", "挿絵：愛想笑い", "「“ははは…ですよね〜”」", "シュッ"),
         ("4–6", "じょんどぅー（アロハ）", "「…おれは、ウソで笑ったことない」／「働いてないからな」", "ノる／ジト目"),
         ("6–8", "じょんどぅーの顔", "「…それ、効くやつあるよ」", "乗り出す・カラン→ジャン"),
         ("8–10", "映画紹介", "トゥルーマン・ショー（1998）", "はんこ"),
         ("10–13", "ごんべぇ", "「人生ずっと撮られてた男のやつね」", "首かしげ"),
         ("13–17", "挿絵：パステルの町", "「あの町、セットじゃない。フロリダに本当にある町」〔出典1〕", "シュッ"),
         ("17–19", "2ショット", "「本物」（特大）", "ごんべぇビクッ・！"),
         ("19–23", "じょんどぅー", "「最初の脚本はもっと暗いスリラー。監督が明るく変えた」〔出典2〕", "首を振る"),
         ("23–25", "ごんべぇの顔", "「…明るい方が、こわいかも」", "目をそらす"),
         ("25–28", "じょんどぅー", "「笑顔で囲まれて、ずっと演じさせられる話だから」", "うなずく"),
         ("28–30", "ごんべぇの顔（暗く）", "（無言）", "目を閉じる"),
         ("30–34", "名言", "「会えないときのために、おはよう、こんにちは、【おやすみ】」— トゥルーマン〔出典3〕", "止め"),
         ("34–39", "処方箋", "用量：愛想笑いが3回を超えた日に。／副作用：空の端っこを確かめたくなる。", "はんこ「ドン」"),
         ("39–42", "会話", "「…今の笑い、本物？」／「…ノーカン」", "照れ笑い・赤面"),
         ("42–45", "挿絵：本棚のアップ", "「次の処方、わかった？」", "次回ヒントの小物")],
  sources=["撮影のほとんどはフロリダ州シーサイドで行われた — [Wikipedia: The Truman Show](https://en.wikipedia.org/wiki/The_Truman_Show)",
           "ニコルの最初の脚本はスリラーで、ウィアーは「暗すぎる」と感じた。ウィアーはキャリーを待つために1年待った — 同上",
           "原文 \"In case I don't see ya, good afternoon, good evening, and good night.\"。訳はこちらでつけた短い引用 — 同上"]),
 dict(id="ep06", slug="hidden-figures", title="ドリーム", year=2016, director="セオドア・メルフィ",
  worry="10. AIで5分の資料が、自分の3時間より評価された", insight="仕事を奪われる不安ではなく、「自分にしかできないことが無い」不安",
  gonbe="gonbe_vest", john="johndoe_tee", tint="#c8a050", window="stars", poster="（オリジナル）ロケットと星空",
  props="Row 1: (1) a small toy rocket; (2) a chalkboard with simple chalk curves and dots (no numbers, no letters); (3) a vintage room-sized computer cabinet in miniature with blinking lights. Row 2: (4) a slide rule; (5) a stack of punch cards (blank); (6) a pair of cat-eye glasses. Row 3: (7) a pencil and eraser; (8) a thermos; (9) a globe.",
  cuts=[("cut_ai5min", "AIの5分と、ごんべぇの3時間",
         "an office at night: Gonbe in a light-blue shirt and knit vest, exhausted, surrounded by piles of paper, while on the next desk a sleek laptop glows smugly with a tiny cute robot icon (no text); a big round wall clock"),
        ("cut_ibm", "1960年代の巨大な計算機の部屋（人は影）",
         "a 1960s computing room with huge refrigerator-sized computer cabinets with reels and blinking lights; several women drawn only as dark featureless silhouettes in 1960s dresses studying a thick manual together, warm hopeful light")],
  beats=[("0–2", "ごんべぇの顔", "ごんべぇ「俺の3時間、AIの5分」（特大）", "ガーン・低音"),
         ("2–4", "挿絵：AIと3時間", "「“AI使えば早いじゃん”って」", "シュッ"),
         ("4–6", "じょんどぅー → ごんべぇ", "「…おれはAIに勝ってる」／「何で」／「…ポテチの食べ方」", "ノる／ジト目"),
         ("6–8", "じょんどぅーの顔", "「…それ、効くやつあるよ」", "乗り出す・カラン→ジャン"),
         ("8–10", "映画紹介", "ドリーム（2016）", "はんこ"),
         ("10–13", "じょんどぅー", "「NASAで“計算”が仕事だった女性たちの、実話」", "うなずく"),
         ("13–17", "挿絵：計算機の部屋", "「機械が来たとき、リーダーのドロシーは、プログラミングを独学して、チームに教えた」〔出典1〕", "シュッ"),
         ("17–19", "2ショット", "「奪われる側から、使う側へ」（特大）", "ごんべぇビクッ・！・低音"),
         ("19–23", "じょんどぅー", "「宇宙飛行士も、機械の計算を“あの人が良いと言うなら行く”って」〔出典2〕", "首かしげ"),
         ("23–25", "ごんべぇの顔", "「…最後は人、か」", "沈む"),
         ("25–27", "ごんべぇの顔（暗く）", "（無言）", "目を閉じる・ため息の煙"),
         ("27–31", "名言", "「前に進めそうになるたび、【ゴール】を動かされる」— メアリー〔出典3〕", "止め"),
         ("31–36", "処方箋", "用量：AIに負けた気がした夜に。／副作用：AIに指示を出したくなる。", "はんこ「ドン」"),
         ("36–41", "会話", "「…明日、AIに資料作らせて、俺がチェックする」／「…えらい」／「上から言うな」", "照れ笑い"),
         ("41–44", "挿絵：本棚のアップ", "「次の処方、わかった？」", "次回ヒントの小物")],
  sources=["ドロシー・ヴォーンはコンピュータの導入に備え、FORTRANを独学して部下に教えた。NACA初の黒人の管理職 — [Wikipedia: Dorothy Vaughan](https://en.wikipedia.org/wiki/Dorothy_Vaughan)",
           "ジョン・グレンは打ち上げ前、キャサリン・ジョンソンに計算の確認を頼み「彼女が良いと言うなら行く」と言った（シェタリーの原作による。映画は時間と場所を脚色している） — [Space.com](https://space.com/35218-hidden-figures-when-did-john-glenn-ask-for-the-girl-to-check-the-numbers.html)",
           "原文 \"Every time we get a chance to get ahead, they move the finish line.\"（メアリー・ジャクソン）。訳はこちらでつけた短い引用 — [The Outlook](https://outlook.monmouth.edu/2017/02/hidden-figures-is-an-excellent-discovery/)"]),
 dict(id="ep07", slug="walter-mitty", title="LIFE!", year=2013, director="ベン・スティラー",
  worry="2. 転職サイトのスカウトメールを、半年開けていない", insight="転職が怖いのではなく、「何もない自分」と向き合うのが怖い",
  gonbe="gonbe_knit", john="johndoe_hoodie", tint="#6a8a9a", window="snow", poster="（オリジナル）雪山とユキヒョウ",
  props="Row 1: (1) a vintage film camera; (2) a roll of film negatives; (3) a skateboard (longboard). Row 2: (4) a hiking backpack; (5) a thermos; (6) a paper map, folded, no text. Row 3: (7) a pair of binoculars; (8) a wool hat; (9) a polaroid photo, blank.",
  cuts=[("cut_scout", "通知が溜まったスマホ（読めない）",
         "close-up of a smartphone face up on a bed showing a pile of unread notification bubbles (no readable text, just shapes) glowing in the dark room; Gonbe's paw pushing it away"),
        ("cut_iceland", "氷河と滝の大地を、ロングボードで下る小さな影",
         "a vast Icelandic landscape: a long empty road winding down green mountains toward a glacier and waterfall, a tiny figure on a longboard riding down it, huge sky")],
  beats=[("0–2", "ごんべぇの顔", "ごんべぇ「スカウト、未読のまま半年」（特大）", "汗・低音"),
         ("2–4", "挿絵：溜まった通知", "「開いたら、自分の値段わかっちゃう」", "シュッ"),
         ("4–6", "じょんどぅー → ごんべぇ", "「…おれは開けてる。全部チラシ」／「一緒にすんな」", "ノる／ジト目"),
         ("6–8", "じょんどぅーの顔", "「…それ、効くやつあるよ」", "乗り出す・カラン→ジャン"),
         ("8–10", "映画紹介", "LIFE!（2013）", "はんこ"),
         ("10–13", "じょんどぅー", "「空想ばっかりしてる地味な会社員が、初めて外に出る話」", "首かしげ"),
         ("13–17", "じょんどぅー → 2ショット", "「リメイクの企画から主役が決まるまで17年。候補が何人も入れ替わった」〔出典1〕", "うなずく"),
         ("17–19", "ごんべぇの顔", "「…映画も、なかなか外に出られなかったんだ」", "目をそらす"),
         ("19–23", "挿絵：氷河とロングボード", "「グリーンランドやアフガニスタンの場面、ほとんどアイスランドで撮ってる」〔出典2〕", "シュッ・グッと寄る"),
         ("23–25", "ごんべぇ", "「え、全部？ もう1回見る」", "ビクッ・！"),
         ("25–27", "ごんべぇの顔（暗く）", "（無言）", "目を閉じる"),
         ("27–31", "名言", "「美しいものは、【注目】を求めない」— ショーン〔出典3〕", "止め"),
         ("31–36", "処方箋", "用量：スカウトメールを開く前の夜に。／副作用：知らない駅で降りたくなる。", "はんこ「ドン」"),
         ("36–41", "会話", "「…1通だけ開ける」／「…おう」／（開く）「…チラシだった」", "汗・ガーン"),
         ("41–44", "挿絵：本棚のアップ", "「次の処方、わかった？」", "次回ヒントの小物")],
  sources=["原作はジェームズ・サーバーの1939年の短編。1994年にリメイクが構想され、ジム・キャリー、スピルバーグ（監督）、オーウェン・ウィルソン、マイク・マイヤーズ、サシャ・バロン・コーエンらが入れ替わり、2011年にスティラーに決まった — [Wikipedia: The Secret Life of Walter Mitty (2013 film)](https://en.wikipedia.org/wiki/The_Secret_Life_of_Walter_Mitty_(2013_film))",
           "グリーンランド（ヌーク）やアフガニスタンの場面は、アイスランドで撮影された — 同上",
           "原文 \"Beautiful things don't ask for attention.\"（ショーン・オコンネル）。訳はこちらでつけた短い引用 — [The Stanford Daily](https://stanforddaily.com/2023/03/16/the-adaptations-the-secret-life-of-walter-mitty/)"]),
 dict(id="ep08", slug="la-la-land", title="ラ・ラ・ランド", year=2016, director="デイミアン・チャゼル",
  worry="3. 「いつかサブカルの仕事がしたい」と、誰にも言えない", insight="夢を守っているつもりで、実は夢から逃げている",
  gonbe="gonbe_flannel", john="johndoe_tee", tint="#5a4aa0", window="neon", poster="（オリジナル）夜の丘とベンチ",
  props="Row 1: (1) a small upright piano; (2) a vinyl record; (3) a jazz club neon-shaped lamp with no letters. Row 2: (4) a yellow dress on a hanger; (5) a vintage microphone; (6) a coffee cup. Row 3: (7) a script stapled, blank pages; (8) a pair of tap shoes; (9) a string of warm bulbs.",
  cuts=[("cut_nomikai", "飲み会で「将来どうすんの？」",
         "a noisy izakaya table at night, several coworkers drawn as dark featureless silhouettes laughing, Gonbe in flannel shirt in the middle holding a beer, smiling politely but empty-eyed (still sleepy half-closed eyes)"),
        ("cut_freeway", "渋滞した高速道路のランプで、車の上で踊る人たち（影）",
         "a sunny Los Angeles freeway ramp jammed with colorful cars, many tiny people drawn as simple dark silhouettes dancing on the car roofs, bright blue sky, palm trees, joyful energy, no text")],
  beats=[("0–2", "ごんべぇの顔", "ごんべぇ「夢、言ったら終わる気がする」（特大）", "沈む・低音"),
         ("2–4", "挿絵：飲み会", "「“将来どうすんの？”」「“…まあ、今の会社で”」", "シュッ"),
         ("4–6", "じょんどぅー → ごんべぇ", "「…おれの夢は、ここで映画を見ること」／「叶ってんじゃん」", "ノる／ジト目"),
         ("6–8", "じょんどぅーの顔", "「…それ、効くやつあるよ」", "乗り出す・カラン→ジャン"),
         ("8–10", "映画紹介", "ラ・ラ・ランド（2016）", "はんこ"),
         ("10–13", "じょんどぅー", "「監督がこの脚本を書いたのは2010年。どこもお金を出さなかった」〔出典1〕", "首を振る"),
         ("13–17", "じょんどぅー → 2ショット", "「だから先に、売りやすい『セッション』を撮って、認められてから作った」〔出典1〕", "うなずく"),
         ("17–19", "ごんべぇの顔", "「…夢、遠回りしてるじゃん」", "目をそらす"),
         ("19–22", "挿絵：高速道路のダンス", "「最初の場面は、本物の高速道路を止めて、2日で撮った。ダンサーは100人以上」〔出典2〕", "シュッ・グッと寄る"),
         ("22–24", "ごんべぇ", "「…それは、見たい」", "ビクッ・！"),
         ("24–26", "ごんべぇの顔（暗く）", "（無言）", "目を閉じる"),
         ("26–30", "名言", "「人は、誰かが【夢中】なものを好きになる」— ミア〔出典3〕", "止め"),
         ("30–35", "処方箋", "用量：飲み会で本音を言えなかった夜に。／副作用：好きなものを語りたくなる。", "はんこ「ドン」"),
         ("35–41", "会話", "「…いつか、映画の仕事したい」／「…知ってた」／「…言ったっけ」／「…中学のときから」", "照れ笑い・赤面"),
         ("41–44", "挿絵：本棚のアップ", "「次の処方、わかった？」", "次回ヒントの小物")],
  sources=["チャゼルは2010年に脚本を書いたが、知っている曲のないオリジナルの現代ミュージカルに出資するスタジオはなかった。売りやすい『セッション』を先に撮り、その成功で企画が動いた — [Wikipedia: La La Land](https://en.wikipedia.org/wiki/La_La_Land)",
           "冒頭の場面はロサンゼルスの高速道路の閉鎖したランプで、2日間・100人以上のダンサーで撮影された — 同上",
           "原文 \"People love what other people are passionate about.\"（ミア）。訳はこちらでつけた短い引用 — [KSL.com](https://www.ksl.com/article/news/utah/la-la-land-a-lesson-in-following-our-dreams/43349087)"]),
 dict(id="ep09", slug="frances-ha", title="フランシス・ハ", year=2012, director="ノア・バームバック（脚本 バームバック＆グレタ・ガーウィグ）",
  worry="6. 地元の友達のインスタで、結婚・家・子どもが続けて流れてくる", insight="焦りの正体は「人と比べた遅れ」ではなく、「自分が何をほしいのかわからないこと」",
  gonbe="gonbe_border", john="johndoe_tee", tint="#8a8a8a", window="none", poster="（オリジナル）街を走る女の子の影（モノクロ）",
  props="Row 1: (1) a small mailbox with a blank name slot; (2) a pair of ballet shoes; (3) a paper bag of groceries. Row 2: (4) a wedding invitation card, blank; (5) a smartphone face down; (6) a cardboard moving box, plain. Row 3: (7) a bicycle bell; (8) a coffee cup with lid; (9) a stack of plain envelopes.",
  cuts=[("cut_insta", "スマホに流れる結婚・家・赤ちゃんのアイコン（読めない）",
         "Gonbe in a striped long-sleeve shirt lying on his bed at night holding up a smartphone over his face; floating above it, simple cute icons of a wedding ring, a little house and a baby bottle drift up like bubbles (no text)"),
        ("cut_monochrome", "モノクロの街を、走ってはしゃぐ女の子（影）",
         "a black-and-white city street (grayscale only), a young woman drawn as a simple dark silhouette running and skipping joyfully down the sidewalk past brownstone buildings, motion lines, no text")],
  beats=[("0–2", "ごんべぇの顔", "ごんべぇ「祝福と焦り、同時にくる」（特大）", "沈む・低音"),
         ("2–4", "挿絵：インスタ", "「また結婚報告きた」", "シュッ"),
         ("4–6", "じょんどぅー → ごんべぇ", "「…おれは結婚報告、出す側じゃないし見る側でもない」／「何側だよ」", "首かしげ／ジト目"),
         ("6–8", "じょんどぅーの顔", "「…それ、効くやつあるよ」", "乗り出す・カラン→ジャン"),
         ("8–10", "映画紹介", "フランシス・ハ（2012）", "はんこ"),
         ("10–13", "じょんどぅー", "「友達が先にちゃんとした大人になっていく話。全部モノクロ」", "うなずく"),
         ("13–17", "挿絵：モノクロの街", "「撮ったのは、普通の写真用カメラ。少人数で、目立たずに街を移動して撮った」〔出典1〕", "シュッ"),
         ("17–19", "2ショット", "「映画なのに、身軽」（特大）", "ノる・キラキラ"),
         ("19–23", "じょんどぅー", "「タイトルの“ハ”の意味は、最後の最後にわかる」〔出典2〕", "首かしげ"),
         ("23–25", "ごんべぇ", "「え、なに。…見る」", "ビクッ・！"),
         ("25–27", "ごんべぇの顔（暗く）", "（無言）", "目を閉じる"),
         ("27–31", "名言", "「私、まだちゃんとした【大人】じゃないの」— フランシス〔出典3〕", "止め"),
         ("31–36", "処方箋", "用量：結婚報告に“いいね”を押した夜に。／副作用：意味もなく走りたくなる。", "はんこ「ドン」"),
         ("36–41", "会話", "「…俺もちゃんとした大人じゃない」／「…おれも」／「お前は知ってる」", "照れ笑い"),
         ("41–44", "挿絵：本棚のアップ", "「次の処方、わかった？」", "次回ヒントの小物")],
  sources=["デジタルの白黒で、民生用の写真カメラ（Canon EOS 5D Mark II）で撮影。小さなカメラと最小限の照明で、目立たずに場所を移動できた — [Wikipedia: Frances Ha](https://en.wikipedia.org/wiki/Frances_Ha)",
           "タイトルの意味：フルネームが郵便受けの名札に収まらず、紙を折る（ラストでわかる） — 同上",
           "原文 \"I'm not a real person yet.\"（フランシス）。訳はこちらでつけた短い引用 — [Sheila O'Malley](https://www.sheilaomalley.com/?p=74299)"]),
 dict(id="ep10", slug="perfect-days", title="PERFECT DAYS", year=2023, director="ヴィム・ヴェンダース",
  worry="5. 金曜の夜は意気込むのに、土日は毎回寝て終わる", insight="疲れているのは体ではなく、「何も選ばない毎日」のほう",
  gonbe="gonbe_coverall", john="johndoe_jersey", tint="#5a8a6a", window="stars", poster="（オリジナル）木もれ日",
  props="Row 1: (1) a cassette tape with a blank label; (2) a small cassette player; (3) a paperback book, plain cover. Row 2: (4) a film camera, compact; (5) a small potted seedling; (6) a canned coffee, plain. Row 3: (7) a bicycle; (8) a toilet-cleaning brush and bucket, cute; (9) a stack of developed photos, blank.",
  cuts=[("cut_donichi", "日曜の夜、YouTubeの光と寝ぐせ",
         "Sunday night in a small dark one-room apartment: Gonbe lying on the floor in a crumpled blanket, face lit only by a phone screen (no image), empty snack bags around, the window dark"),
        ("cut_komorebi", "木もれ日を見上げる、作業着の後ろ姿（影）",
         "a quiet Tokyo park at noon, sunlight filtering through tree leaves (komorebi) in soft dappled patterns, a person in a plain navy work uniform seen from behind as a simple silhouette, looking up, holding a small camera")],
  beats=[("0–2", "ごんべぇの顔", "ごんべぇ「土日、記憶がない」（特大）", "沈む・どんより・低音"),
         ("2–4", "挿絵：日曜の夜", "「金曜は“何かしよう”って思うのに」", "シュッ"),
         ("4–6", "じょんどぅー（ジャージ）→ ごんべぇ", "「…おれは毎日が土日」／「うらやましくない」", "ノる／ジト目"),
         ("6–8", "じょんどぅーの顔", "「…それ、効くやつあるよ」", "乗り出す・カラン→ジャン"),
         ("8–10", "映画紹介", "PERFECT DAYS（2023）", "はんこ"),
         ("10–13", "じょんどぅー", "「東京のトイレ清掃員の、同じような毎日の話」", "うなずく"),
         ("13–15", "ごんべぇ", "「…地味そう」", "ジト目"),
         ("15–19", "挿絵：木もれ日", "「主演の役所広司は、これでカンヌの男優賞」〔出典1〕", "シュッ"),
         ("19–21", "2ショット", "「撮影は、たった16日」（特大）〔出典2〕", "ごんべぇビクッ・！・低音"),
         ("21–25", "じょんどぅー", "「主人公の名前“平山”も、偶然じゃないって監督が言ってる」〔出典3〕", "首かしげ"),
         ("25–27", "ごんべぇの顔（暗く）", "（無言）", "目を閉じる"),
         ("27–31", "名言", "「今度は今度、【今】は今」— 平山〔出典4〕", "止め"),
         ("31–36", "処方箋", "用量：金曜の夜、寝る前に。／副作用：土曜の朝、空を見上げたくなる。", "はんこ「ドン」"),
         ("36–41", "会話", "「…土曜、カセット買いに行く」／「…おれも行く」／「お前は来なくていい」", "照れ笑い"),
         ("41–44", "挿絵：本棚のアップ", "「次の処方、わかった？」", "次回ヒントの小物")],
  sources=["役所広司は第76回カンヌ国際映画祭で男優賞 — [nippon.com](https://www.nippon.com/en/japan-topics/c030250/wim-wenders-and-yakusho-koji-take-film-to-the-toilet-with-perfect-days.html)",
           "16日間の撮影スケジュールで撮られた — [The Guardian（PressReader）](https://www.pressreader.com/usa/the-guardian-usa/20240212/282011857270154)",
           "ヴェンダース「小津が最後の映画を撮ってから60年後に東京で撮った。主人公の名前が平山なのは偶然ではない」 — [Festival de Cannes](https://www.festival-cannes.com/en/2023/perfect-days-interview-with-wim-wenders/)",
           "平山が姪のニコに言うセリフ（自転車の場面）。短く1つの引用 — [映画.com レビュー](https://eiga.com/movie/99306/review/04855188/)"]),
 dict(id="ep11", slug="cinema-paradiso", title="ニュー・シネマ・パラダイス", year=1988, director="ジュゼッペ・トルナトーレ",
  worry="4. 学生時代に好きだった映画を見返したら、何も感じなかった", insight="好きなものを失ったのではなく、「感動できる自分」を失っている",
  gonbe="gonbe_sweat", john="johndoe_turtle", tint="#c87a3a", window="stars", poster="（オリジナル）古い映画館と星空",
  props="Row 1: (1) an old film projector; (2) a film reel; (3) a strip of film. Row 2: (4) a small bicycle; (5) a vintage movie ticket, blank; (6) a cinema seat, single. Row 3: (7) an old radio; (8) a box of old photos; (9) a plain envelope tied with string.",
  cuts=[("cut_netetu", "名作を再生したまま、スマホを見ているごんべぇ",
         "Gonbe in a faded green sweatshirt on his sofa at night, a TV in front of him playing (only soft light, no image), but he is looking down at his phone, bored; a cold blue room"),
        ("cut_projection", "映写室の小窓から、光の帯が客席へのびる",
         "inside a tiny old projection booth: a vintage film projector throwing a bright beam through a small square window into a dark Sicilian village cinema below, a little boy and an old man drawn as warm silhouettes watching together")],
  beats=[("0–2", "ごんべぇの顔", "ごんべぇ「好きだった映画で、寝た」（特大）", "沈む・ガーン・低音"),
         ("2–4", "挿絵：スマホを見ながら", "「…感動の仕方、忘れたかも」", "シュッ"),
         ("4–6", "じょんどぅー（黒タートル）→ ごんべぇ", "「…今日は、ちゃんとした話をする」／「服で言うな」", "うなずく／ジト目"),
         ("6–8", "じょんどぅーの顔", "「…それ、効くやつあるよ」", "乗り出す・カラン→ジャン"),
         ("8–10", "映画紹介", "ニュー・シネマ・パラダイス（1988）", "はんこ"),
         ("10–13", "じょんどぅー", "「映画好きの少年と、映写技師のおじさんの話」", "うなずく"),
         ("13–17", "じょんどぅー → 2ショット", "「イタリアで公開したとき、2回ともコケた」〔出典1〕", "首を振る"),
         ("17–20", "じょんどぅー", "「短く切り直して、カンヌで賞。アカデミー賞まで」〔出典1〕", "ノる・キラキラ"),
         ("20–22", "ごんべぇ", "「…一回コケても、いいんだ」", "目をそらす"),
         ("22–25", "挿絵：映写室の光", "「撮ったのは、監督の地元の町」〔出典2〕", "シュッ"),
         ("25–27", "ごんべぇの顔（暗く）", "（無言）", "目を閉じる"),
         ("27–31", "名言", "「何をするにしても、それを【愛せ】」— アルフレード〔出典3〕", "止め"),
         ("31–36", "処方箋", "用量：昔好きだった映画で寝た夜に。／副作用：最後の5分で、たぶん泣く。", "はんこ「ドン」"),
         ("36–42", "会話", "「…中学のとき、2人で見たよな」／「…覚えてる」／「…寝たけどな、お前」", "照れ笑い・赤面"),
         ("42–45", "挿絵：本棚のアップ", "「次の処方、わかった？」", "次回ヒントの小物")],
  sources=["イタリアでは155分で公開され、2度とも興行的に失敗。124分に短くした版が1989年のカンヌで受賞し、アカデミー外国語映画賞を受賞 — [Wikipedia: Cinema Paradiso](https://en.wikipedia.org/wiki/Cinema_Paradiso)",
           "撮影は監督トルナトーレの地元、シチリアのバゲーリア — 同上",
           "原文 \"Whatever you end up doing, love it.\"（アルフレード）。訳はこちらでつけた短い引用 — [Winchester City Voices](https://www.wincityvoices.org/reel-classics-cinema-paradiso/)"]),
]


def write_scripts():
    for e in EPS:
        d = os.path.join(ROOT, "episodes", f"{e['id']}-{e['slug']}")
        os.makedirs(d, exist_ok=True)
        go, jo = OUTFITS[e["gonbe"]][1], OUTFITS[e["john"]][1]
        L = [f"# {e['id']} {e['title']}（構成v2・約45秒）",
             f"悩み（ストック）：**{e['worry']}**", f"インサイト：{e['insight']}",
             f"処方：{e['title']}（{e['year']}・{e['director']}）　カルテ：処方 No.{int(e['id'][2:]):02d}",
             "状態：**台本（オーナー承認待ち）**。裏話・名言は事実確認ずみ（下の出典）。配信先・上映時間は書き出し前にFilmarksで確認", "",
             "## 見た目", f"- ごんべぇ：{go}　／　じょんどぅー：{jo}",
             f"- 部屋：照明の色 `{e['tint']}`・窓 `{e['window']}`・壁のポスター {e['poster']}",
             "- 小物：この回の小物シート（バッチ2）から2〜3個", "",
             "| 秒 | 場面 | セリフ・テロップ | 動き・音 |", "|---|---|---|---|"]
        L += [f"| {a} | {b} | {c} | {x} |" for a, b, c, x in e["beats"]]
        L += ["", "## 出典（事実確認）"] + [f"{i + 1}. {s}" for i, s in enumerate(e["sources"])]
        L += ["", "## メモ", "- 監督・作り手・俳優は描かない（挿絵では影・シルエット）",
              "- 名言の訳はこちらでつけた短い引用（1つまで）。字幕の訳とは違う場合がある"]
        open(os.path.join(d, "script.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")
        look = {"gonbe_outfit": e["gonbe"], "johndoe_outfit": e["john"],
                "room": {"tint": e["tint"], "tintA": 0.14, "window": e["window"], "poster": e["poster"],
                         "props_sheet": f"sheet_props_{e['id']}.png"},
                "cutaways": [{"file": f"cutaways/{c[0][4:]}_{e['id']}.png", "label": c[1]} for c in e["cuts"]]}
        json.dump(look, open(os.path.join(d, "look.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def write_prompts():
    items = []
    # 服（ごんべぇ・じょんどぅー）
    for oid, (who, ja, en, eps) in OUTFITS.items():
        if not en:
            continue
        attach = ["gonbe/sit_source.png"] if who == "gonbe" else ["johndoe/sit_source.png"]
        extra = " Keep his dark-brown knit beanie ON." if who == "gonbe" else " His eyes must stay completely hidden by the fur."
        items.append(dict(id=f"O-{oid}", group="服", title=f"{'ごんべぇ' if who == 'gonbe' else 'じょんどぅー'}：{ja}（{'・'.join(eps)}）",
                          chat="new" if oid in ("gonbe_jacket", "johndoe_aloha") else ("same:O-gonbe_jacket" if who == "gonbe" else "same:O-johndoe_aloha"),
                          attach=attach, save=f"{oid}.png", post=f"assets/characters/{who}/outfits/{oid.split('_', 1)[1]}/ に置き、頭と体を分けるリグを作る",
                          prompt=f"Edit the ORIGINAL attached image (create an edited image). Change ONLY his clothes: {en}.{extra} {EDIT_KEEP}"))
    # 回ごとの小物シートと挿絵
    for e in EPS:
        items.append(dict(id=f"P-{e['id']}", group="小物", title=f"{e['id']} {e['title']} の小物9個", chat="new" if e is EPS[0] else f"same:P-{EPS[0]['id']}",
                          attach=["keyvisual.png"], save=f"sheet_props_{e['id']}.png", post="python3 scripts/slice_sheet.py <画像> props 名前:表示名 …",
                          prompt=f"{STYLE} Make a sprite sheet of 9 small props for the apartment room in the reference image, front view, no characters, no text or labels on anything. Arrange them in a clean 3x3 grid, each centered in its own cell, same scale, wide empty space between them. Square image. {MAGENTA} {e['props']}"))
        for c in e["cuts"]:
            items.append(dict(id=f"C-{e['id']}-{c[0][4:]}", group="挿絵", title=f"{e['id']} {e['title']}：{c[1]}", chat="new" if e is EPS[0] and c is e["cuts"][0] else f"same:C-{EPS[0]['id']}-{EPS[0]['cuts'][0][0][4:]}",
                              attach=["keyvisual.png"], save=f"{c[0]}_{e['id']}.png", post=f"assets/cutaways/{c[0][4:]}_{e['id']}.png",
                              prompt=f"{STYLE} Vertical 9:16 full illustration with a complete background, main subject in the middle 80% of the frame, nothing important in the bottom-right corner. Real people are never depicted: anyone who is not Gonbe or Johndoe is a dark featureless silhouette. ({GONBE}.) Scene: {c[2]}."))
    os.makedirs(os.path.join(ROOT, "assets/prompts"), exist_ok=True)
    json.dump({"style_lock": STYLE, "items": items}, open(os.path.join(ROOT, "assets/prompts/batch02.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    n = {g: sum(1 for i in items if i["group"] == g) for g in ("服", "小物", "挿絵")}
    L = ["# 素材のまとめ作り（バッチ2・本編10本ぶん）", "",
         f"全{len(items)}本（服 {n['服']}・小物シート {n['小物']}・挿絵 {n['挿絵']}）。上から順に。服はキャラごとに同じチャットで続けると、体の形がそろいやすい。", "",
         "## 使い方", "",
         "- 服：座りの絵（`gonbe/sit_source.png` か `johndoe/sit_source.png`）を添付して、**毎回「元の画像を編集」**と頼む（前に作った服をさらに編集しない）",
         "- 小物・挿絵：`keyvisual.png` を添付。小物は無地のマゼンタ背景で頼む（自動で切り抜く）",
         "- できた画像は保存名でClaudeに送る。切り抜き・リグ作り・登録はClaude", "",
         "| ID | 種類 | 内容 | チャット | 保存名 |", "|---|---|---|---|---|"]
    for i in items:
        ch = "新しいチャット" if i["chat"] == "new" else i["chat"].replace("same:", "") + "と同じ"
        L.append(f"| {i['id']} | {i['group']} | {i['title']} | {ch} | `{i['save']}` |")
    L.append("")
    for i in items:
        ch = "新しいチャット" if i["chat"] == "new" else i["chat"].replace("same:", "") + " と同じチャットで続けて"
        L += [f"## {i['id']} {i['title']}", f"チャット：{ch}　添付：" + "・".join(f"`{a}`" for a in i["attach"]) + f"　保存名：`{i['save']}`", "",
              "```", i["prompt"], "```", f"あとの処理：{i['post']}", ""]
    open(os.path.join(ROOT, "assets/prompts/batch02.md"), "w", encoding="utf-8").write("\n".join(L))
    return items


def write_index():
    rows = [("ep01", "fight-club", "ファイト・クラブ", "“みんな我慢してる”で片づけられる", "gonbe_suit", "johndoe_tee", "作成済み・下書き動画あり"),
            ("ep02", "her", "her／世界でひとつの彼女", "9. 今日の会話、レジだけ", "gonbe_hoodie", "johndoe_tee", "作成済み・下書き動画あり")]
    rows += [(e["id"], e["slug"], e["title"], e["worry"], e["gonbe"], e["john"], "台本（承認待ち）") for e in EPS]
    L = ["# シーズン1（本編10本＋試作）", "",
         "構成v2（`docs/format-v2.md`）。悩みはごんべぇのストック10個（具体的な場面とインサイト）から。順番は「仕事の我慢」→「好きなことを話せる相手」→「夢」→「好きだったもの」へ深くなる。", "",
         "| 回 | 映画 | 悩み | ごんべぇの服 | じょんどぅーの服 | 状態 |", "|---|---|---|---|---|---|"]
    for r in rows:
        L.append(f"| {r[0]} | [{r[2]}](../episodes/{r[0]}-{r[1]}/{'script_v2.md' if r[0] == 'ep01' else 'script.md'}) | {r[3]} | {OUTFITS[r[4]][1]} | {OUTFITS[r[5]][1]} | {r[6]} |")
    L += ["", "## お約束（毎回）",
          "- 0秒：ごんべぇの本音の一撃（特大）→ 挿絵のあるある → じょんどぅーの噛み合わない返し",
          "- 「…それ、効くやつあるよ」→ カラン→ジャン → 映画紹介",
          "- 裏話は事実確認ずみのものだけ。1つは「もう1回見たくなる」事実",
          "- 名言で止める → 処方箋（用量・副作用はボケ）→ 2人の会話のオチ →「次の処方、わかった？」",
          "", "## 必要な素材", "- 服・回ごとの小物・挿絵のプロンプト：`assets/prompts/batch02.md`（まとめページの「まとめ作り バッチ2」）",
          "- 共通の素材（記号・表情・映画館など）：`assets/prompts/batch01.md`"]
    open(os.path.join(ROOT, "docs/season1.md"), "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    write_scripts()
    items = write_prompts()
    write_index()
    print(f"台本 {len(EPS)}本・プロンプト {len(items)}本・docs/season1.md を書き出しました")
