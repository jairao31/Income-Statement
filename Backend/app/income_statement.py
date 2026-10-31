from datetime import date
from decimal import Decimal

ZERO = Decimal("0.00")
CENT = Decimal("0.01")

# The only entry statuses the ledger may use (see the README's data dictionary).
STATUSES = {"posted", "draft", "void"}


def money(amount):
    """Format a Decimal as a string with exactly 2 decimals, e.g. '1099.97'."""
    return str(amount.quantize(CENT))


def check_date(name, value):
    """Raise ValueError unless value is a real calendar date written as YYYY-MM-DD."""
    try:
        is_valid = date.fromisoformat(value).isoformat() == value
    except ValueError:
        is_valid = False
    if not is_valid:
        raise ValueError(
            f"'{name}' must be a real date in YYYY-MM-DD format, got '{value}'"
        )


def validate_ledger(ledger):
    """
    Raise ValueError if the ledger is malformed. It is called once, when the
    server starts, so a bad ledger stops the server with a clear message
    instead of giving wrong numbers or a crash on the first request.

    It checks every journal entry (including drafts and voids) for:
        - a known status: posted, draft or void
        - lines that use account numbers that exist in the chart of accounts
        - total debits equal to total credits
    """
    account_numbers = {account["number"] for account in ledger["accounts"]}

    for entry in ledger["journal_entries"]:
        entry_id = entry["id"]

        if entry["status"] not in STATUSES:
            raise ValueError(
                f"Entry {entry_id} has an unknown status '{entry['status']}'"
            )

        debits = ZERO
        credits = ZERO
        for line in entry["lines"]:
            if line["account"] not in account_numbers:
                raise ValueError(
                    f"Entry {entry_id} uses an unknown account '{line['account']}'"
                )
            debits += Decimal(line["debit"])
            credits += Decimal(line["credit"])

        if debits != credits:
            raise ValueError(
                f"Entry {entry_id} is unbalanced: debits {debits} do not equal credits {credits}"
            )


def signed_amount(account_type, debit, credit):
    """
    The amount a line adds to its account on an income statement.
    Revenue grows with credits, expenses grow with debits.
    Returns None for accounts that do not belong on an income statement.
    """
    if account_type == "revenue":
        return credit - debit
    if account_type == "expense":
        return debit - credit
    return None


def account_totals(ledger, start, end):
    """
    Add up each account's amount over posted entries dated from start to end,
    inclusive. Drafts and voids are ignored. Returns {account_number: Decimal}.
    """
    account_types = {}
    totals = {}
    for account in ledger["accounts"]:
        account_types[account["number"]] = account["type"]
        totals[account["number"]] = ZERO

    for entry in ledger["journal_entries"]:
        if entry["status"] != "posted":
            continue
        # ISO dates (YYYY-MM-DD) compare correctly as plain strings.
        if not (start <= entry["date"] <= end):
            continue
        for line in entry["lines"]:
            number = line["account"]
            amount = signed_amount(
                account_types[number],
                Decimal(line["debit"]),
                Decimal(line["credit"]),
            )
            if amount is not None:
                totals[number] += amount
    return totals


def account_section(ledger, totals, key, title, subtypes):
    """A section with one line per account (in ledger order) and their total."""
    lines = []
    total = ZERO
    for account in ledger["accounts"]:
        if account["subtype"] not in subtypes:
            continue
        amount = totals[account["number"]]
        lines.append(
            {"account": account["number"], "name": account["name"], "amount": amount}
        )
        total += amount
    return {
        "key": key,
        "title": title,
        "kind": "accounts",
        "lines": lines,
        "total": total,
    }


def calculated_section(key, title, parts):
    """
    A calculated row such as Gross profit. parts is a list of (name, Decimal)
    that add up to the result, so the reader can see how it is built.
    Subtractions are passed as negative amounts.
    """
    lines = []
    total = ZERO
    for name, amount in parts:
        lines.append({"account": None, "name": name, "amount": amount})
        total += amount
    return {
        "key": key,
        "title": title,
        "kind": "calculated",
        "lines": lines,
        "total": total,
    }


def render_section(section):
    """Turn a section's Decimal amounts into 2 decimal strings for the response."""
    lines = []
    for line in section["lines"]:
        rendered = dict(line)
        rendered["amount"] = money(line["amount"])
        lines.append(rendered)
    return {
        "key": section["key"],
        "title": section["title"],
        "kind": section["kind"],
        "lines": lines,
        "total": money(section["total"]),
    }


def build_income_statement(ledger, start, end):
    """start and end are 'YYYY-MM-DD' strings. Raises ValueError on bad input."""
    check_date("start", start)
    check_date("end", end)
    # start == end is allowed and gives a single-day statement.
    if start > end:
        raise ValueError(f"'start' ({start}) must not be after 'end' ({end})")

    totals = account_totals(ledger, start, end)

    revenue = account_section(
        ledger, totals, "revenue", "Revenue", ["operating_revenue", "contra_revenue"]
    )

    cogs = account_section(ledger, totals, "cogs", "Cost of goods sold", ["cogs"])

    gross_profit = calculated_section(
        "gross_profit",
        "Gross profit",
        [
            ("Total revenue", revenue["total"]),
            ("Cost of goods sold", -cogs["total"]),
        ],
    )

    operating_expenses = account_section(
        ledger,
        totals,
        "operating_expenses",
        "Operating expenses",
        ["operating_expense"],
    )

    operating_income = calculated_section(
        "operating_income",
        "Operating income",
        [
            ("Gross profit", gross_profit["total"]),
            ("Total operating expenses", -operating_expenses["total"]),
        ],
    )

    other_income = account_section(
        ledger, totals, "other_income", "Other income", ["other_income"]
    )

    net_income = calculated_section(
        "net_income",
        "Net income",
        [
            ("Operating income", operating_income["total"]),
            ("Other income", other_income["total"]),
        ],
    )

    sections = [
        revenue,
        cogs,
        gross_profit,
        operating_expenses,
        operating_income,
        other_income,
        net_income,
    ]
    rendered_sections = []
    for section in sections:
        rendered_sections.append(render_section(section))

    return {
        "company": ledger["company"],
        "currency": ledger["currency"],
        "period": {"start": start, "end": end},
        "sections": rendered_sections,
    }
