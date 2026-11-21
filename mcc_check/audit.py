"""Merchant audit: settlement या statement की जाँच।

दो जाँचें होती हैं:
1. MDR जाँच: जो शुल्क कटा, वह नियम के हिसाब से सही है या नहीं।
2. MCC समीक्षा: merchant के नाम से लगने वाला MCC, assign किए गए MCC से अलग है या नहीं।

यह tool कोई बदलाव नहीं करता और कोई MCC बदलने की सलाह नहीं देता। यह केवल जाँच के लिए संकेत देता है।
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional

from .mdr import MdrRule, expected_mdr, find_rule
from .suggest import confidence, suggest

REQUIRED = ("date", "amount", "mdr_charged", "merchant_name", "assigned_mcc")


@dataclass(frozen=True)
class Row:
    txn_date: date
    amount: Decimal
    mdr_charged: Decimal
    merchant_name: str
    assigned_mcc: str
    instrument: str


@dataclass(frozen=True)
class Finding:
    row: Row
    kind: str                       # OVERCHARGE, UNDERCHARGE, MCC_REVIEW, NO_RULE
    message: str
    expected: Optional[Decimal] = None
    suggested_mcc: Optional[str] = None


def read_rows(path: Path) -> list:
    with Path(path).open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        headers = set(reader.fieldnames or [])
        missing = [name for name in REQUIRED if name not in headers]
        if missing:
            raise ValueError(f"ज़रूरी कॉलम नहीं मिले: {', '.join(missing)}")
        rows = []
        for line_no, raw in enumerate(reader, start=2):
            try:
                rows.append(_parse(raw))
            except (ValueError, InvalidOperation) as exc:
                raise ValueError(f"पंक्ति {line_no}: {exc}") from exc
    return rows


def _parse(raw: dict) -> Row:
    def cell(name: str) -> str:
        return (raw.get(name) or "").strip()

    try:
        txn_date = date.fromisoformat(cell("date"))
    except ValueError:
        raise ValueError(f"गलत तारीख '{cell('date')}', YYYY-MM-DD चाहिए") from None
    amount = Decimal(cell("amount"))
    mdr = Decimal(cell("mdr_charged") or "0")
    if amount <= 0:
        raise ValueError("रकम धनात्मक होनी चाहिए")
    return Row(
        txn_date=txn_date,
        amount=amount,
        mdr_charged=mdr,
        merchant_name=cell("merchant_name"),
        assigned_mcc=cell("assigned_mcc"),
        instrument=cell("instrument") or "upi_p2m",
    )


def audit(rows: list, rules: dict, tolerance: Decimal = Decimal("0.05"),
          review_confidence: float = 0.5) -> list:
    findings = []
    for row in rows:
        rule: Optional[MdrRule] = find_rule(rules, row.instrument, row.assigned_mcc)
        if rule is None:
            findings.append(Finding(row, "NO_RULE", "इस माध्यम के लिए नियम उपलब्ध नहीं है, जाँच छोड़ी गई।"))
        else:
            expected = expected_mdr(row.amount, rule)
            diff = row.mdr_charged - expected
            if diff > tolerance:
                findings.append(Finding(
                    row, "OVERCHARGE",
                    f"कटा शुल्क ₹{row.mdr_charged} है, नियम से ₹{expected} बनता है। अंतर ₹{diff}।",
                    expected=expected,
                ))
            elif diff < -tolerance:
                findings.append(Finding(
                    row, "UNDERCHARGE",
                    f"कटा शुल्क ₹{row.mdr_charged} है, नियम से ₹{expected} बनता है। यह जानकारी के लिए है।",
                    expected=expected,
                ))

        results = suggest(row.merchant_name)
        top = results[0] if results else None
        if top and top.code != row.assigned_mcc and confidence(results) >= review_confidence:
            findings.append(Finding(
                row, "MCC_REVIEW",
                f"नाम के संकेत '{', '.join(top.matched)}' से {top.code} ({top.name}) दिखता है, "
                f"जबकि assign किया गया MCC {row.assigned_mcc} है। यह समीक्षा का संकेत है, निर्णय नहीं।",
                suggested_mcc=top.code,
            ))
    return findings
