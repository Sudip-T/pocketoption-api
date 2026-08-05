# # """
# # PyPocket — Real-time Candle & Tick Data
# # =========================================
# # Fixes the timing issue: waits for updateHistoryNewFast before
# # calling get_candles(), then prints live updateStream ticks.
# # """

# # import time
# # import json
# # from datetime import datetime
# # import pocketoptionapi.state as global_value
# # from pocketoptionapi.pocketapi import PocketOption

# # # ── Paste your SSID here ──────────────────────────────────────────────────────
# # YOUR_SSID = YOUR_SSID
# # # ─────────────────────────────────────────────────────────────────────────────

# # ASSET  = "EURUSD_otc"
# # PERIOD = 5   # seconds per candle (60 = 1-minute candles)


# # def wait_for(fn, timeout=15, poll=0.3, label=""):
# #     start = time.time()
# #     while time.time() - start < timeout:
# #         if fn():
# #             return True
# #         time.sleep(poll)
# #     print(f"  [TIMEOUT] {label}")
# #     return False


# # # ── 1. Connect ────────────────────────────────────────────────────────────────
# # print("Connecting...")
# # client = PocketOption(ssid=YOUR_SSID, demo=True)
# # client.connect()

# # wait_for(client.check_connect, timeout=15, label="websocket connect")
# # wait_for(lambda: client.get_balance() is not None, timeout=10, label="balance")
# # print(f"Connected! Balance: {client.get_balance()}")


# # # ── 2. Subscribe to symbol — this triggers updateHistoryNewFast ───────────────
# # print(f"\nSubscribing to {ASSET} @ {PERIOD}s candles...")
# # client.change_symbol(ASSET, PERIOD)

# # # Wait for history_new to be populated by the WS message handler
# # print("Waiting for history data from server...")
# # got_history = wait_for(
# #     lambda: client.api.history_new is not None,
# #     timeout=15,
# #     label="history_new (updateHistoryNewFast)"
# # )

# # if not got_history:
# #     print("  Server did not send history. Try a different asset or check your session.")
# # else:
# #     his = client.api.history_new

# #     # ── Parse OHLCV candles ───────────────────────────────────────────────────
# #     candles = []
# #     for c in his.get("candles", []):
# #         # Format: [timestamp, open, close, high, low, volume]
# #         candles.append({
# #             "time"  : datetime.fromtimestamp(c[0]).strftime("%H:%M:%S"),
# #             "open"  : c[1],
# #             "close" : c[2],
# #             "high"  : c[3],
# #             "low"   : c[4],
# #             "vol"   : c[5],
# #         })
# #     candles.sort(key=lambda x: x["time"])

# #     print(f"\n{'='*60}")
# #     print(f"OHLCV CANDLES  ({len(candles)} bars, {PERIOD}s each)")
# #     print(f"{'='*60}")
# #     print(f"{'Time':<10} {'Open':>9} {'High':>9} {'Low':>9} {'Close':>9} {'Vol':>5}")
# #     print("-" * 60)
# #     for c in candles[-10:]:   # show last 10 candles
# #         print(f"{c['time']:<10} {c['open']:>9.5f} {c['high']:>9.5f} {c['low']:>9.5f} {c['close']:>9.5f} {c['vol']:>5}")

# #     # ── Parse raw tick history ────────────────────────────────────────────────
# #     ticks = his.get("history", [])
# #     if ticks:
# #         print(f"\n{'='*60}")
# #         print(f"RAW TICKS  (last 5 of {len(ticks)} ticks)")
# #         print(f"{'='*60}")
# #         for ts, price in ticks[-5:]:
# #             t = datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f")[:-3]
# #             print(f"  {t}  →  {price:.5f}")

# #     # ── Also process into DataFrame via stable_api helper ─────────────────────
# #     ohlcv_list = PocketOption.process_data_history(
# #         {"history": [[t, p] for t, p in ticks]},
# #         period=PERIOD
# #     )
# #     print(f"\nDataFrame-style OHLCV bars built: {len(ohlcv_list)}")


