"""ChatGPTでまとめて素材を作るための「プロンプトの順番待ちリスト」を書き出す。

    python3 scripts/prompt_batch.py
出力：
    assets/prompts/batch01.json … Claude がブラウザで ChatGPT を操作するときに上から順に使う
    assets/prompts/batch01.md   … 人が読む・手でコピペする用（まとめページにも載る）

絵柄のルール（STYLE LOCK）は docs/style-bible.md と同じ文章。全部のプロンプトの頭に付ける。
"""
from __future__ import annotations

import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

STYLE = """STYLE LOCK — follow exactly, same art style as the attached reference image:
- Flat 2D cartoon cel style. Bold, uniform-weight dark brown-black outlines (#1f150f), slightly hand-inked.
- Flat color fills with only ONE simple shadow tone. NO gradients, NO airbrush, NO glow, NO bloom, NO texture, NO glossy highlights, NO lens effects.
- Muted warm palette: browns, dark brown, mustard, dusty red, cream, olive green, navy.
- Simple rounded shapes, low detail. No tiny patterns, no text, no logos, no watermarks, no signatures."""
MAGENTA = "Background: solid flat pure magenta (#FF00FF), no shadow on the background, no floor."
SHEET = ("Arrange them in a clean 3x3 grid, each centered in its own cell, all at the same scale, separated by wide empty space. "
         "Square image. " + MAGENTA)

GONBE = ("Gonbe: brown floppy-eared dog, dark-brown knit beanie (always on), red hoodie, navy pants, "
         "his usual sleepy half-closed bored eyes (never wide, never teary, never curved ^^), big dark nose.")
JOHN = ("Johndoe: round fluffy black dog, big curly fur that COMPLETELY hides his eyes (eyes never visible), "
        "small dark nose, small mouth, plain cream T-shirt, grey shorts, short round body.")

EDIT_KEEP = ("Keep everything else exactly identical: same pose, same position, same size, same canvas, "
             "same colors, same line thickness. Keep the transparent background.")
POSE_KEEP = ("Keep his design exactly the same as the attached image: same face, same proportions, same colors, "
             "same thick outlines. Full body visible, character about 75% of the image height. Vertical 2:3 image. " + MAGENTA)

ITEMS = []


def add(id, group, pri, title, attach, prompt, save, post, chat="new", note=""):
    ITEMS.append(dict(id=id, group=group, priority=pri, title=title, chat=chat, attach=attach,
                      prompt=prompt.strip(), save=save, post=post, note=note))


# ---------------- A. 表情（座りの絵を編集。位置はそのまま） ----------------
GS = ["gonbe/sit_source.png"]
add("A1", "表情", 1, "ごんべぇ 照れ笑い（口を閉じて）", GS, f"""
Edit the attached image. Keep his usual sleepy half-closed eyes EXACTLY as they are (same eye shape, same eyelids) — do not close or curve the eyes.
Change ONLY: a small embarrassed smirk — one corner of the closed mouth slightly raised, a light pink blush on the cheeks, pupils looking slightly to the side.
{EDIT_KEEP}""", "gonbe_tere.png", "表情の部品にする（目・口・頬を切り出し）→ parts/eyes_tere.png")
add("A2", "表情", 1, "ごんべぇ ため息", GS, f"""
Edit the attached image. Keep his usual eye SHAPE (sleepy, half-closed) — do NOT make the eyes bigger, rounder or teary, and do not close them into curves.
Make the upper eyelids droop a little lower, as if exhausted, pupils looking slightly down.
Change the mouth to a sigh: lips slightly parted, a small open mouth breathing out.
{EDIT_KEEP}""", "gonbe_sigh.png", "parts/eyes_sigh.png ＋ 口", chat="same:A1")
add("A3", "表情", 1, "ごんべぇ にやけ（得意げ）", GS, f"""
Edit the attached image. Keep his usual sleepy half-closed eyes exactly — same shape — but make the pupils glance sideways with a smug look.
Change ONLY the mouth: a smug, self-satisfied grin — wide closed-mouth smirk stretching to one side.
{EDIT_KEEP}""", "gonbe_niyake.png", "表情の部品", chat="same:A1")
add("A4", "表情", 1, "ごんべぇ 口ぽかん（あぜん）", GS, f"""
Edit the attached image. Keep his usual sleepy half-closed eye shape, but make the pupils tiny dots, as if stunned.
Change ONLY the mouth: dropped wide open in disbelief, a tall oval mouth showing a dark inside and a bit of tongue.
{EDIT_KEEP}""", "gonbe_pokan.png", "表情の部品", chat="same:A1")
add("A5", "表情", 2, "ごんべぇ イラッ（歯を食いしばる）", GS, f"""
Edit the attached image. Keep his usual sleepy half-closed eye shape, but lower the brows into an annoyed frown.
Change ONLY the mouth: clenched teeth in a tight, wide grimace.
{EDIT_KEEP}""", "gonbe_ira.png", "表情の部品", chat="same:A1")
add("A6", "表情", 2, "ごんべぇ 「は？」（片方の口角が下がる）", GS, f"""
Edit the attached image. Keep his usual sleepy half-closed eyes, one brow raised in skeptical disbelief.
Change ONLY the mouth: a small crooked open mouth as if saying "huh?", one corner pulled down.
{EDIT_KEEP}""", "gonbe_ha.png", "表情の部品", chat="same:A1")
JS = ["johndoe/sit_source.png"]
add("A7", "表情", 2, "じょんどぅー にやり（口だけ）", JS, f"""
Edit the attached image. His eyes must stay completely hidden by the fur.
Change ONLY the mouth: a small smug closed-mouth smile, curved up like a cat mouth (ω shape).
{EDIT_KEEP}""", "johndoe_niyari.png", "口の部品 parts/mouth_niyari.png")
add("A8", "表情", 2, "じょんどぅー への字口", JS, f"""
Edit the attached image. His eyes must stay completely hidden by the fur.
Change ONLY the mouth: a small sulky downturned mouth (upside-down U shape).
{EDIT_KEEP}""", "johndoe_henoji.png", "口の部品", chat="same:A7")

