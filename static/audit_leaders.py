import csv
import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stock-cycle-reviews"
OUT_FILE = OUT_DIR / "leader-audit.csv"
TMP_FILE = OUT_DIR / "leader-audit.tmp.csv"


def read_report(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r'<script type="application/json" id="stock-cycle-review-data">\s*(.*?)\s*</script>',
        text,
        re.S,
    )
    if not match:
        return None
    return json.loads(html.unescape(match.group(1)))


def verdict_summary(report, verdict):
    items = []
    for item in report.get("model_verdicts") or []:
        if item.get("verdict") != verdict:
            continue
        reason = item.get("reason") or ""
        suffix = f":{reason}" if reason and verdict == "standard buy" else ""
        items.append(f"{item.get('stock', '')}({item.get('role', '')}){suffix}")
    return "; ".join(items)


def main():
    OUT_DIR.mkdir(exist_ok=True)
    fields = [
        "date",
        "skill",
        "market_phase",
        "cycle",
        "prior",
        "prior_theme",
        "prior_confirmed",
        "old_leader_state",
        "loss_effect",
        "leader_watch",
        "core",
        "tradable",
        "next",
        "std",
        "observe",
        "reject",
        "std_count",
    ]
    rows = []
    for path in sorted(OUT_DIR.glob("2026-*.html")):
        report = read_report(path)
        if not report:
            continue
        standard = [
            item
            for item in report.get("model_verdicts") or []
            if item.get("verdict") == "standard buy"
        ]
        rows.append(
            {
                "date": report.get("review_date", ""),
                "skill": (report.get("generated_by_skill") or {}).get("name", ""),
                "market_phase": report.get("market_phase", ""),
                "cycle": report.get("cycle_stage", ""),
                "prior": report.get("prior_confirmed_leader", ""),
                "prior_theme": report.get("prior_leader_theme", ""),
                "prior_confirmed": report.get("prior_leader_confirmed", ""),
                "old_leader_state": report.get("old_leader_state", ""),
                "loss_effect": (report.get("loss_effect") or {}).get("level", ""),
                "leader_watch": report.get("leader_watch", ""),
                "core": report.get("current_core", ""),
                "tradable": report.get("tradable_high_board", ""),
                "next": report.get("next_opportunity", ""),
                "std": verdict_summary(report, "standard buy"),
                "observe": verdict_summary(report, "observe only"),
                "reject": verdict_summary(report, "reject"),
                "std_count": len(standard),
            }
        )

    with TMP_FILE.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    TMP_FILE.replace(OUT_FILE)
    print(json.dumps({"written": str(OUT_FILE), "rows": len(rows)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
