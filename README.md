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