# # # ── 3. Live tick stream — runs for N seconds ──────────────────────────────────
# # STREAM_SECONDS = 15
# # print(f"\n{'='*60}")
# # print(f"LIVE TICK STREAM  ({STREAM_SECONDS}s)  —  {ASSET}")
# # print(f"{'='*60}")

# # seen = set()
# # end = time.time() + STREAM_SECONDS

# # while time.time() < end:
# #     # global_value.pairs is updated by the WS handler for updateStream ticks
# #     pair_data = global_value.pairs.get(ASSET, {})
# #     history   = pair_data.get("history", [])

# #     for tick in history:
# #         key = (tick["time"], tick["price"])
# #         if key not in seen:
# #             seen.add(key)
# #             t = datetime.fromtimestamp(tick["time"]).strftime("%H:%M:%S.%f")[:-3]
# #             print(f"  {t}  →  {tick['price']:.5f}")

# #     time.sleep(0.1)

# # print(f"\nStream ended. Total ticks captured: {len(seen)}")

# # # ── 4. Disconnect ─────────────────────────────────────────────────────────────
# # client.disconnect()
# # print("Done.")




# """
# PyPocket — Multi-Pair Live Streaming
# =====================================
# Streams ticks and builds live candles for multiple assets
# simultaneously using a single WebSocket connection.
# """

# import time
# from datetime import datetime
# import pocketoptionapi.state as state
# from pocketoptionapi.pocketapi import PocketOption

# # ── Config ────────────────────────────────────────────────────────────────────

# ASSETS = [
#     "EURUSD_otc",
#     "GBPUSD_otc",
#     "AUDJPY_otc",
#     "BTCUSD_otc",
#     "XAUUSD_otc",
# ]

# PERIOD       = 60    # candle period in seconds
# STREAM_SECS  = 120   # how long to run the live stream
# # ─────────────────────────────────────────────────────────────────────────────


# def wait_for(fn, timeout=15, poll=0.3, label=""):
#     start = time.time()
#     while time.time() - start < timeout:
#         if fn():
#             return True
#         time.sleep(poll)
#     print(f"  [TIMEOUT] {label}")
#     return False


# def fmt(ts):
#     return datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f")[:-4]


# # ── Connect ───────────────────────────────────────────────────────────────────
# print("Connecting...")
# client = PocketOption(ssid=YOUR_SSID, demo=True)
# client.connect()

# wait_for(client.check_connect, timeout=15, label="websocket")
# wait_for(lambda: client.get_balance() is not None, timeout=10, label="balance")
# print(f"✓ Connected  |  Balance: ${client.get_balance():,.2f}\n")


# # ── Subscribe to all pairs ────────────────────────────────────────────────────
# # The server starts streaming updateStream ticks for each asset
# # as soon as change_symbol() is called. Subscribe with a short
# # gap so the server doesn't drop messages.
# print("Subscribing to pairs...")
# for asset in ASSETS:
#     client.change_symbol(asset, PERIOD)
#     print(f"  ✓ {asset}")
#     time.sleep(0.5)   # small gap between subscriptions

# # Wait for at least one history_new to confirm connection is live
# print("\nWaiting for first history response...")
# wait_for(lambda: client.api.history_new is not None, timeout=15, label="history_new")
# time.sleep(2)   # let remaining histories arrive


# # ── Print last 3 closed candles per pair ─────────────────────────────────────
# his = client.api.history_new  # most recently received history
# if his:
#     asset = his.get("asset", "?")
#     closed = sorted(his.get("candles", []), key=lambda c: c[0])
#     print(f"\n── Closed candles: {asset} ──────────────────────────────")
#     print(f"  {'Time':<10} {'Open':>8} {'High':>8} {'Low':>8} {'Close':>8}")
#     for c in closed[-3:]:
#         ts, o, cl, h, l = c[0], c[1], c[2], c[3], c[4]
#         arrow = "▲" if cl >= o else "▼"
#         print(f"  {datetime.fromtimestamp(ts).strftime('%H:%M:%S'):<10} "
#               f"{o:>8.5f} {h:>8.5f} {l:>8.5f} {cl:>8.5f}  {arrow}")


