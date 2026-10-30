# NUMPE TRADING SOFTWARE

> **“Data-Driven Decisions. Disciplined Investing.”**

Full-Stack Financial Intelligence, Quantitative Investment Monitoring and NLP-Powered Market Research Platform for the **Nifty 100 Equal Weight Index**.

Designed for disciplined long-term index monitoring with transparent indicator evaluations, historical valuation percentiles, real-time news intelligence, and zero speculation.

---

## Key Highlights

* **Tracked Asset:** Nifty 100 Equal Weight Index (`NIFTY100_EQL_WGT.NS` via official NSE data pipelines).
* **Quantitative Signal Engine:** Evaluates 4 systematic entry conditions:
  1. **Price Anchor:** $T = 1.10 \times \left[ \frac{\text{52W Low} + \text{200-Day SMA}}{2} \right]$ (with selectable Mode A & Mode B interpretations).
  2. **Momentum:** RSI (14) with Wilder’s exponential smoothing $< 42.0$.
  3. **Valuation Multiple:** Consolidated P/E $< 20.0$.
  4. **Book Value Support:** P/B ratio within configurable range $[2.7, 3.2]$.
* **Financial News Intelligence:** Ingests live Indian financial RSS feeds, dedupes articles, extracts entities (RBI, SEBI, Nifty constituents), classifies topics across 17 market categories, and generates a daily AI market briefing.
* **Institutional Backtesting:** Simulates 5 distinct investment strategies (including all-condition triggers, value-only, deep-value, and monthly SIP) with CAGR, maximum drawdown, and Sharpe ratio calculations.
* **Responsive Mobile Terminal:** Dark navy & charcoal institutional aesthetic built for desktops, tablets, and smartphones (PWA installable).

---

## Architecture Overview

```
Numpe trading/
├── Dockerfile                  # Unified production multi-stage container
├── docker-compose.yml          # Containerized dev & production setup
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI entry point & SPA file server
│   │   ├── config.py           # Pydantic BaseSettings
│   │   ├── database.py         # Async SQLAlchemy engine & sessionmaker
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic v2 validation models
│   │   ├── routers/            # Clean REST API endpoints (/api/...)
│   │   ├── services/
│   │   │   ├── market_data.py          # Real index price ingestion & history
│   │   │   ├── technical_indicators.py # Wilder's RSI, 200 SMA, MACD
│   │   │   ├── fundamental_valuation.py# Consolidated P/E, P/B, Earnings Yield
│   │   │   ├── signal_engine.py        # 4-condition investment monitor
│   │   │   ├── news_intelligence.py    # NLP news classification & sentiment
│   │   │   ├── backtesting.py          # Quantitative backtest engine
│   │   │   └── scheduler.py            # APScheduler background tasks
│   │   └── utils/
│   │       ├── auth.py                 # JWT token security & admin hash
│   │       └── timezone.py             # IST market hours & holiday awareness
│   └── tests/
│       └── test_quant_calculations.py  # 100% passing automated test suite
├── frontend/
│   ├── src/
│   │   ├── components/                 # Financial terminal UI components
│   │   ├── pages/                      # 8 dedicated full pages
│   │   ├── services/api.ts             # Typed Axios client
│   │   └── types/                      # TypeScript domain models
│   ├── package.json
│   └── vite.config.ts
└── docs/
    ├── VALIDATION_REPORT.md    # Mathematical verification & accuracy report
    └── DEPLOYMENT_GUIDE.md     # Public cloud deployment & HTTPS instructions
```

---

## Quickstart (Local Development)

### 1. Prerequisites
* Python 3.12+ (or 3.14)
* Node.js 18+ & npm

### 2. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run backend API
uvicorn app.main:app --reload --port 8000
```
API Documentation will be available at: `http://localhost:8000/docs`

### 3. Frontend Setup
```bash
cd ../frontend
npm install
npm run dev
```
Frontend development server will open at: `http://localhost:5173`

---

## Running Automated Tests

Run the test suite verifying Wilder's smoothing RSI, SMA calculations, price threshold anchor, P/E earnings yield, and NLP deduplication:

```bash
cd backend
PYTHONPATH=. pytest -v tests/test_quant_calculations.py
```

---

## Public Deployment

See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for full step-by-step instructions.

### 1-Click Cloud Deployment (Render / Railway)
Simply connect this repository to Render or Railway. The root `Dockerfile` automatically builds the React frontend and packages it inside the FastAPI backend. You receive an instant public HTTPS URL (e.g. `https://numpe-trading.onrender.com`) accessible from any mobile device or tablet.

---

## Disclaimers & Intended Usage

NUMPE Trading Software is a personal quantitative financial research and investment monitoring platform. It is not an algorithmic trading bot and **does not execute trades automatically**. Calculations and alerts represent indicator evaluations and do not constitute registered investment advice or guarantees of financial returns.

