"""The real ledger.json, checked against numbers worked out by hand from the entries."""
import json
from pathlib import Path

from app.income_statement import build_income_statement
from tests.helpers import amount, total

LEDGER = json.load(open(Path(__file__).parent.parent / "data" / "ledger.json"))


def statement(start, end):
    return build_income_statement(LEDGER, start, end)


def test_q1_2026_every_line():
    s = statement("2026-01-01", "2026-03-31")
    # Revenue: 12450.75 + 8200 + 15000 = 35650.75 ; subscription 3 x 1000 ; returns 650.25 + 150
    assert amount(s, "revenue", "4000") == "35650.75"
    assert amount(s, "revenue", "4100") == "3000.00"
    assert amount(s, "revenue", "4900") == "-800.25"
    assert total(s, "revenue") == "37850.50"
    # COGS: 4980.30 + 3280 + 6012.45
    assert total(s, "cogs") == "14272.75"
    assert total(s, "gross_profit") == "23577.75"
    # Opex: salaries 3 x 18500 ; rent 9000 ; software 1199.97 - 100 ; marketing 2500.10
    assert amount(s, "operating_expenses", "6000") == "55500.00"
    assert amount(s, "operating_expenses", "6100") == "9000.00"
    assert amount(s, "operating_expenses", "6200") == "1099.97"
    assert amount(s, "operating_expenses", "6300") == "2500.10"
    assert total(s, "operating_expenses") == "68100.07"
    assert total(s, "operating_income") == "-44522.32"
    assert total(s, "other_income") == "42.18"
    assert total(s, "net_income") == "-44480.14"


def test_february_only():
    # Revenue 8200 + 1000 - 650.25 ; COGS 3280 ; payroll 18500 (void JE-009 ignored)
    s = statement("2026-02-01", "2026-02-28")
    assert total(s, "revenue") == "8549.75"
    assert total(s, "net_income") == "-13230.25"


def test_single_day_march_31():
    # Subscription 1000 + interest 42.18 - payroll 18500
    s = statement("2026-03-31", "2026-03-31")
    assert total(s, "net_income") == "-17457.82"


def test_december_2025_only():
    s = statement("2025-12-01", "2025-12-31")
    assert total(s, "net_income") == "5000.00"


def test_april_2026_only():
    s = statement("2026-04-01", "2026-04-30")
    assert total(s, "net_income") == "9100.00"


def test_range_with_no_entries():
    s = statement("2030-01-01", "2030-12-31")
    assert total(s, "net_income") == "0.00"


def test_range_covering_everything():
    # Q1 net income + December 5000 + April 9100
    s = statement("2025-01-01", "2026-12-31")
    assert total(s, "net_income") == "-30380.14"


def test_adjacent_ranges_add_up_to_the_whole():
    # Splitting a range in two must not lose or double-count any entry.
    jan = statement("2026-01-01", "2026-01-31")
    rest = statement("2026-02-01", "2026-03-31")
    q1 = statement("2026-01-01", "2026-03-31")
    from decimal import Decimal
    assert Decimal(total(jan, "net_income")) + Decimal(total(rest, "net_income")) == Decimal(total(q1, "net_income"))


def test_every_posted_entry_balances():
    # Sanity check on the data itself: debits equal credits in each entry.
    from decimal import Decimal
    for e in LEDGER["journal_entries"]:
        debits = sum(Decimal(l["debit"]) for l in e["lines"])
        credits = sum(Decimal(l["credit"]) for l in e["lines"])
        assert debits == credits, e["id"]


def test_net_income_matches_a_calculation_that_skips_the_sections():
    # Independent check: add up every posted revenue-type account (credit - debit)
    # and subtract every expense-type account (debit - credit) straight from the
    # entries, without using any of the statement code.
    from decimal import Decimal
    types = {a["number"]: a["type"] for a in LEDGER["accounts"]}
    expected = Decimal("0.00")
    for e in LEDGER["journal_entries"]:
        if e["status"] == "posted" and "2026-01-01" <= e["date"] <= "2026-03-31":
            for l in e["lines"]:
                change = Decimal(l["credit"]) - Decimal(l["debit"])
                if types[l["account"]] == "revenue":
                    expected += change
                elif types[l["account"]] == "expense":
                    expected += change  # an expense debit lowers net income
    assert total(statement("2026-01-01", "2026-03-31"), "net_income") == str(expected)