# ---------------- B. ポーズ（全身の新しい絵） ----------------
add("B1", "ポーズ", 1, "ごんべぇ 立ち姿（入ってくる）", GS, f"""
{STYLE}

Draw the character from the attached image ({GONBE}) as a STANDING full-body pose, walking in from the left and just stopping, as if entering a friend's room.
Pose: body facing slightly to the right, one paw raised casually in greeting, the other paw in the hoodie pocket, mouth slightly open. A small plain plastic convenience-store bag hanging from his wrist.
{POSE_KEEP}""", "gonbe_stand.png", "切り抜き → assets/characters/gonbe/stand.png（スタジオの灰色の代役が本物になる）")
add("B2", "ポーズ", 1, "ごんべぇ ソファに突っ伏す（フック用）", GS, f"""
{STYLE}

Draw the character from the attached image ({GONBE}) lying face-down flat on his stomach, completely exhausted, arms limp at his sides, legs straight, as if he just collapsed onto a sofa. Seen from the side, head turned toward the viewer with a dead-tired face. Do not draw the sofa.
{POSE_KEEP}""", "gonbe_flop.png", "ポーズの部品")
add("B3", "ポーズ", 1, "ごんべぇ 床で大の字（「…死んでる？」用）", GS, f"""
{STYLE}

Draw the character from the attached image ({GONBE}) lying flat on his back spread-eagle on the floor, seen from directly above, arms and legs stretched out, staring blankly at the ceiling. Do not draw the floor.
Square image, character fills about 80% of the image. {MAGENTA}""", "gonbe_daiji.png", "ポーズの部品（真上から）")
add("B4", "ポーズ", 2, "ごんべぇ 頭を抱える（座り）", GS, f"""
{STYLE}

Draw the character from the attached image ({GONBE}) sitting in the same position as the attached image, but holding his head with both paws in despair, beanie slightly pushed, eyes still sleepy half-closed, mouth a wobbly line.
{POSE_KEEP}""", "gonbe_atama.png", "ポーズの部品")
add("B5", "ポーズ", 1, "ごんべぇ スマホを見て固まる（座り）", GS, f"""
{STYLE}

Draw the character from the attached image ({GONBE}) sitting in the same position as the attached image, holding a plain smartphone in both paws close to his face (the screen faces him, we see the back of the phone), frozen, a single sweat drop.
{POSE_KEEP}""", "gonbe_sumaho.png", "ポーズの部品（上司のLINEを見て固まる小ネタ）")
add("B6", "ポーズ", 2, "ごんべぇ 体育座りでいじける", GS, f"""
{STYLE}

Draw the character from the attached image ({GONBE}) sitting on the floor hugging his knees, sulking, seen from a slight side angle, eyes sleepy half-closed looking down.
{POSE_KEEP}""", "gonbe_taiiku.png", "ポーズの部品")
add("B7", "ポーズ", 2, "ごんべぇ 歩き2コマ（横向き）", GS, f"""
{STYLE}

Draw TWO walking frames of the character from the attached image ({GONBE}), side view facing right, hands in hoodie pocket, lazy slouched walk. Frame 1: left foot forward. Frame 2: right foot forward. Place the two frames side by side with wide space between them, same size, same height. Landscape 3:2 image. {MAGENTA}""",
    "gonbe_walk.png", "シート切り抜き（2個）")
