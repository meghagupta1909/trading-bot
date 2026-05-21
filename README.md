# 🤖 Binance Futures Trading Bot

A production-grade trading bot for **Binance Futures Testnet (USDT-M)** built with **FastAPI + React**. Supports MARKET, LIMIT, and STOP-LIMIT orders with full input validation, structured rotating logs, centralised error handling, a REST API, CLI, and a modern dark dashboard UI.

---

## 📸 Screenshots

> _Place order form and live log viewer — dark trading dashboard_

```
┌─────────────────────────────────────────────────────────┐
│  🤖 FuturesBot   Binance Testnet          ● Connected    │
├───────────────────┬─────────────────────────────────────┤
│  Place Order      │  System Status  │  Recent Orders     │
│  ─────────────    │  ─────────────  │  ──────────────    │
│  [BUY] [SELL]     │  Testnet: ✅    │  BTCUSDT BUY       │
│  Symbol: BTCUSDT  │  Version: 1.0.0 │  FILLED  #2897127  │
│  Type: MARKET     │                 │                     │
│  Qty: 0.01        ├─────────────────┴─────────────────── │
│                   │  Log Viewer                           │
│  [BUY MARKET]     │  > 10:01:13 INFO Order placed ✅     │
└───────────────────┴─────────────────────────────────────┘
```

---

## ✨ Features

| Feature | Details |
|---|---|
| **Order Types** | MARKET, LIMIT, STOP-LIMIT (bonus) |
| **Sides** | BUY and SELL |
| **CLI** | Typer-based with Rich output |
| **REST API** | FastAPI + Swagger docs at `/docs` |
| **Frontend** | React + Vite + TailwindCSS dark dashboard |
| **Validation** | Pydantic v2 + custom validators |
| **Logging** | Rotating file logs (trading_bot, orders, errors) |
| **Error Handling** | Centralised exception handlers + HTTP error mapping |
| **Docker** | Full docker-compose stack |
| **Tests** | Pytest with mocked Binance API |

---

## 🗂 Project Structure

```
trading-bot/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py          # Combines all routers
│   │   │   ├── orders.py            # POST /api/orders/place
│   │   │   ├── health.py            # GET /api/health, /api/logs/*
│   │   │   └── exception_handlers.py
│   │   ├── core/
│   │   │   ├── config.py            # Pydantic settings / env vars
│   │   │   ├── exceptions.py        # Custom exception hierarchy
│   │   │   └── logging_config.py    # Rotating file + console logging
│   │   ├── models/
│   │   │   └── schemas.py           # Pydantic request/response schemas
│   │   ├── services/
│   │   │   ├── binance_client.py    # Async HMAC-signed REST client
│   │   │   └── order_service.py     # Business logic / orchestration
│   │   ├── validators/
│   │   │   └── order_validator.py   # Input validation helpers
│   │   ├── utils/
│   │   │   └── log_utils.py         # Log file reading utilities
│   │   └── main.py                  # FastAPI app factory + lifespan
│   ├── logs/                        # Rotating log files (gitignored)
│   │   ├── trading_bot.log
│   │   ├── orders.log
│   │   └── errors.log
│   ├── tests/
│   │   ├── test_validators.py
│   │   └── test_api.py
│   ├── cli.py                       # Typer CLI entry point
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   ├── OrderForm.jsx        # Main trading form
│   │   │   ├── OrderResult.jsx      # Order response display
│   │   │   ├── OrderHistory.jsx     # Session order history
│   │   │   ├── HealthPanel.jsx      # System status
│   │   │   ├── LogViewer.jsx        # Live log tail viewer
│   │   │   ├── StatusBadge.jsx
│   │   │   └── Spinner.jsx
│   │   ├── hooks/
│   │   │   ├── useHealth.js
│   │   │   └── useLogs.js
│   │   ├── services/
│   │   │   └── api.js               # Axios API service
│   │   ├── utils/
│   │   │   └── formatters.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.js
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Environment Variables

### Backend (`backend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `BINANCE_API_KEY` | ✅ | — | Binance Futures Testnet API key |
| `BINANCE_SECRET_KEY` | ✅ | — | Binance Futures Testnet secret key |
| `BINANCE_BASE_URL` | ❌ | `https://testnet.binancefuture.com` | Testnet base URL |
| `LOG_LEVEL` | ❌ | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `DEBUG` | ❌ | `false` | Enable Uvicorn auto-reload |
| `PORT` | ❌ | `8000` | Server port |

### Frontend (`frontend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `VITE_API_URL` | ❌ | `""` | Backend base URL (empty = Vite proxy) |

---

## 🚀 Local Setup (Without Docker)

### 1. Prerequisites

