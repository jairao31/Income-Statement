"""validate_ledger stops a malformed ledger before it can give wrong numbers."""
import json
from pathlib import Path

import pytest

from app.income_statement import validate_ledger
from tests.helpers import entry, make_ledger, sale

REAL_LEDGER = json.load(open(Path(__file__).parent.parent / "data" / "ledger.json"))


def test_real_ledger_is_valid():
    validate_ledger(REAL_LEDGER)


def test_well_formed_ledger_passes():
    validate_ledger(make_ledger(sale("A", "2026-01-05", "100.00")))


def test_unknown_account_is_rejected():
    ledger = make_ledger(entry("A", "2026-01-05", [("1000", "50.00", "0.00"), ("9999", "0.00", "50.00")]))
    with pytest.raises(ValueError, match="Entry A uses an unknown account '9999'"):
        validate_ledger(ledger)


def test_unbalanced_entry_is_rejected():
    ledger = make_ledger(entry("A", "2026-01-05", [("1000", "100.00", "0.00"), ("4000", "0.00", "99.99")]))
    with pytest.raises(ValueError, match="Entry A is unbalanced"):
        validate_ledger(ledger)


def test_unknown_status_is_rejected():
    # "Posted" with a capital P would otherwise be silently left out of every statement.
    ledger = make_ledger(sale("A", "2026-01-05", "100.00", status="Posted"))
    with pytest.raises(ValueError, match="Entry A has an unknown status 'Posted'"):
        validate_ledger(ledger)


def test_drafts_and_voids_are_checked_too():
    bad_void = entry("A", "2026-01-05", [("1000", "10.00", "0.00"), ("4000", "0.00", "5.00")], status="void")
    with pytest.raises(ValueError, match="Entry A is unbalanced"):
        validate_ledger(make_ledger(bad_void))
