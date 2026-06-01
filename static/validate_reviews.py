import html
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "stock-cycle-reviews"


def read_report(path):
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r'<script type="application/json" id="stock-cycle-review-data">\s*(.*?)\s*</script>',
        text,
        re.S,
    )
    if not match:
        raise AssertionError(f"missing JSON block: {path}")
    return json.loads(html.unescape(match.group(1)))


def main():
    reports = []
    standard_buys = []
    for path in sorted(OUT_DIR.glob("2026-*.html")):
        report = read_report(path)
        reports.append(report)
        for item in report.get("model_verdicts") or []:
            if item.get("verdict") == "standard buy":
                standard_buys.append(
                    {
                        "date": report.get("review_date"),
                        "stock": item.get("stock"),
                        "reason": item.get("reason"),
                    }
                )

    print(
        json.dumps(
            {
                "reports": len(reports),
                "standard_buy_count": len(standard_buys),
                "standard_buys": standard_buys,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
