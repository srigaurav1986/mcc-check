"""MDR (Merchant Discount Rate) का हिसाब।

डिफ़ॉल्ट नियम प्रकाशित बैंक सूचनाओं पर आधारित हैं, पर ये स्थायी नहीं हैं।
नियम बदलने पर JSON फ़ाइल से उन्हें बदलें। अंतिम दर बैंक तय करता है।
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class MdrRule:
    rate: Decimal                 # जैसे 0.004 मतलब 0.40%
    cap: Optional[Decimal]        # प्रति लेनदेन अधिकतम शुल्क
    zero_below: Decimal           # इस रकम तक या इससे कम पर शुल्क शून्य


# एक बैंक की सूचना के अनुसार: सामान्य P2M पर 0.40% तक, अधिकतम ₹300, और ₹2,000 तक शून्य।
DEFAULT_RULES = {
    "upi_p2m": MdrRule(rate=Decimal("0.004"), cap=Decimal("300"), zero_below=Decimal("2000")),
}


def expected_mdr(amount: Decimal, rule: MdrRule) -> Decimal:
    if amount <= rule.zero_below:
        return Decimal("0.00")
    fee = amount * rule.rate
    if rule.cap is not None:
        fee = min(fee, rule.cap)
    return fee.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def load_rules(path: Optional[Path]) -> dict:
    """नियम लोड करें। JSON की कुंजी 'instrument' या 'instrument:MCC' हो सकती है।

    उदाहरण:
      {"upi_p2m": {"rate": "0.004", "cap": "300", "zero_below": "2000"},
       "rupay_cc_upi:5541": {"rate": "0.01", "cap": null, "zero_below": "0"}}
    """
    rules = dict(DEFAULT_RULES)
    if path is None:
        return rules
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    for key, spec in data.items():
        if key.startswith("_"):
            continue
        cap = spec.get("cap")
        rules[key] = MdrRule(
            rate=Decimal(spec["rate"]),
            cap=Decimal(cap) if cap is not None else None,
            zero_below=Decimal(spec.get("zero_below", "0")),
        )
    return rules


def find_rule(rules: dict, instrument: str, mcc: str) -> Optional[MdrRule]:
    return rules.get(f"{instrument}:{mcc}") or rules.get(instrument)