# # ── Live multi-pair candle builder ────────────────────────────────────────────
# # One live candle per asset, updated from incoming ticks
# live_candles = {asset: None for asset in ASSETS}
# seen         = {asset: set() for asset in ASSETS}
# last_print   = 0

# print(f"\n{'='*72}")
# print(f"  LIVE MULTI-PAIR STREAM  ({STREAM_SECS}s)  —  {PERIOD}s candles")
# print(f"{'='*72}")
# print(f"  {'Asset':<16} {'Time':>8}  {'Open':>8} {'High':>8} {'Low':>8} {'Close':>8}  {'Last tick':>10}  Dir")
# print(f"  {'-'*70}")

# end = time.time() + STREAM_SECS

# while time.time() < end:
#     any_new = False

#     for asset in ASSETS:
#         pair_data = state.pairs.get(asset, {})
#         ticks     = pair_data.get("history", [])

#         for tick in ticks:
#             ts    = tick["time"]
#             price = tick["price"]
#             key   = (round(ts, 3), price)

#             if key in seen[asset]:
#                 continue
#             seen[asset].add(key)
#             any_new = True

#             # ── Update live candle ────────────────────────────────────────────
#             bucket = int(ts // PERIOD) * PERIOD

#             c = live_candles[asset]
#             if c is None or c["start"] != bucket:
#                 live_candles[asset] = {
#                     "start": bucket,
#                     "o": price, "h": price, "l": price, "c": price
#                 }
#             else:
#                 c["h"] = max(c["h"], price)
#                 c["l"] = min(c["l"], price)
#                 c["c"] = price

#     # ── Print dashboard every 1 second ───────────────────────────────────────
#     now = time.time()
#     if now - last_print >= 1.0:
#         last_print = now
#         # Move cursor up to overwrite previous dashboard lines
#         if any(live_candles[a] is not None for a in ASSETS):
#             print(f"\033[{len(ASSETS)+1}A", end="")  # move up N lines
#             print(f"  {'Asset':<16} {'Time':>8}  {'Open':>8} {'High':>8} {'Low':>8} {'Close':>8}  {'Price':>8}  Dir")
#             print(f"  {'-'*70}")
#             for asset in ASSETS:
#                 c = live_candles[asset]
#                 ticks = state.pairs.get(asset, {}).get("history", [])
#                 last_tick = ticks[-1]["price"] if ticks else None

#                 if c and last_tick:
#                     remaining = int(PERIOD - (time.time() % PERIOD))
#                     direction = "▲" if c["c"] >= c["o"] else "▼"
#                     candle_time = datetime.fromtimestamp(c["start"]).strftime("%H:%M:%S")
#                     print(f"  {asset:<16} {candle_time:>8}  "
#                           f"{c['o']:>8.5f} {c['h']:>8.5f} {c['l']:>8.5f} {c['c']:>8.5f}  "
#                           f"{last_tick:>8.5f}  {direction}  [{remaining}s]")
#                 else:
#                     print(f"  {asset:<16}  {'waiting...':>60}")

#     time.sleep(0.05)


# # ── Final summary ─────────────────────────────────────────────────────────────
# print(f"\n\n{'='*72}")
# print("FINAL CANDLE STATE")
# print(f"{'='*72}")
# for asset in ASSETS:
#     c = live_candles[asset]
#     ticks = state.pairs.get(asset, {}).get("history", [])
#     if c:
#         direction = "BULL ▲" if c["c"] >= c["o"] else "BEAR ▼"
#         change    = ((c["c"] - c["o"]) / c["o"]) * 100
#         print(f"  {asset:<16}  O:{c['o']:.5f}  H:{c['h']:.5f}  "
#               f"L:{c['l']:.5f}  C:{c['c']:.5f}  "
#               f"Δ{change:+.4f}%  {direction}  ({len(ticks)} ticks)")
#     else:
#         print(f"  {asset:<16}  no data")