add("B8", "ポーズ", 1, "じょんどぅー DVDを差し出す（処方のポーズ）", JS, f"""
{STYLE}

Draw the character from the attached image ({JOHN}) sitting in the same position as the attached image, but holding out a plain DVD case toward the left with one paw (blank cover, no text, no art), like a doctor handing over medicine. Eyes stay hidden by the fur.
{POSE_KEEP}""", "johndoe_dvd.png", "ポーズの部品（処方の合図）")
add("B9", "ポーズ", 1, "じょんどぅー ポテチを食べる（座り）", JS, f"""
{STYLE}

Draw the character from the attached image ({JOHN}) sitting in the same position as the attached image, holding an open plain potato-chip bag (no logo, no text) in one paw and a chip near his mouth with the other. Eyes stay hidden by the fur.
{POSE_KEEP}""", "johndoe_chips.png", "ポーズの部品", chat="same:B8")
add("B10", "ポーズ", 2, "じょんどぅー 寝転がって本を読む", JS, f"""
{STYLE}

Draw the character from the attached image ({JOHN}) lying on his stomach, reading a plain hardcover book (blank cover), legs kicked up behind him, relaxed. Side view. Eyes stay hidden by the fur.
{POSE_KEEP}""", "johndoe_yomu.png", "ポーズの部品", chat="same:B8")
add("B11", "ポーズ", 2, "じょんどぅー 振り向き（後ろ姿→こっち）", JS, f"""
{STYLE}

Draw the character from the attached image ({JOHN}) standing with his back to the viewer, turning his head over his shoulder to look back toward the viewer. Eyes stay hidden by the fur.
{POSE_KEEP}""", "johndoe_furimuki.png", "ポーズの部品", chat="same:B8")

# ---------------- C. 服違い（座りのまま服だけ） ----------------
add("C1", "服", 1, "ごんべぇ くたびれたスーツ（仕事の回）", GS, f"""
Edit the attached image. Change ONLY his clothes: a slightly wrinkled navy suit jacket and trousers, white shirt, loose dark-red necktie pulled down. Keep his dark-brown knit beanie ON. Keep his face, eyes, fur and body shape exactly identical.
{EDIT_KEEP}""", "gonbe_suit.png", "assets/characters/gonbe/outfits/suit/")
add("C2", "服", 2, "ごんべぇ 無地バンドT＋ネルシャツ", GS, f"""
Edit the attached image. Change ONLY his clothes: an open mustard-and-brown flannel shirt over a plain black T-shirt (no print, no text), the same navy pants. Keep his beanie, face, eyes, fur and body shape exactly identical.
{EDIT_KEEP}""", "gonbe_flannel.png", "outfits/flannel/", chat="same:C1")
add("C3", "服", 2, "ごんべぇ 大きめカーディガン", GS, f"""
Edit the attached image. Change ONLY his clothes: an oversized olive-green knit cardigan over a cream T-shirt, the same navy pants. Keep his beanie, face, eyes, fur and body shape exactly identical.
{EDIT_KEEP}""", "gonbe_cardigan.png", "outfits/cardigan/", chat="same:C1")
add("C4", "服", 2, "じょんどぅー 部屋着ジャージ", JS, f"""
Edit the attached image. Change ONLY his clothes: a faded navy track jacket (zipped halfway, no logo) over the plain cream T-shirt, grey shorts. Eyes stay hidden. Keep his fur, face and body shape exactly identical.
{EDIT_KEEP}""", "johndoe_jersey.png", "outfits/jersey/")
add("C5", "服", 2, "じょんどぅー 冬のパーカー", JS, f"""
Edit the attached image. Change ONLY his clothes: a thick mustard hoodie (no print), grey sweatpants. Eyes stay hidden. Keep his fur, face and body shape exactly identical.
{EDIT_KEEP}""", "johndoe_hoodie.png", "outfits/hoodie/", chat="same:C4")