- Python 3.11+
- Node.js 18+
- A [Binance Futures Testnet](https://testnet.binancefuture.com) account with API credentials

### 2. Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp .env.example .env
# Edit .env — set BINANCE_API_KEY and BINANCE_SECRET_KEY

# Start the API server
uvicorn app.main:app --reload --port 8000
```

The API is now available at:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health:** http://localhost:8000/api/health

### 3. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure (optional — Vite proxies /api to localhost:8000 by default)
cp .env.example .env

# Start dev server
npm run dev
```

Dashboard: http://localhost:5173

---

## 🐳 Docker Setup

```bash
# 1. Clone and enter the project
cd trading-bot

# 2. Set credentials
cp .env.example .env
# Edit .env with your BINANCE_API_KEY and BINANCE_SECRET_KEY

# 3. Build and start
docker-compose up --build

# 4. Access
#    Frontend:  http://localhost
#    API docs:  http://localhost:8000/docs
#    Health:    http://localhost:8000/api/health

# Stop
docker-compose down
```

---

## 💻 CLI Usage

All CLI commands are run from the `backend/` directory with the virtual environment active.

### Place a MARKET order

```bash
python cli.py place-order --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

### Place a LIMIT order

```bash
python cli.py place-order \
  --symbol ETHUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 0.1 \
  --price 3200
```

### Place a STOP-LIMIT order (bonus)

```bash
python cli.py place-order \
  --symbol BTCUSDT \
  --side BUY \
  --type STOP_LIMIT \
  --quantity 0.01 \
  --price 65000 \
  --stop-price 64500
```

### Interactive mode (prompted)

```bash
python cli.py place-order
# CLI will prompt for each required field
```

### Check connectivity

```bash
python cli.py health
```

### View recent logs

```bash
python cli.py recent-logs
python cli.py recent-logs --file orders.log --lines 50
```

---

## 🌐 API Reference

Base URL: `http://localhost:8000`

### POST `/api/orders/place`

Place a futures order.

**Request body:**

```json
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "type": "MARKET",
  "quantity": "0.01"
}
```

**LIMIT order:**

```json
{
  "symbol": "ETHUSDT",
  "side": "SELL",
  "type": "LIMIT",
  "quantity": "0.1",
  "price": "3200.00",
  "time_in_force": "GTC"
}
```

**STOP-LIMIT order:**

```json
{
  "symbol": "BTCUSDT",
  "side": "BUY",
  "type": "STOP_LIMIT",
  "quantity": "0.01",
  "price": "65000",
  "stop_price": "64500"
}
```

**Response:**

```json
{
  "success": true,
  "message": "Order placed successfully [orderId=2897127894]",
  "request_summary": {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
    "quantity": "0.01",
    "price": "N/A",
    "stop_price": "N/A"
  },
  "order": {
    "orderId": 2897127894,
    "clientOrderId": "web_VKVRyXnLVVXdv9YT3FKO",
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
    "status": "FILLED",
    "origQty": "0.01",
    "executedQty": "0.01",
    "avgPrice": "65023.40"
  },
  "error": null
}
```

### GET `/api/health`

```json
{
  "status": "ok",
  "version": "1.0.0",
  "binance_connected": true,
  "message": "All systems operational"
}
```

### GET `/api/logs/recent?log_file=trading_bot.log&lines=100`

Returns last N log lines from the specified log file.

### GET `/api/logs/files`

Returns list of available log files.

---

## 🧪 Running Tests

```bash
cd backend
source .venv/bin/activate

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --tb=short
```

---

## 📋 Validation Rules

| Field | Rule |
|---|---|
| `symbol` | Uppercase alphanumeric, 2–20 chars (e.g. `BTCUSDT`) |
| `side` | Must be `BUY` or `SELL` |
| `type` | Must be `MARKET`, `LIMIT`, or `STOP_LIMIT` |
| `quantity` | Decimal > 0 |
| `price` | Decimal > 0 — **required** for LIMIT and STOP_LIMIT |
| `stop_price` | Decimal > 0 — **required** for STOP_LIMIT |

---

## 📁 Log Files

| File | Contents |
|---|---|
| `trading_bot.log` | All log events (INFO+) — main log |
| `orders.log` | Order placement events only |
| `errors.log` | ERROR and CRITICAL events only |

All log files rotate at 10 MB with 5 backup copies kept.

---

## 🏗 Architecture

```
CLI (cli.py / Typer)
        │
        ▼
FastAPI App (app/main.py)
        │
   ┌────┴────┐
   │  API    │  ← Pydantic request validation + exception handlers
   │ Routers │     (app/api/orders.py, app/api/health.py)
   └────┬────┘
        │
   ┌────▼─────────┐
   │ Order Service │  ← Business logic, validation orchestration
   │               │     (app/services/order_service.py)
   └────┬──────────┘
        │
   ┌────▼─────────┐
   │ Binance      │  ← HMAC-SHA256 signed async REST calls
   │ Client       │     (app/services/binance_client.py)
   └──────────────┘
```

---

## 💡 Assumptions

1. **Testnet only** — `BINANCE_BASE_URL` defaults to `https://testnet.binancefuture.com`. Never use real funds.
2. **STOP_LIMIT** maps to Binance Futures `STOP_MARKET` with a limit price — this is the standard stop-limit behaviour on USDM futures.
3. **Quantity precision** — the app sends quantities as-is. For production use, quantities must respect the `LOT_SIZE` filter from `GET /fapi/v1/exchangeInfo`.
4. **No position management** — this bot places orders only; it does not track P&L, manage positions, or cancel open orders automatically.
5. **Single-instance** — designed for manual/interactive use; not a HFT or automated strategy runner.

---

## 📧 Submission

Email the repository link + log files to:
- joydip@anything.ai
- chetan@anything.ai
- hello@anything.ai
- CC: sonika@anything.ai