# Income Statement

A full-stack app that produces an **income statement (P&L)** for Northwind Coffee Roasters over any date range, built from a chart of accounts and double-entry journal entries.

Take-home assessment for the Software Engineer role at Campfire.

| Layer | Stack |
| --- | --- |
| Backend | Python, FastAPI |
| Frontend | React 18, Vite, Material UI |
| Tests | pytest |

## Demo video
https://github.com/user-attachments/assets/8cd238af-d2ac-4552-b098-4174f82ee027


## Quick start

You need two terminals, one for each service.

**Terminal 1: Backend** (http://localhost:8000)

First time only:

```bash
cd Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start the server (after the first time, run `cd Backend` and `source .venv/bin/activate` first):

```bash
uvicorn app.main:app --reload --port 8000
```

**Terminal 2: Frontend** (http://localhost:5173)

First time only:

```bash
cd Frontend
npm install
```

Start the app:

```bash
npm run dev
```

Then open http://localhost:5173.

Useful backend URLs:

- Health check: http://localhost:8000/health
- Interactive API docs (Swagger): http://localhost:8000/docs

> The backend only allows CORS from `http://localhost:5173` and `http://127.0.0.1:5173`. If Vite picks another port, update the allowed origins in `Backend/app/main.py`.

## Tests

```bash
cd Backend
source .venv/bin/activate
pytest
```

## API

```
GET /income-statement?start=YYYY-MM-DD&end=YYYY-MM-DD
```

Returns the statement for the inclusive date range. Every response, success or error, has the same four fields:

```json
{ "status": "success", "status_code": 200, "message": "Income statement generated", "data": { } }
```

`data.sections` is an ordered list of seven sections:

Revenue → Cost of goods sold → **Gross profit** → Operating expenses → **Operating income** → Other income → **Net income**

- Sections with `"kind": "accounts"` list one line per account (`account`, `name`, `amount`) and a `total`.
- Sections with `"kind": "calculated"` (gross profit, operating income, net income) list the components they are built from and a `total`.
- All amounts are strings with two decimals, such as `"35650.75"`. Negative amounts are prefixed with `-`.

Invalid input (missing or malformed dates, start after end) returns HTTP 422 with `"status": "error"` and a message.

Other endpoints: `GET /health` and `GET /ledger` (the raw data).

The data lives in `Backend/data/ledger.json` and is read once when the server starts.

Assumptions and design decisions are in [NOTES.md](NOTES.md).

## Project structure

```
.
├── Backend/
│   ├── app/
│   │   ├── main.py              API endpoints and input validation
│   │   └── income_statement.py  the accounting logic
│   ├── data/ledger.json         chart of accounts and journal entries
│   ├── tests/                   pytest tests
│   └── requirements.txt
├── Frontend/
│   └── src/                     React app (App, api, format, components)
├── NOTES.md                     Decisions, assumptions, verification
└── README.md
```

## Environment

Developed and run on macOS.

| Tool | Version |
| --- | --- |
| Python | 3.15.1 |
| FastAPI | 0.162.0 |
| Uvicorn | 0.54.0 |
| Pydantic | 2.14.2 |
| pytest | 9.2.0 |
| Node.js | 26.13.0 |
| npm | 11.20.0 |
| React | 18.3.1 |
| Vite | 8.3.5 |
| Material UI | 9.5.0 |

Node can be installed with `brew install node`.

## Author

**Jaiganesh Rao**

+1 (551) 689-6918 · jaiganesh.rao31@gmail.com · Jersey City, NJ
[LinkedIn](https://linkedin.com/in/jaiganeshrao) · [Portfolio](https://jaiganesh-rao.vercel.app)
