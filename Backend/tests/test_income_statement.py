"""Accounting rules, each tested on a tiny ledger so the expected number is obvious."""
from decimal import Decimal

from app.income_statement import build_income_statement
from tests.helpers import amount, entry, make_ledger, sale, section, total

START, END = "2026-01-01", "2026-03-31"


def run(*entries, start=START, end=END):
    return build_income_statement(make_ledger(*entries), start, end)


# --- which entries count -------------------------------------------------------

def test_void_entry_is_ignored():
    # Same sale entered twice, one copy voided (like JE-009 / JE-010).
    s = run(sale("A", "2026-02-03", "8200.00"), sale("B", "2026-02-03", "8200.00", status="void"))
    assert total(s, "revenue") == "8200.00"


def test_draft_entry_is_ignored():
    # Bonus accrual waiting for approval (like JE-019).
    s = run(
        entry("A", "2026-03-15", [("6000", "5000.00", "0.00"), ("2000", "0.00", "5000.00")], status="draft")
    )
    assert total(s, "operating_expenses") == "0.00"
    assert total(s, "net_income") == "0.00"


def test_start_and_end_dates_are_inclusive():
    s = run(
        sale("A", "2026-01-01", "100.00"),  # exactly on start
        sale("B", "2026-03-31", "200.00"),  # exactly on end
    )
    assert total(s, "revenue") == "300.00"


def test_entries_outside_the_range_are_excluded():
    s = run(
        sale("A", "2025-12-31", "100.00"),  # one day before start
        sale("B", "2026-04-01", "200.00"),  # one day after end
        sale("C", "2026-02-15", "50.00"),
    )
    assert total(s, "revenue") == "50.00"


def test_single_day_range():
    s = run(sale("A", "2026-03-31", "10.00"), sale("B", "2026-03-30", "99.00"), start="2026-03-31", end="2026-03-31")
    assert total(s, "revenue") == "10.00"


def test_entries_do_not_need_to_be_in_date_order():
    # JE-007 in the real data is dated Jan 1 but listed after Jan 31 entries.
    s = run(sale("A", "2026-03-31", "200.00"), sale("B", "2026-01-01", "100.00"))
    assert total(s, "revenue") == "300.00"


def test_balance_sheet_accounts_never_appear():
    s = run(sale("A", "2026-02-01", "100.00"))
    shown = [l["account"] for sec in s["sections"] for l in sec.get("lines", [])]
    assert "1000" not in shown and "2000" not in shown


# --- signs ---------------------------------------------------------------------

def test_contra_revenue_reduces_revenue():
    s = run(
        sale("A", "2026-02-01", "1000.00"),
        entry("B", "2026-02-14", [("4900", "250.00", "0.00"), ("1000", "0.00", "250.00")]),
    )
    assert amount(s, "revenue", "4900") == "-250.00"
    assert total(s, "revenue") == "750.00"


def test_three_line_entry_with_discount():
    # Like JE-016: 15000 sale with a 150 discount, cash receives 14850.
    s = run(
        entry("A", "2026-03-02", [("1000", "14850.00", "0.00"), ("4900", "150.00", "0.00"), ("4000", "0.00", "15000.00")])
    )
    assert amount(s, "revenue", "4000") == "15000.00"
    assert amount(s, "revenue", "4900") == "-150.00"
    assert total(s, "revenue") == "14850.00"


def test_credit_to_an_expense_reduces_it():
    # Like JE-020: vendor credit against Software.
    s = run(
        entry("A", "2026-03-10", [("6000", "1199.97", "0.00"), ("2000", "0.00", "1199.97")]),
        entry("B", "2026-03-20", [("2000", "100.00", "0.00"), ("6000", "0.00", "100.00")]),
    )
    assert amount(s, "operating_expenses", "6000") == "1099.97"


# --- structure -----------------------------------------------------------------

def test_inactive_account_with_history_still_appears():
    s = run(entry("A", "2026-01-20", [("6300", "2500.10", "0.00"), ("2000", "0.00", "2500.10")]))
    assert amount(s, "operating_expenses", "6300") == "2500.10"


def test_accounts_with_no_activity_show_zero():
    s = run(sale("A", "2026-02-01", "100.00"))
    assert amount(s, "operating_expenses", "6000") == "0.00"
    assert amount(s, "operating_expenses", "6300") == "0.00"
    assert amount(s, "cogs", "5000") == "0.00"


