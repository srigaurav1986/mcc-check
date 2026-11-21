"""कमांड-लाइन इंटरफ़ेस: lookup, suggest, mdr, audit।"""

from __future__ import annotations

import argparse
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

from .audit import audit, read_rows
from .data import BY_CODE
from .dispute import render_dispute
from .mdr import expected_mdr, find_rule, load_rules
from .suggest import confidence, suggest


def _cmd_lookup(args) -> int:
    entry = BY_CODE.get(args.code)
    if entry is None:
        print(f"त्रुटि: MCC {args.code} हमारी सूची में नहीं है। आधिकारिक ISO 18245 सूची देखें।", file=sys.stderr)
        return 2
    print(f"{entry.code}: {entry.hindi} ({entry.name})")
    return 0


def _cmd_suggest(args) -> int:
    results = suggest(args.text)
    if not results:
        print("कोई संकेत नहीं मिला। नाम या narration में कोई पहचाना हुआ शब्द नहीं है।")
        return 0
    for r in results:
        print(f"{r.code}: {BY_CODE[r.code].hindi} (स्कोर {r.score}, मिले शब्द: {', '.join(r.matched)})")
    print(f"विश्वास: {confidence(results)}। यह केवल संकेत है, अंतिम MCC acquirer तय करता है।")
    return 0


def _cmd_mdr(args) -> int:
    rules = load_rules(args.rules)
    rule = find_rule(rules, args.instrument, args.mcc or "")
    if rule is None:
        print(f"त्रुटि: '{args.instrument}' के लिए नियम नहीं मिला।", file=sys.stderr)
        return 2
    fee = expected_mdr(Decimal(str(args.amount)), rule)
    print(f"अनुमानित MDR: ₹{fee}")
    print("यह प्रकाशित नियमों पर आधारित अनुमान है। वास्तविक दर बैंक तय करता है।")
    return 0


def _cmd_audit(args) -> int:
    rules = load_rules(args.rules)
    rows = read_rows(args.csv_file)
    findings = audit(rows, rules, tolerance=Decimal(str(args.tolerance)))
    if not findings:
        print("कोई जाँच-योग्य गड़बड़ी नहीं मिली।")
        return 0
    for f in findings:
        print(f"[{f.kind}] {f.row.txn_date.isoformat()} {f.row.merchant_name}: {f.message}")
    if args.dispute:
        for f in findings:
            if f.kind in ("OVERCHARGE", "MCC_REVIEW"):
                print("\n" + "-" * 40)
                print(render_dispute(f))
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcc-check",
        description="MCC का संकेत, MDR का हिसाब और merchant audit। सब कुछ आपकी मशीन पर चलता है।",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("lookup", help="MCC कोड का अर्थ देखें")
    p.add_argument("code")
    p.set_defaults(func=_cmd_lookup)

    p = sub.add_parser("suggest", help="नाम या narration से MCC का संकेत लें")
    p.add_argument("text")
    p.set_defaults(func=_cmd_suggest)

    p = sub.add_parser("mdr", help="रकम पर अनुमानित MDR निकालें")
    p.add_argument("--amount", type=float, required=True)
    p.add_argument("--instrument", default="upi_p2m")
    p.add_argument("--mcc", default="")
    p.add_argument("--rules", type=Path, help="नियमों वाली JSON फ़ाइल")
    p.set_defaults(func=_cmd_mdr)

    p = sub.add_parser("audit", help="statement CSV की जाँच करें")
    p.add_argument("csv_file", type=Path)
    p.add_argument("--rules", type=Path, help="नियमों वाली JSON फ़ाइल")
    p.add_argument("--tolerance", default="0.05", help="छोटे अंतर को अनदेखा करने की सीमा (रुपये)")
    p.add_argument("--dispute", action="store_true", help="समीक्षा अनुरोध के मसौदे भी दिखाएँ")
    p.set_defaults(func=_cmd_audit)
    return parser


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError, InvalidOperation) as exc:
        print(f"त्रुटि: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