# ---------------- D. 挿絵（脳内・あるある・裏話の1枚絵。9:16） ----------------
KV = ["keyvisual.png"]
CUT = "Vertical 9:16 full illustration with a complete background, main subject in the middle 80% of the frame, nothing important in the bottom-right corner."
add("D1", "挿絵", 1, "会議室で詰められるごんべぇ（上司は影）", KV, f"""
{STYLE}

{CUT}
Scene: a small dull office meeting room. {GONBE} wearing a wrinkled navy suit and loose red tie (beanie still on), sitting small at the table, shoulders hunched, sweating. Across the table, his boss is drawn ONLY as a big dark featureless silhouette leaning forward and pointing. Fluorescent cold light. Comic, slightly exaggerated.""",
    "cut_kaigi.png", "assets/cutaways/kaigi.png")
add("D2", "挿絵", 1, "満員電車でつぶれるごんべぇ", KV, f"""
{STYLE}

{CUT}
Scene: a packed morning commuter train. {GONBE} in a navy suit (beanie still on) squashed between faceless grey silhouette passengers, face pressed flat, dead eyes (still his half-closed sleepy shape). Comic.""",
    "cut_densha.png", "assets/cutaways/densha.png", chat="same:D1")
add("D3", "挿絵", 2, "深夜のオフィスでひとり残業", KV, f"""
{STYLE}

{CUT}
Scene: a dark empty office at night, only one desk lamp on. {GONBE} in a suit, alone at his desk in front of a glowing blank monitor (no text on screen), cold coffee cup, slumped.""",
    "cut_zangyo.png", "assets/cutaways/zangyo.png", chat="same:D1")
add("D4", "挿絵", 2, "夜のコンビニ前で缶コーヒー", KV, f"""
{STYLE}

{CUT}
Scene: night, outside a small generic convenience store (no logos, no signs with text), {GONBE} in his red hoodie crouching by the wall holding a plain can of coffee, staring at nothing.""",
    "cut_konbini.png", "assets/cutaways/konbini.png", chat="same:D1")
add("D5", "挿絵", 2, "日曜の夜、ベッドで天井を見る", KV, f"""
{STYLE}

{CUT}
Scene: a small one-room apartment at night, {GONBE} lying on his back in bed under a blanket, staring at the ceiling with dread (Sunday night before Monday). A plain alarm clock on the floor.""",
    "cut_nichiyou.png", "assets/cutaways/nichiyou.png", chat="same:D1")
add("D6", "挿絵", 2, "スマホで同期の結婚報告（画面は見せない）", KV, f"""
{STYLE}

{CUT}
Scene: {GONBE} in his red hoodie sitting alone on a convenience-store bench at night, looking at his smartphone (we see the back of the phone), soft light on his face, a complicated half-smile. Tiny cartoon hearts and confetti floating up from the phone (no text).""",
    "cut_kekkon.png", "assets/cutaways/kekkon.png", chat="same:D1")
add("D7", "挿絵", 1, "学生時代のごんべぇ、レンタル店でDVDを選ぶ（回想）", KV, f"""
{STYLE}

{CUT}
Scene: a cozy old video rental shop with shelves of plain DVD/VHS cases (blank covers, no titles). A younger {GONBE} (same beanie, school uniform blazer instead of hoodie) holding several cases, happy in his own sleepy way.""",
    "cut_rental.png", "assets/cutaways/rental.png", chat="same:D1")
add("D8", "挿絵", 2, "映画館の暗い客席（スクリーンは無地）", KV, f"""
{STYLE}

{CUT}
Scene: inside a dark old movie theater seen from behind the seats, a glowing plain white screen, {GONBE} and {JOHN} sitting side by side seen from behind, silhouettes lit by the screen.""",
    "cut_eigakan.png", "assets/cutaways/eigakan.png", chat="same:D1")
add("D9", "挿絵", 1, "撮影現場のシルエット（裏話用・人物は影）", KV, f"""
{STYLE}

{CUT}
Scene: a film set seen from behind the camera: a big old film camera on a tripod, a director's chair (blank, no name), studio lights, and several crew members drawn ONLY as dark featureless silhouettes. Moody, warm light. No recognizable real people.""",
    "cut_satsuei.png", "assets/cutaways/satsuei.png", chat="same:D1")
