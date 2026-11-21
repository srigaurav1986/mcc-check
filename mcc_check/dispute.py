"""Acquirer या NPCI को भेजने के लिए समीक्षा अनुरोध का मसौदा।

मसौदा केवल समीक्षा का अनुरोध करता है। अंतिम निर्णय acquirer या NPCI का होगा।
"""

from __future__ import annotations

from .audit import Finding
from .data import BY_CODE

KIND_HINDI = {
    "OVERCHARGE": "MDR अधिक कटने की समीक्षा",
    "MCC_REVIEW": "MCC वर्गीकरण की समीक्षा",
}


def render_dispute(finding: Finding) -> str:
    row = finding.row
    title = KIND_HINDI.get(finding.kind, "जाँच")
    lines = [
        f"विषय: {title}",
        "",
        f"तारीख: {row.txn_date.isoformat()}",
        f"Merchant का नाम: {row.merchant_name or 'उपलब्ध नहीं'}",
        f"रकम: ₹{row.amount}",
        f"कटा MDR: ₹{row.mdr_charged}",
        f"Assign किया गया MCC: {row.assigned_mcc} ({_label(row.assigned_mcc)})",
    ]
    if finding.expected is not None:
        lines.append(f"नियम से अपेक्षित MDR: ₹{finding.expected}")
    if finding.suggested_mcc:
        lines.append(f"नाम के आधार पर संकेतित MCC: {finding.suggested_mcc} ({_label(finding.suggested_mcc)})")
    lines += [
        "",
        f"जाँच का परिणाम: {finding.message}",
        "",
        "अनुरोध: कृपया इस लेनदेन के MCC वर्गीकरण और लागू MDR की समीक्षा करें।",
        "यह जाँच एक अनुमान पर आधारित है। अंतिम निर्णय acquirer या NPCI का होगा।",
    ]
    return "\n".join(lines)


def _label(code: str) -> str:
    entry = BY_CODE.get(code)
    return entry.hindi if entry else "अज्ञात"
