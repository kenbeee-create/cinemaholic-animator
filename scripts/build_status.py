"""進み具合のページ docs/status.md を作る（AIを使わない）。

判定：
  台本     … episodes/<回>/script_v2.md か script.md がある
  承認     … docs/progress.json の approved に日付がある
  下書き動画 … episodes/<回>/episode.json がある（スタジオで組める状態）
  公開     … docs/progress.json の published に日付がある
段階（docs/purpose.md）：公開本数 0〜2 → 段階0、3〜9 → 段階1、10〜29 → 段階2、30〜 → 段階3
使い方：python3 scripts/build_status.py
"""
import datetime
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
STAGES = [(0, "段階0：まず3本公開する"), (3, "段階1：10本まで出して型を確かめる"),
          (10, "段階2：30本でシリーズにする"), (30, "段階3：規模と仕事の入口")]


def main():
    prog = json.load(open(os.path.join(ROOT, "docs/progress.json"), encoding="utf-8"))
    eps = sorted(d for d in os.listdir(os.path.join(ROOT, "episodes"))
                 if d.startswith("ep") and not d.startswith("ep00"))
    rows, n = [], {"script": 0, "approved": 0, "draft": 0, "published": 0}
    for e in eps:
        d = os.path.join(ROOT, "episodes", e)
        p = prog["episodes"].get(e, {})
        s = os.path.exists(os.path.join(d, "script_v2.md")) or os.path.exists(os.path.join(d, "script.md"))
        dr = os.path.exists(os.path.join(d, "episode.json"))
        ap, pu = p.get("approved"), p.get("published")
        for k, v in (("script", s), ("approved", ap), ("draft", dr), ("published", pu)):
            n[k] += bool(v)
        mark = lambda v: (v if isinstance(v, str) else "○") if v else "—"
        rows.append(f"| {e} | {mark(s)} | {mark(ap)} | {mark(dr)} | {mark(pu)} |")
    stage = [label for lo, label in STAGES if n["published"] >= lo][-1]
    nxt = next((lo for lo, _ in STAGES if lo > n["published"]), None)
    out = [
        "# シネマホリックの進み具合（自動生成）",
        "",
        f"更新：{datetime.date.today()}（scripts/build_status.py が作る。手で直さない。承認・公開は docs/progress.json に書く）",
        "",
        f"- 今の段階：**{stage}**" + (f"（公開 {n['published']} / {nxt} 本）" if nxt else ""),
        f"- 台本 {n['script']}本 ／ 承認 {n['approved']}本 ／ 下書き動画 {n['draft']}本 ／ 公開 {n['published']}本",
        "",
        "## 本人待ち",
        *([f"- {w}" for w in prog.get("waiting_on_owner", [])] or ["- なし"]),
        "",
        "## 回ごと",
        "| 回 | 台本 | 承認 | 下書き動画 | 公開 |",
        "|---|---|---|---|---|",
        *rows,
        "",
    ]
    open(os.path.join(ROOT, "docs/status.md"), "w", encoding="utf-8").write("\n".join(out))
    print("\n".join(out[:7]))


if __name__ == "__main__":
    main()
