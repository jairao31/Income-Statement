"""Small helpers so each test can describe a tiny ledger in a few lines."""

# A minimal chart of accounts: one account for each place on the statement,
# plus Cash and AP (balance sheet) so entries can be balanced.
ACCOUNTS = [
    {"number": "1000", "name": "Cash", "type": "asset", "subtype": "balance_sheet", "is_active": True},
    {"number": "2000", "name": "Accounts Payable", "type": "liability", "subtype": "balance_sheet", "is_active": True},
    {"number": "4000", "name": "Product Revenue", "type": "revenue", "subtype": "operating_revenue", "is_active": True},
    {"number": "4900", "name": "Returns", "type": "revenue", "subtype": "contra_revenue", "is_active": True},
    {"number": "5000", "name": "COGS", "type": "expense", "subtype": "cogs", "is_active": True},
    {"number": "6000", "name": "Salaries", "type": "expense", "subtype": "operating_expense", "is_active": True},
    {"number": "6300", "name": "Marketing (legacy)", "type": "expense", "subtype": "operating_expense", "is_active": False},
    {"number": "7000", "name": "Interest Income", "type": "revenue", "subtype": "other_income", "is_active": True},
]


def entry(entry_id, date, lines, status="posted"):
    """lines is a list of (account, debit, credit) tuples, amounts as strings."""
    return {
        "id": entry_id,
        "date": date,
        "status": status,
        "memo": "",
        "lines": [{"account": a, "debit": d, "credit": c} for a, d, c in lines],
    }


def make_ledger(*entries):
    return {
        "company": "Test Co",
        "currency": "USD",
        "accounts": ACCOUNTS,
        "journal_entries": list(entries),
    }


def sale(entry_id, date, amount, status="posted"):
    """A sale: debit Cash, credit Product Revenue."""
    return entry(entry_id, date, [("1000", amount, "0.00"), ("4000", "0.00", amount)], status)


def section(statement, key):
    return next(s for s in statement["sections"] if s["key"] == key)


def amount(statement, key, account):
    """The amount shown for one account line inside a section."""
    return next(l["amount"] for l in section(statement, key)["lines"] if l["account"] == account)


def total(statement, key):
    return section(statement, key)["total"]
