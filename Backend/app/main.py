import json
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Income Statement API")

# Allow the React dev server (Vite, port 5173) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Read Backend/data/ledger.json once, when the server starts.
# Every request uses this in-memory copy, so restart the server after editing the file.
LEDGER_FILE = Path(__file__).parent.parent / "data" / "ledger.json"
with open(LEDGER_FILE) as file:
    ledger = json.load(file)


# Every response has the same four fields:
#   status       "success" or "error"
#   status_code  the HTTP status code, repeated in the body for the frontend
#   message      a short human-readable note
#   data         the payload, or null
def success_response(message, data=None):
    return {
        "status": "success",
        "status_code": 200,
        "message": message,
        "data": data,
    }


@app.get("/health")
def health():
    return success_response("Server is running")


@app.get("/ledger")
def get_ledger():
    # Returns the raw ledger (accounts and journal entries) exactly as loaded.
    return success_response("Ledger fetched", ledger)
