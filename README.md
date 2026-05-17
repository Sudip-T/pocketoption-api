# PyPocket — Unofficial Python API for Pocket Option

A comprehensive, asynchronous Python wrapper for the Pocket Option trading platform. Built for reliability and ease of use, this API provides real-time market data streaming, automated trading capabilities, and full account management functionality.

## ✨ Features

- **Real-time Candle Streaming** — Subscribe to live OHLCV data for any asset
- **Automated Trading** — Execute binary options trades programmatically
- **Balance Management** — Real-time account balance tracking
- **Multi-Region Support** — Connect to EU, Asia, US, or Demo servers
- **WebSocket Integration** — Low-latency real-time data feed
- **Async Architecture** — Non-blocking operations for high-frequency strategies
- **Session Persistence** — Automatic reconnection and state management

## 📦 Supported Operations

| Category | Methods |
|----------|---------|
| Trading | Buy/Sell options, Custom expiry times |
| Market Data | Live candles, Historical data, Payout rates |
| Account | Balance inquiry, Open/closed positions |
| Utilities | Server time sync, Symbol management |

## 🚀 Quick Example

```python
from pocketoptionapi import PocketOption

client = PocketOption(ssid="your_session_id", demo=True)
client.connect()

# Subscribe to 1-minute EURUSD candles
client.change_symbol("EURUSD_otc", 60)

# Execute a trade
result, order_id = client.buy(
    amount=10,           # $10
    active="EURUSD_otc",
    action="call",       # or "put"
    expirations=1        # 1 minute
)

# Check result
profit, status = client.check_win(order_id)
