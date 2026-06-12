# Binance Futures Testnet Trading Bot

A clean, production-style Python CLI app to place orders on Binance Futures Testnet (USDT-M).
Supports MARKET, LIMIT, and STOP_MARKET orders with structured logging and full error handling.

---

## Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py         # Package metadata
│   ├── client.py           # Binance REST client (HMAC signing, retries)
│   ├── orders.py           # Order placement logic
│   ├── validators.py       # Input validation
│   ├── logging_config.py   # Rotating file + console logging
│   └── cli.py              # argparse CLI entry point
├── logs/
│   └── trading_bot.log     # Auto-created on first run
├── README.md
└── requirements.txt
```

---

## Setup

### Step 1 — Get Testnet API Keys

1. Go to https://testnet.binancefuture.com
2. Log in with GitHub account
3. Click "API Key" at the top -> copy your API Key and Secret Key

### Step 2 — Clone / Download the Project

```bash
git clone https://github.com/YOUR_USERNAME/trading_bot.git
cd trading_bot
```

### Step 3 — Create a Virtual Environment

```bash
python -m venv venv

# Activate:
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Set API Credentials

```bash
# macOS/Linux:
export BINANCE_API_KEY="your_api_key_here"
export BINANCE_API_SECRET="your_secret_here"

# Windows CMD:
set BINANCE_API_KEY=your_api_key_here
set BINANCE_API_SECRET=your_secret_here
```

---

## How to Run

### MARKET Order

```bash
python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
python -m bot.cli --symbol ETHUSDT --side SELL --type MARKET --quantity 0.01
```

### LIMIT Order

```bash
python -m bot.cli --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.001 --price 60000
python -m bot.cli --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500
```

### STOP_MARKET Order (Bonus)

```bash
python -m bot.cli --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --price 58000
```

### Dry Run (no order placed)

```bash
python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --dry-run
```

### Full JSON Response

```bash
python -m bot.cli --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --json
```

---

## Sample Output

### MARKET BUY (success)
```
--- Order Request ---
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001

Order placed successfully
--- Order Response ---
  Order ID      : 4183920571
  Symbol        : BTCUSDT
  Side          : BUY
  Type          : MARKET
  Status        : FILLED
  Orig Qty      : 0.001
  Executed Qty  : 0.001
  Avg Price     : 67423.50
```

---

## All CLI Flags

| Flag           | Required        | Description                             |
|----------------|-----------------|-----------------------------------------|
| --symbol       | Yes             | Trading pair e.g. BTCUSDT              |
| --side         | Yes             | BUY or SELL                             |
| --type         | Yes             | MARKET, LIMIT, or STOP_MARKET          |
| --quantity     | Yes             | Order quantity (base asset)             |
| --price        | LIMIT/STOP only | Limit price or stop trigger price       |
| --api-key      | No (use env)    | Binance API key                         |
| --api-secret   | No (use env)    | Binance API secret                      |
| --dry-run      | No              | Validate inputs, no order placed        |
| --json         | No              | Print full raw API response as JSON     |
| --log-level    | No              | DEBUG (default) or INFO                 |

---

## Logs

Saved to logs/trading_bot.log automatically.
- Console: INFO and above
- File: DEBUG and above (full request/response detail)
- Rotates at 5 MB, keeps 5 backups

---

## Assumptions

1. Testnet only — base URL is https://testnet.binancefuture.com
2. USDT-M Futures market only
3. LIMIT orders use timeInForce=GTC by default
4. Uses only `requests` library (no python-binance) for transparency
5. Python 3.8+ required

---

## Common Errors

| Error | Fix |
|-------|-----|
| [Binance -1121] Invalid symbol | Check symbol name (e.g. BTCUSDT not BTC-USDT) |
| [Binance -2019] Margin insufficient | Claim free funds on testnet dashboard |
| [Binance -1111] Precision over maximum | Use fewer decimals in quantity/price |
| Missing API credentials | Export env vars or use --api-key flag |

---

## Dependencies

```
requests>=2.31.0
urllib3>=2.0.0
```