add("D10", "挿絵", 1, "作り手の散らかった机（裏話用）", KV, f"""
{STYLE}

{CUT}
Scene: a messy writer's desk at night seen from above at an angle: an old typewriter, crumpled paper balls, a blank notebook, a coffee mug, film reels and a desk lamp. No text on any paper.""",
    "cut_tsukue.png", "assets/cutaways/tsukue.png", chat="same:D1")
add("D11", "挿絵", 1, "腫れた顔で出社するシルエット（裏話用）", KV, f"""
{STYLE}

{CUT}
Scene: an office floor; a figure drawn as a dark featureless silhouette with a visibly swollen, bandaged face walks in; coworkers (also faceless silhouettes) at their desks keep staring at their monitors, ignoring him. Comic and a bit sad. No recognizable real people.""",
    "cut_shussha.png", "assets/cutaways/shussha.png", chat="same:D1", note="ファイト・クラブの回の裏話用（事実確認が通った場合だけ使う）")

# ---------------- E. 記号シート ----------------
add("E1", "記号", 1, "記号シート①（汗・怒りマーク など9個）", KV, f"""
{STYLE}

Make a sprite sheet of 9 Japanese manga emotion symbols for this cartoon. No characters, only the symbols. {SHEET}
Row 1: (1) a single sweat drop, pale blue; (2) a dusty-red anger vein cross mark; (3) a block of 6 vertical gloomy lines, dark blue-gray.
Row 2: (4) a small dark wavy gloom cloud with drips; (5) two music notes; (6) a cluster of three mustard-yellow sparkles.
Row 3: (7) a bold exclamation mark in mustard yellow; (8) a bold question mark in cream; (9) a small puff of sigh smoke, pale gray-cream.""",
    "sheet_fx1.png", "python3 scripts/slice_sheet.py <画像> fx")
add("E2", "記号", 1, "記号シート②（ハート・稲妻 など9個）", KV, f"""
{STYLE}

Make a sprite sheet of 9 more Japanese manga emotion symbols for this cartoon. No characters, only the symbols. {SHEET}
Row 1: (1) a small dusty-pink heart; (2) two angry nose-snort puffs; (3) a mustard lightning bolt.
Row 2: (4) a dizzy spiral; (5) three falling flower petals, dusty pink; (6) three angry steam puffs.
Row 3: (7) three small cold-sweat drops in a row; (8) a tiny rain cloud with three drops; (9) a light bulb (idea), mustard.""",
    "sheet_fx2.png", "切り抜き → assets/fx/（heart, snort, bolt, dizzy, petals, angry_steam, cold_sweat, raincloud, idea）", chat="same:E1")
add("E3", "記号", 2, "モザイク・ピー用の札（隠すふり）", KV, f"""
{STYLE}

Make a sprite sheet of 3 comedic censor graphics, side by side with wide space between them. Landscape 3:2 image. {MAGENTA}
(1) a square pixel-mosaic block in warm browns and creams (big chunky pixels); (2) a thick black censor bar with rounded ends; (3) a round cartoon "bleep" starburst in mustard and dusty red, empty inside (no text).""",
    "sheet_censor.png", "切り抜き → assets/fx/（mosaic, censor_bar, bleep）", chat="same:E1")

# ---------------- F. 小物シート ----------------
def props(id, pri, title, rows, save, chat="new", note=""):
    add(id, "小物", pri, title, KV, f"""
{STYLE}

Make a sprite sheet of 9 small props for the apartment room in the reference image, front view, the scale they would have in the room. No characters, no text or labels on anything. {SHEET}
{rows}""", save, "python3 scripts/slice_sheet.py <画像> props 名前:表示名 …", chat=chat, note=note)


