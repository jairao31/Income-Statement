import json
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.income_statement import build_income_statement, validate_ledger

app = FastAPI(title="Income Statement API")

# Allow the React dev server (Vite, port 5173) to call this API from the browser.
# Without this, browsers block the requests. Only GET is needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Read Backend/data/ledger.json once, when the server starts, and check it is well-formed.
# A bad ledger stops the server here, with a clear message.
LEDGER_FILE = Path(__file__).parent.parent / "data" / "ledger.json"
with open(LEDGER_FILE) as file:
    ledger = json.load(file)
validate_ledger(ledger)


# ---------------------------------------------------------------------------
# Response format
# Every response (success or error) has the same four fields:
#   status       "success" or "error"
#   status_code  the HTTP status code, repeated in the body for the frontend
#   message      a short human-readable note
#   data         the payload, or null on errors
# ---------------------------------------------------------------------------
def success_response(message, data=None):
    return {
        "status": "success",
        "status_code": 200,
        "message": message,
        "data": data,
    }


def error_response(message, status_code=422):
    """422 = invalid input."""
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "status_code": status_code,
            "message": message,
            "data": None,
        },
    )


@app.exception_handler(RequestValidationError)
def handle_missing_params(request, exc):
    # FastAPI calls this automatically when a required query parameter, like
    # start or end, is missing from the URL. It makes those errors match our format.
    missing = [e["loc"][-1] for e in exc.errors() if e["type"] == "missing"]
    if missing:
        return error_response(
            f"Missing required query parameter(s): {', '.join(missing)}"
        )
    return error_response("Invalid request")


@app.get("/health")
def health():
    return success_response("Server is running")


@app.get("/ledger")
def get_ledger():
    # Returns the raw ledger (accounts and journal entries) exactly as loaded.
    return success_response("Ledger fetched", ledger)


@app.get("/income-statement")
def get_income_statement(start: str = Query(...), end: str = Query(...)):
    # GET /income-statement?start=YYYY-MM-DD&end=YYYY-MM-DD
    # build_income_statement checks the dates and raises ValueError with a
    # readable message, so the date rules live in one place (income_statement.py).
    try:
        data = build_income_statement(ledger, start, end)
    except ValueError as error:
        return error_response(str(error))
    return success_response("Income statement generated", data)