def test_empty_range_gives_all_zeros():
    s = run(sale("A", "2025-01-01", "100.00"))
    assert total(s, "net_income") == "0.00"


def test_calculated_rows_show_how_they_are_built():
    s = run(
        sale("A", "2026-01-05", "1000.00"),
        entry("B", "2026-01-05", [("5000", "400.00", "0.00"), ("1000", "0.00", "400.00")]),
        entry("C", "2026-01-31", [("6000", "250.00", "0.00"), ("1000", "0.00", "250.00")]),
        entry("D", "2026-01-31", [("1000", "10.00", "0.00"), ("7000", "0.00", "10.00")]),
    )

    def parts(key):
        return [(l["name"], l["amount"]) for l in section(s, key)["lines"]]

    assert section(s, "gross_profit")["kind"] == "calculated"
    assert parts("gross_profit") == [("Total revenue", "1000.00"), ("Cost of goods sold", "-400.00")]
    assert parts("operating_income") == [("Gross profit", "600.00"), ("Total operating expenses", "-250.00")]
    assert parts("net_income") == [("Operating income", "350.00"), ("Other income", "10.00")]
    assert section(s, "revenue")["kind"] == "accounts"


def test_every_section_total_equals_the_sum_of_its_lines():
    s = run(
        sale("A", "2026-01-05", "1000.00"),
        entry("B", "2026-01-05", [("4900", "75.50", "0.00"), ("1000", "0.00", "75.50")]),
        entry("C", "2026-01-05", [("5000", "400.00", "0.00"), ("1000", "0.00", "400.00")]),
        entry("D", "2026-01-31", [("6000", "250.00", "0.00"), ("1000", "0.00", "250.00")]),
    )
    for sec in s["sections"]:
        assert sum(Decimal(l["amount"]) for l in sec["lines"]) == Decimal(sec["total"]), sec["key"]


def test_zero_is_never_shown_as_negative_zero():
    # With no activity, "Less: cost of goods sold" is 0 and must print 0.00, not -0.00.
    s = run(sale("A", "2026-02-01", "100.00"))
    shown = [l["amount"] for sec in s["sections"] for l in sec["lines"]] + [sec["total"] for sec in s["sections"]]
    assert "-0.00" not in shown


def test_sections_are_in_statement_order():
    s = run(sale("A", "2026-02-01", "100.00"))
    assert [sec["key"] for sec in s["sections"]] == [
        "revenue", "cogs", "gross_profit", "operating_expenses",
        "operating_income", "other_income", "net_income",
    ]


# --- subtotals -----------------------------------------------------------------

def test_subtotals_flow_through_to_net_income():
    s = run(
        sale("A", "2026-01-05", "1000.00"),
        entry("B", "2026-01-05", [("5000", "400.00", "0.00"), ("1000", "0.00", "400.00")]),
        entry("C", "2026-01-31", [("6000", "250.00", "0.00"), ("1000", "0.00", "250.00")]),
        entry("D", "2026-01-31", [("1000", "10.00", "0.00"), ("7000", "0.00", "10.00")]),
    )
    assert total(s, "gross_profit") == "600.00"      # 1000 - 400
    assert total(s, "operating_income") == "350.00"  # 600 - 250
    assert total(s, "net_income") == "360.00"        # 350 + 10


def test_net_loss_is_negative():
    s = run(entry("A", "2026-01-31", [("6000", "500.00", "0.00"), ("1000", "0.00", "500.00")]))
    assert total(s, "net_income") == "-500.00"


def test_other_income_is_added_not_subtracted():
    s = run(entry("A", "2026-01-31", [("1000", "42.18", "0.00"), ("7000", "0.00", "42.18")]))
    assert total(s, "other_income") == "42.18"
    assert total(s, "net_income") == "42.18"


# --- money ---------------------------------------------------------------------

def test_amounts_are_exact_not_floats():
    # Ten sales of 0.10 add up to exactly 1.00 (floats give 0.9999999999999999).
    s = run(*[sale(f"E{i}", "2026-02-01", "0.10") for i in range(10)])
    assert total(s, "revenue") == "1.00"


def test_amounts_are_strings_with_two_decimals():
    s = run(sale("A", "2026-02-01", "5.00"))
    assert amount(s, "revenue", "4000") == "5.00"
    assert isinstance(total(s, "net_income"), str)
