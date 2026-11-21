import json
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from mcc_check.audit import Row, audit, read_rows
from mcc_check.data import BY_CODE
from mcc_check.dispute import render_dispute
from mcc_check.mdr import DEFAULT_RULES, MdrRule, expected_mdr, find_rule, load_rules
from mcc_check.suggest import confidence, suggest

ROOT = Path(__file__).resolve().parent.parent
SAMPLE = ROOT / "examples" / "statement.csv"


class SuggestTest(unittest.TestCase):
    def test_english_name(self):
        self.assertEqual(suggest("Sharma Kirana Store")[0].code, "5411")

    def test_hindi_name(self):
        self.assertEqual(suggest("गुप्ता मेडिकल हॉल")[0].code, "5912")

    def test_unknown_name_gives_nothing(self):
        self.assertEqual(suggest("Zebra Xylo Works"), [])

    def test_confidence_zero_when_no_match(self):
        self.assertEqual(confidence([]), 0.0)

    def test_all_table_codes_are_four_digits(self):
        for code in BY_CODE:
            self.assertEqual(len(code), 4)
            self.assertTrue(code.isdigit())


class MdrTest(unittest.TestCase):
    rule = DEFAULT_RULES["upi_p2m"]

    def test_zero_at_threshold(self):
        self.assertEqual(expected_mdr(Decimal("2000"), self.rule), Decimal("0.00"))

    def test_rate_applies_above_threshold(self):
        self.assertEqual(expected_mdr(Decimal("2500"), self.rule), Decimal("10.00"))

    def test_cap_applies(self):
        self.assertEqual(expected_mdr(Decimal("100000"), self.rule), Decimal("300"))

    def test_custom_rule_file_overrides_default(self):
        data = {"upi_p2m": {"rate": "0.01", "cap": None, "zero_below": "0"}}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as h:
            json.dump(data, h)
        try:
            rules = load_rules(Path(h.name))
        finally:
            Path(h.name).unlink()
        self.assertEqual(expected_mdr(Decimal("1000"), rules["upi_p2m"]), Decimal("10.00"))

    def test_mcc_specific_rule_wins(self):
        rules = {"upi_p2m": self.rule, "upi_p2m:5541": MdrRule(Decimal("0.02"), None, Decimal("0"))}
        self.assertEqual(find_rule(rules, "upi_p2m", "5541").rate, Decimal("0.02"))
        self.assertEqual(find_rule(rules, "upi_p2m", "5411").rate, Decimal("0.004"))


class AuditTest(unittest.TestCase):
    def test_sample_findings(self):
        findings = audit(read_rows(SAMPLE), DEFAULT_RULES)
        kinds = [(f.kind, f.row.merchant_name) for f in findings]
        self.assertIn(("OVERCHARGE", "Gupta Medical Hall"), kinds)
        self.assertIn(("MCC_REVIEW", "Gupta Medical Hall"), kinds)
        self.assertNotIn(("OVERCHARGE", "Sharma Kirana Store"), kinds)
        self.assertNotIn(("MCC_REVIEW", "City Petrol Pump"), kinds)

    def test_no_rule_is_reported(self):
        row = Row(date(2026, 11, 2), Decimal("100"), Decimal("0"), "X", "5411", "unknown_rail")
        findings = audit([row], DEFAULT_RULES)
        self.assertEqual(findings[0].kind, "NO_RULE")

    def test_tolerance_hides_small_difference(self):
        row = Row(date(2026, 11, 2), Decimal("2500"), Decimal("10.04"), "Sharma Kirana Store", "5411", "upi_p2m")
        self.assertEqual(audit([row], DEFAULT_RULES), [])


class DisputeTest(unittest.TestCase):
    def test_draft_is_hindi_and_non_binding(self):
        findings = audit(read_rows(SAMPLE), DEFAULT_RULES)
        overcharge = next(f for f in findings if f.kind == "OVERCHARGE")
        text = render_dispute(overcharge)
        self.assertIn("अनुरोध", text)
        self.assertIn("अंतिम निर्णय acquirer या NPCI का होगा", text)


if __name__ == "__main__":
    unittest.main()