# client.disconnect()
# print("\nDone.")



# """
# PyPocket — Multi-Pair Live Streaming (Windows-compatible)
# ==========================================================
# Streams ticks and builds live candles for multiple assets.
# Uses cls-style full redraw instead of ANSI cursor tricks.
# """

# import time
# import os
# from datetime import datetime
# import pocketoptionapi.state as state
# from pocketoptionapi.pocketapi import PocketOption

# # ── Config ────────────────────────────────────────────────────────────────────

# ASSETS = [
#     "EURUSD_otc",
#     "GBPUSD_otc",
#     "AUDJPY_otc",
#     "BTCUSD_otc",
#     "XAUUSD_otc",
# ]

# PERIOD      = 60   # candle period in seconds
# STREAM_SECS = 300  # how long to run (seconds)
# # ─────────────────────────────────────────────────────────────────────────────


# def clear():
#     os.system("cls" if os.name == "nt" else "clear")


# def wait_for(fn, timeout=15, poll=0.3, label=""):
#     start = time.time()
#     while time.time() - start < timeout:
#         if fn():
#             return True
#         time.sleep(poll)
#     print(f"  [TIMEOUT] {label}")
#     return False


# # ── Connect ───────────────────────────────────────────────────────────────────
# print("Connecting...")
# client = PocketOption(ssid=YOUR_SSID, demo=True)
# client.connect()

# wait_for(client.check_connect, timeout=15, label="websocket")
# wait_for(lambda: client.get_balance() is not None, timeout=10, label="balance")
# balance = client.get_balance()
# print(f"Connected! Balance: ${balance:,.2f}\n")

# # ── Subscribe to all pairs ────────────────────────────────────────────────────
# print("Subscribing to pairs...")
# for asset in ASSETS:
#     client.change_symbol(asset, PERIOD)
#     print(f"  + {asset}")
#     time.sleep(0.5)

# # print("\nWaiting for history data...")
# # wait_for(lambda: client.api.history_new is not None, timeout=15, label="history_new")
# # time.sleep(2)
# # print("Ready!\n")
# # time.sleep(1)

# # ── Live candle state per asset ───────────────────────────────────────────────
# live_candles = {asset: None for asset in ASSETS}
# seen         = {asset: set() for asset in ASSETS}
# tick_counts  = {asset: 0 for asset in ASSETS}

# end       = time.time() + STREAM_SECS
# last_draw = 0

# while time.time() < end:

#     # ── Ingest new ticks ─────────────────────────────────────────────────────
#     for asset in ASSETS:
#         ticks = state.pairs.get(asset, {}).get("history", [])
#         for tick in ticks:
#             ts    = tick["time"]
#             price = tick["price"]
#             key   = (round(ts, 3), price)
#             if key in seen[asset]:
#                 continue
#             seen[asset].add(key)
#             tick_counts[asset] += 1

#             bucket = int(ts // PERIOD) * PERIOD
#             c = live_candles[asset]
#             if c is None or c["start"] != bucket:
#                 live_candles[asset] = {
#                     "start": bucket,
#                     "o": price, "h": price, "l": price, "c": price,
#                 }
#             else:
#                 c["h"] = max(c["h"], price)
#                 c["l"] = min(c["l"], price)
#                 c["c"] = price

#     # ── Redraw dashboard every second ────────────────────────────────────────
#     now = time.time()
#     if now - last_draw >= 1.0:
#         last_draw = now
#         clear()