props("F1", 1, "だらだらセット（毎回使う）", """Row 1: (1) an open potato-chip bag, plain; (2) a plain soda can; (3) a closed plain pizza box.
Row 2: (4) a generic game controller; (5) a TV remote; (6) a squishy cushion.
Row 3: (7) a crumpled blanket; (8) a stack of three plain comic books; (9) a cup noodle with a fork on the lid, plain.""", "sheet_props_darada.png")
props("F2", 1, "映画オタクの棚セット（毎回使う）", """Row 1: (1) a stack of plain DVD cases (blank spines); (2) three plain VHS tapes; (3) a film reel.
Row 2: (4) a clapperboard (blank, no writing); (5) a small vintage CRT TV; (6) a small home projector.
Row 3: (7) a striped popcorn bucket; (8) a pair of 3D glasses; (9) a pile of plain movie pamphlets (no text).""", "sheet_props_otaku.png", chat="same:F1")
props("F3", 1, "ファイト・クラブの回", """Row 1: (1) a pink bar of soap; (2) a stack of three blank VHS tapes; (3) a crumpled paper coffee cup.
Row 2: (4) a cracked smartphone face down; (5) a small potted cactus; (6) a pair of worn sneakers.
Row 3: (7) a plain necktie hanging loose; (8) a first-aid kit; (9) a framed blank picture (empty frame).""", "sheet_props_fightclub.png", chat="same:F1")
props("F4", 2, "仕事の悩みの回（オフィス）", """Row 1: (1) a plain ID badge on a lanyard; (2) a tall stack of documents; (3) a plain energy-drink can.
Row 2: (4) a necktie; (5) a briefcase; (6) a plain wall clock.
Row 3: (7) a stapler; (8) a desk calendar (no numbers); (9) a coffee thermos.""", "sheet_props_office.png", chat="same:F1")
props("F5", 2, "SF・夜の街の回", """Row 1: (1) a small neon-tube sign shaped like a wave (no letters); (2) a toy robot; (3) a toy rocket.
Row 2: (4) an origami unicorn; (5) a plain umbrella; (6) a retro handheld game.
Row 3: (7) a lava lamp; (8) a globe; (9) a model of a planet with a ring.""", "sheet_props_sf.png", chat="same:F1")
props("F6", 2, "ホラー・ゾンビの回", """Row 1: (1) a carved pumpkin; (2) a candle with dripping wax; (3) a toy skull.
Row 2: (4) a flashlight; (5) a baseball bat wrapped in tape; (6) a rubber zombie hand toy.
Row 3: (7) an old radio; (8) a canned food stack, plain; (9) a crow plush toy.""", "sheet_props_horror.png", chat="same:F1")
props("F7", 2, "恋愛・青春の回", """Row 1: (1) a cassette tape with blank label; (2) a pair of headphones; (3) a small bouquet.
Row 2: (4) a polaroid photo (blank); (5) a vinyl record; (6) a paper airplane.
Row 3: (7) a ukulele; (8) a sealed letter with a heart sticker; (9) a snow globe.""", "sheet_props_seishun.png", chat="same:F1")
props("F8", 2, "夏・休日の回", """Row 1: (1) a paper fan; (2) a wind chime; (3) a watermelon slice.
Row 2: (4) a straw hat; (5) a desk fan; (6) a popsicle.
Row 3: (7) a mosquito coil; (8) beach sandals; (9) a bottle of ramune soda, plain.""", "sheet_props_natsu.png", chat="same:F1")
props("F9", 1, "壁の飾り", """Row 1: (1) a blank pennant flag; (2) a round wall clock; (3) a cork board with blank notes.
Row 2: (4) a hanging plant; (5) a vinyl record in a frame; (6) an acoustic guitar.
Row 3: (7) string lights; (8) an empty picture frame; (9) a small shelf with a plant.""", "sheet_props_kabe.png", chat="same:F1")
props("F10", 1, "処方の小物（お医者さんごっこ）", """Row 1: (1) a paper medicine bag (blank); (2) a two-color capsule pill; (3) a blister pack of pills.
Row 2: (4) a stethoscope; (5) a clipboard with a blank chart; (6) a blank prescription paper.
Row 3: (7) a round rubber stamp; (8) an amber medicine bottle (blank label); (9) a white doctor's coat on a hanger.""", "sheet_props_shoho.png", chat="same:F1")

# ---------------- G. 壁のポスター（オリジナル・文字なし） ----------------
add("G1", "ポスター", 1, "オリジナルの映画ふうポスター9枚（文字なし）", KV, f"""
{STYLE}

Make a sheet of 9 ORIGINAL minimalist vertical poster artworks to hang on the wall of the room in the reference image. Each poster: a simple bold graphic with one strong image, flat colors, a thin frame. NO text, NO titles, NO logos, not based on any real movie poster. {SHEET}
Themes: (1) a single pink soap bar; (2) a rainy neon city street; (3) a lone astronaut; (4) a zombie hand rising from the ground; (5) a summer sea horizon; (6) two umbrellas in the rain; (7) a cassette tape and headphones; (8) a forest with one red balloon; (9) an old cinema building at night.""",
    "sheet_posters.png", "python3 scripts/slice_sheet.py <画像> props poster_soap:ポスター石けん …")

