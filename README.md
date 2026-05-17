# PyPocket — Unofficial Python API for Pocket Option

> An unofficial, asynchronous Python client for the [Pocket Option](https://pocketoption.com) trading platform.  
> Built for real-time market data, automated trading, and full account management via WebSocket.

---

## ⚠️ Disclaimer

This is an **unofficial** third-party API wrapper. It is not affiliated with, endorsed by, or supported by Pocket Option. Use at your own risk. Trading binary options involves significant financial risk. This library is intended for educational and research purposes only.

---

## ✨ Features

- 📡 **Real-time WebSocket Streaming** — Low-latency live data feed with automatic reconnection
- 🕯️ **Live & Historical Candles** — Subscribe to OHLCV data for any asset and timeframe
- 💹 **Automated Trading** — Execute binary options (buy/sell) programmatically
- 💰 **Balance Management** — Track real-time account balance and trade history
- 🌍 **Multi-Region Support** — Connect to EU, Asia, US, Russia, India, Demo, and more
- ⏱️ **Smart Expiry Calculation** — Automatic expiration time rounding to `:30` second boundaries
- 🔄 **Session Persistence** — Reconnect logic and WebSocket keep-alive pings
- 🧵 **Thread-safe Design** — SSL mutual exclusion for concurrent read/write safety
- 🗂️ **Local Caching** — JSON-based cache for historical data and state persistence

---

## 📦 Installation

```bash
git clone https://github.com/Sudip-T/pocketoption-api.git
cd pocketoption-api
pip install -r requirements.txt
```

### Requirements

- Python 3.8+
- `websocket-client`
- `requests`
- `pause`

---

## 🚀 Quick Start

```python
from pocketoptionapi.stable_api import PocketOption

# Connect to demo account
client = PocketOption(ssid="your_session_id", demo=True)
client.connect()

# Change to a symbol and timeframe
client.change_symbol("EURUSD_otc", 60)  # 60 seconds

# Place a trade
result, order_id = client.buy(
    amount=10,            # $10
    active="EURUSD_otc",
    action="call",        # "call" (up) or "put" (down)
    expirations=1         # 1 minute
)

# Check trade result
profit, status = client.check_win(order_id)
print(f"Status: {status}, Profit: {profit}")
```

---

## 🌍 Region Selection

Connect to different regional servers using the built-in `REGION` constants:

```python
from pocketoptionapi.constants import REGION

region = REGION()

# Available regions:
# EUROPA, SEYCHELLES, HONGKONG, SERVER1, FRANCE, FRANCE2
# UNITED_STATES, UNITED_STATES2, UNITED_STATES3, UNITED_STATES4
# RUSSIA, INDIA, FINLAND, ASIA, SERVER2, SERVER3, SERVER4
# DEMO, DEMO_2

url = region.REGIONS["EUROPA"]
url = region.REGIONS["DEMO"]   # For paper trading
```

---

## 📊 Supported Operations

| Category       | Functionality                                        |
|----------------|------------------------------------------------------|
| **Trading**    | Buy/Sell options, custom expiry, multi-option orders |
| **Market Data**| Live candles, historical candles, payout rates       |
| **Account**    | Balance inquiry, open/closed positions, trade history|
| **Utilities**  | Server time sync, symbol change, WebSocket ping      |
| **Caching**    | Local JSON cache for historical data                 |

---

## ⏱️ Expiration Time Utilities

The `expiration.py` module provides helpers for computing trade expiry timestamps:

```python
from pocketoptionapi.expiration import get_expiration_time, get_remaning_time
import time

timestamp = time.time()

# Get expiration timestamp for a 5-minute trade
expiry = get_expiration_time(timestamp, duration=5)

# Get list of upcoming expiry windows with remaining seconds
windows = get_remaning_time(timestamp)
for duration, remaining in windows:
    print(f"{duration}min expiry — {remaining}s remaining")
```

Expiration times are always snapped to the `:30` second mark of the target minute.

---

## 🗂️ Project Structure

```
pocketoption-api/
├── pocketoptionapi/
│   ├── stable_api.py         # High-level user-facing API
│   ├── api.py                # Core PocketOptionAPI class
│   ├── pocket.py             # Low-level WebSocket client
│   ├── constants.py          # Regional WebSocket URLs
│   ├── expiration.py         # Expiry time calculation utilities
│   ├── global_value.py       # Shared state and logging
│   └── ws/
│       ├── client.py         # WebSocket connection handler
│       ├── channels/         # WebSocket message channels
│       │   ├── ssid.py
│       │   ├── buyv3.py
│       │   ├── candles.py
│       │   ├── get_balances.py
│       │   └── change_symbol.py
│       └── objects/          # Data models
│           ├── candles.py
│           ├── timesync.py
│           └── time_sync.py
```

---

## ⚙️ Configuration & Logging

Log verbosity is controlled via `global_value.loglevel`:

```python
import pocketoptionapi.global_value as global_value

global_value.loglevel = "DEBUG"   # Show all messages
global_value.loglevel = "INFO"    # Show info messages (default)
global_value.loglevel = "ERROR"   # Show errors only
```

---

## 🔧 Advanced Usage

### Fetching Payout Data

```python
payout = client.GetPayoutData()
print(payout)
```

### Fetching Closed Deals

```python
deals = client.GetClosedDeals()
for deal in deals:
    print(deal)
```

### Server Time Synchronization

The API automatically synchronizes with the PocketOption server clock using `TimeSynchronizer`. You can access the synced datetime:

```python
synced_time = client.api.synced_datetime
print(f"Server time: {synced_time}")
```

---

## 🤝 Contributing

Contributions, bug reports, and feature requests are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

Inspired by community efforts to build open tooling around trading platform WebSocket APIs. Special thanks to contributors and testers.

---

> **Note:** Always test with a demo account before using real funds. The authors are not responsible for any financial losses incurred through use of this software.