#         print(f"  PocketOption Live Dashboard   [{datetime.now().strftime('%H:%M:%S')}]")
#         print(f"  Balance: ${balance:,.2f}   Period: {PERIOD}s candles   Ends in: {int(end-now)}s")
#         print()
#         print(f"  {'Asset':<16} {'Open time':>9}  {'Open':>9} {'High':>9} {'Low':>9} {'Close':>9}  {'Chg%':>7}  {'Ticks':>6}  {'Left':>5}  Dir")
#         print(f"  {'─'*95}")

#         for asset in ASSETS:
#             c     = live_candles[asset]
#             ticks = state.pairs.get(asset, {}).get("history", [])

#             if c:
#                 candle_time = datetime.fromtimestamp(c["start"]).strftime("%H:%M:%S")
#                 change_pct  = ((c["c"] - c["o"]) / c["o"]) * 100 if c["o"] else 0
#                 direction   = "^" if c["c"] >= c["o"] else "v"
#                 remaining   = int(PERIOD - (now % PERIOD))
#                 tag         = "[+]" if c["c"] >= c["o"] else "[-]"

#                 print(f"  {tag} {asset:<14} {candle_time:>9}  "
#                       f"{c['o']:>9.5f} {c['h']:>9.5f} {c['l']:>9.5f} {c['c']:>9.5f}  "
#                       f"{change_pct:>+6.3f}%  "
#                       f"{tick_counts[asset]:>6}  "
#                       f"{remaining:>3}s   {direction}")
#             else:
#                 print(f"  [~] {asset:<14}  {'waiting...'}")

#         print(f"\n  {'─'*95}")
#         print(f"  Recent ticks:")
#         for asset in ASSETS:
#             ticks = state.pairs.get(asset, {}).get("history", [])
#             if ticks:
#                 last3  = ticks[-3:]
#                 prices = "  ->  ".join(f"{t['price']:.5f}" for t in last3)
#                 ts_str = datetime.fromtimestamp(last3[-1]["time"]).strftime("%H:%M:%S")
#                 print(f"    {asset:<16}  {ts_str}   {prices}")
#             else:
#                 print(f"    {asset:<16}  no ticks yet")

#     time.sleep(0.05)


# # ── Final summary ─────────────────────────────────────────────────────────────
# clear()
# print(f"\n{'='*65}")
# print("FINAL SUMMARY")
# print(f"{'='*65}")
# for asset in ASSETS:
#     c = live_candles[asset]
#     if c:
#         pct = ((c["c"] - c["o"]) / c["o"]) * 100
#         dir = "BULL ^" if c["c"] >= c["o"] else "BEAR v"
#         print(f"  {asset:<16}  O:{c['o']:.5f}  H:{c['h']:.5f}  "
#               f"L:{c['l']:.5f}  C:{c['c']:.5f}  "
#               f"{pct:>+.4f}%  {dir}  ({tick_counts[asset]} ticks)")
#     else:
#         print(f"  {asset:<16}  no data")

# client.disconnect()
# print("\nDone.")




"""
PyPocket — Multi-Pair Live Streaming (no redraw)
=================================================
Prints each new tick as it arrives, one line per tick.
"""

import time
import os
from datetime import datetime
import pocketoptionapi.state as state
from pocketoptionapi.pocketapi import PocketOption

# ── Config ────────────────────────────────────────────────────────────────────

ASSETS = [
    "EURUSD_otc",
    "GBPUSD_otc",
    "AUDJPY_otc",
    # "BTCUSD_otc",
    # "XAUUSD_otc",
]

PERIOD = 60  # candle size in seconds
# ─────────────────────────────────────────────────────────────────────────────

def wait_for(fn, timeout=15, poll=0.3, label=""):
    start = time.time()
    while time.time() - start < timeout:
        if fn():
            return True
        time.sleep(poll)
    print(f"  [TIMEOUT] {label}")
    return False

# Your SSID (replace with your own or use .env)
YOUR_SSID = os.getenv('POCKET_SSID', 'YOUR_SSID_HERE')