# ---------------- H. 部屋の別の場所（背景） ----------------
add("H1", "背景", 1, "じょんどぅーの本棚のアップ（次回ヒント用）", ["keyvisual.png", "room_base_source.png"], f"""
{STYLE}

Vertical 9:16 background illustration, no characters. A close-up of the bookshelf from the attached room: rows of plain DVD cases and books (blank spines, no text), a few small figures and knick-knacks, warm dim lamp light. Leave one empty space on the middle shelf (we will place a prop there later).""",
    "bg_tana.png", "assets/backgrounds/shelf_close.png")
add("H2", "背景", 2, "ローテーブルの上のアップ", ["keyvisual.png", "room_base_source.png"], f"""
{STYLE}

Vertical 9:16 background illustration, no characters. A close-up looking down at the low wooden coffee table from the attached room: wood grain kept simple, a mug and a remote at the edges, the center left empty (we will place props there later).""",
    "bg_table.png", "assets/backgrounds/table_close.png", chat="same:H1")
add("H3", "背景", 2, "部屋の入口（ごんべぇが入ってくる）", ["keyvisual.png", "room_base_source.png"], f"""
{STYLE}

Vertical 9:16 background illustration, no characters. The door side of the attached room: a half-open wooden door with a dim hallway behind it, a shoe rack, coats on hooks, same warm lighting and colors as the room.""",
    "bg_door.png", "assets/backgrounds/door.png", chat="same:H1")


def write():
    out = os.path.join(ROOT, "assets/prompts")
    os.makedirs(out, exist_ok=True)
    json.dump({"style_lock": STYLE, "items": ITEMS}, open(os.path.join(out, "batch01.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    n1 = sum(1 for i in ITEMS if i["priority"] == 1)
    lines = ["# 素材のまとめ作り（バッチ1）", "",
             f"全{len(ITEMS)}本（★優先 {n1}本）。Claude がブラウザで ChatGPT を操作するときは上から順に使う。手でやるときもこの順でコピペ。", "",
             "## 使い方", "",
             "- **添付**の画像は、まとめページの「添付する画像」から保存できる",
             "- **チャット**が「新しいチャット」のものは新しく開く。「〇〇と同じチャット」は続けて送る（絵柄がそろう）",
             "- できた画像は**保存名**で保存してClaudeに送る（名前が違っても大丈夫）。切り抜き・仕上げ・登録はClaude",
             "- 絵柄のルール（STYLE LOCK）は `docs/style-bible.md`。シートは無地のマゼンタ背景で頼む（自動で切り抜くため）",
             "- ChatGPTには時間あたりの画像の枚数制限がある。止められたら★だけ先に",
             "", "## 一覧", "", "| ID | 優先 | 種類 | 内容 | チャット | 保存名 |", "|---|---|---|---|---|---|"]
    for i in ITEMS:
        chat = "新しいチャット" if i["chat"] == "new" else i["chat"].replace("same:", "") + "と同じ"
        lines.append(f"| {i['id']} | {'★' if i['priority'] == 1 else ''} | {i['group']} | {i['title']} | {chat} | `{i['save']}` |")
    lines.append("")
    for i in ITEMS:
        chat = "新しいチャット" if i["chat"] == "new" else i["chat"].replace("same:", "") + " と同じチャットで続けて"
        lines += [f"## {i['id']} {'★ ' if i['priority'] == 1 else ''}{i['title']}",
                  f"チャット：{chat}　添付：" + "・".join(f"`{a}`" for a in i["attach"]) + f"　保存名：`{i['save']}`", ""]
        if i["note"]:
            lines += [f"メモ：{i['note']}", ""]
        lines += ["```", i["prompt"], "```", f"あとの処理：{i['post']}", ""]
    open(os.path.join(out, "batch01.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"書き出し完了: assets/prompts/batch01.json・batch01.md（{len(ITEMS)}本、★{n1}本）")


if __name__ == "__main__":
    write()
