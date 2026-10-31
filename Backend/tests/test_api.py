"""The HTTP endpoint: response shape and input validation."""
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def get(query):
    return client.get("/income-statement" + query)


def test_success_response_shape():
    r = get("?start=2026-01-01&end=2026-03-31")
    body = r.json()
    assert r.status_code == 200
    assert body["status"] == "success"
    assert body["status_code"] == 200
    assert body["data"]["period"] == {"start": "2026-01-01", "end": "2026-03-31"}
    assert body["data"]["sections"][-1]["total"] == "-44480.14"


def test_parameter_order_does_not_matter():
    assert get("?end=2026-03-31&start=2026-01-01").status_code == 200


def test_start_equal_to_end_is_allowed():
    assert get("?start=2026-03-31&end=2026-03-31").status_code == 200


def test_future_dates_are_allowed():
    assert get("?start=2030-01-01&end=2030-12-31").status_code == 200


@pytest.mark.parametrize(
    "query, expected_message",
    [
        ("", "Missing required query parameter(s): start, end"),
        ("?start=2026-01-01", "Missing required query parameter(s): end"),
        ("?end=2026-03-31", "Missing required query parameter(s): start"),
        ("?start=2026-1-1&end=2026-03-31", "YYYY-MM-DD"),
        ("?start=20260101&end=2026-03-31", "YYYY-MM-DD"),
        ("?start=abc&end=2026-03-31", "YYYY-MM-DD"),
        ("?start=2026-01-01&end=", "YYYY-MM-DD"),
        ("?start=2026-02-30&end=2026-03-31", "must be a real date"),
        ("?start=2026-01-01&end=2026-13-01", "must be a real date"),
        ("?start=2026-03-31&end=2026-01-01", "must not be after"),
    ],
)
def test_invalid_input_returns_422(query, expected_message):
    r = get(query)
    body = r.json()
    assert r.status_code == 422
    assert body["status"] == "error"
    assert body["status_code"] == 422
    assert body["data"] is None
    assert expected_message in body["message"]


def test_leap_day_is_a_real_date():
    assert get("?start=2028-02-29&end=2028-03-01").status_code == 200
    assert get("?start=2026-02-29&end=2026-03-01").status_code == 422


def test_health_and_ledger_endpoints():
    assert client.get("/health").json()["status"] == "success"
    ledger = client.get("/ledger").json()["data"]
    assert len(ledger["journal_entries"]) == 25