# ── Connect ───────────────────────────────────────────────────────────────────
print("Connecting...")
client = PocketOption(ssid=YOUR_SSID, demo=True)
client.connect()

wait_for(client.check_connect, timeout=15, label="websocket")
wait_for(lambda: client.get_balance() is not None, timeout=10, label="balance")
print(f"Connected! Balance: ${client.get_balance():,.2f}\n")

# ── Subscribe ─────────────────────────────────────────────────────────────────
print("Subscribing to pairs...")
for asset in ASSETS:
    client.change_symbol(asset, PERIOD)
    # client.api.subfor(asset)
    print(f"  + {asset}")
    time.sleep(0.5)

# wait_for(lambda: client.api.history_new is not None, timeout=15, label="history_new")
# time.sleep(2)

# # ── Candle state ──────────────────────────────────────────────────────────────
# live_candles = {a: None for a in ASSETS}
# seen         = {a: set() for a in ASSETS}

# print(f"\n{'Asset':<16}  {'Time':<14}  {'Price':>9}  {'O':>9} {'H':>9} {'L':>9} {'C':>9}  {'Chg%':>7}  Left")
# print("─" * 100)

# # ── Stream forever (Ctrl+C to stop) ──────────────────────────────────────────
# import time
# from datetime import datetime

# start_time = time.time()
# duration = 10  # seconds

try:
    # while time.time() - start_time < duration:
    #     for asset in ASSETS:
    #         ticks = state.pairs.get(asset, {}).get("history", [])
    #         for tick in ticks:
    #             ts    = tick["time"]
    #             price = tick["price"]
    #             key   = (round(ts, 3), price)
    #             if key in seen[asset]:
    #                 continue
    #             seen[asset].add(key)

    #             # Update candle
    #             bucket = int(ts // PERIOD) * PERIOD
    #             c = live_candles[asset]
    #             if c is None or c["start"] != bucket:
    #                 if c:
    #                     # Print candle close line
    #                     pct = ((c["c"] - c["o"]) / c["o"]) * 100
    #                     d   = "CLOSED ^" if c["c"] >= c["o"] else "CLOSED v"
    #                     t   = datetime.fromtimestamp(c["start"]).strftime("%H:%M:%S")
    #                     print(f"{'':─<16}  {t:<14}  {'':>9}  "
    #                           f"{c['o']:>9.5f} {c['h']:>9.5f} {c['l']:>9.5f} {c['c']:>9.5f}  "
    #                           f"{pct:>+6.3f}%  {d}")
                              
    #                 live_candles[asset] = {"start": bucket, "o": price, "h": price, "l": price, "c": price}
    #             else:
    #                 c["h"] = max(c["h"], price)
    #                 c["l"] = min(c["l"], price)
    #                 c["c"] = price

    #             # Print tick line
    #             c         = live_candles[asset]
    #             pct       = ((c["c"] - c["o"]) / c["o"]) * 100
    #             remaining = int(PERIOD - (ts % PERIOD))
    #             t         = datetime.fromtimestamp(ts).strftime("%H:%M:%S.%f")[:-4]
    #             print(f"{asset:<16}  {t:<14}  {price:>9.5f}  "
    #                   f"{c['o']:>9.5f} {c['h']:>9.5f} {c['l']:>9.5f} {c['c']:>9.5f}  "
    #                   f"{pct:>+6.3f}%  {remaining}s")
    # client.api.subfor(ASSETS[0])
    time.sleep(5)

    print(' f"{pct:>+6.3f}%  {remaining}s")')
    # print("unSubscribing to pairs...")
    # for asset in ASSETS:
    #     client.api.unsubfor(asset)
    #     print(f"  + {asset}")
    #     time.sleep(0.5)

    client.change_symbol('AS', '0')
    time.sleep(5)

except KeyboardInterrupt:
    print("\nStopped.")
    client.disconnect()
    print("Done.")