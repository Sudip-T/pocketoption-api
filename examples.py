"""
═══════════════════════════════════════════════════════════════════════════
POCKET OPTION API - COMPLETE EXAMPLES FOR VIEWERS
═══════════════════════════════════════════════════════════════════════════

This file contains ready-to-run examples for every major feature.
Each function is self-contained and shows exactly how to use that feature.

Author: Sudip
YouTube: @BytecodeAutomation
═══════════════════════════════════════════════════════════════════════════
"""

import time
import logging
import os
from datetime import datetime
from dotenv import load_dotenv

import pocketoptionapi.state as state
from pocketoptionapi.pocketapi import PocketOption
from pocketoptionapi.constants import REGION
from pocketoptionapi.expiration import get_expiration_time, get_remaning_time

# Load environment variables
load_dotenv()

# Configure logging for clean output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger("PocketOptionExample")

# Your SSID (replace with your own or use .env)
YOUR_SSID = os.getenv('POCKET_SSID', 'YOUR_SSID_HERE')

# Create client (demo account by default)
client = PocketOption(ssid=YOUR_SSID, demo=True)

# Connect to Pocket Option
client.connect()
time.sleep(5)

# ═══════════════════════════════════════════════════════════════════════
# 1. BASIC CONNECTION & ACCOUNT
# ═══════════════════════════════════════════════════════════════════════

def example_connect_and_get_balance():
    """
    EP#01: Connect to Pocket Option and get account balance.
    The foundation for everything else.
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: GET BALANCE")
    print("="*60)

    # Check connection
    if client.check_connect():
        print("✅ Connection status: Connected")
    else:
        print("❌ Connection failed")
        return

    # Get account balance
    balance = client.get_balance()
    print(f"💰 Current balance: ${balance:.2f}")
    
    return client


def example_server_time():
    """
    EP#01: Get server time (important for syncing trades).
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: SERVER TIME")
    print("="*60)
    
    # Get server timestamp
    timestamp = client.get_server_timestamp()
    print(f"🕐 Server timestamp: {timestamp}")
    
    # Get formatted datetime
    dt = client.get_server_datetime()
    print(f"📅 Server datetime: {dt}")
    
    # Get synced datetime
    synced = client.sync_datetime()
    print(f"🔄 Synced datetime: {synced}")


def example_get_regions():
    """
    EP#01: Show available server regions.
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: SERVER REGIONS")
    print("="*60)
    
    region = REGION()
    
    # Show all regions
    print("🌍 Available regions:")
    for region_name, region_url in region.REGIONS.items():
        print(f"   {region_name}: {region_url}")
    
    # Get demo servers
    demo_urls = region.get_regions(demo=True)
    print(f"\n🎮 Demo servers: {demo_urls}")
    
    # Get live servers
    live_urls = region.get_regions(demo=False)
    print(f"💰 Live servers: {live_urls}")


# ═══════════════════════════════════════════════════════════════════════
# 2. ASSET MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════

def example_get_assets():
    """
    Alternative: Get assets directly from websocket (requires active connection).
    """
    print("\n" + "="*60)
    print("EXAMPLE 4b: GET ASSETS FROM WEBSOCKET (Direct)")
    print("="*60)
    
    # If you have the raw payout data in state
    if hasattr(state, 'PayoutData') and state.PayoutData:
        import json
        
        try:
            # Parse the raw data
            raw_data = state.PayoutData
            if isinstance(raw_data, str):
                assets_list = json.loads(raw_data)
            else:
                assets_list = raw_data
            
            print(f"✅ Retrieved {len(assets_list)} assets from websocket")
            
            # Process and display
            asset_types = {}
            for asset in assets_list:
                if len(asset) > 3:
                    asset_type = asset[3]
                    asset_types[asset_type] = asset_types.get(asset_type, 0) + 1
            
            print("\n📊 Asset breakdown:")
            for atype, count in sorted(asset_types.items()):
                print(f"   {atype}: {count} assets")
            
            # Show first 10
            print("\n📈 First 10 assets:")
            for asset in assets_list[:10]:
                if len(asset) > 2:
                    print(f"   {asset[1]} - {asset[2]}")
                    
        except Exception as e:
            print(f"❌ Error parsing data: {e}")
    else:
        print("❌ No websocket data available. Make sure you're connected.")
        print("   Run example 1 (Connect & Get Balance) first.")


def example_save_assets_to_file():
    """
    Manually save assets from websocket to file.
    """
    print("\n" + "="*60)
    print("EXAMPLE 4c: SAVE ASSETS TO FILE MANUALLY")
    print("="*60)
    
    if hasattr(state, 'PayoutData') and state.PayoutData:
        import json
        import pickle
        import os
        
        # Create directory
        data_dir = "active_data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        try:
            # Parse data
            raw_data = state.PayoutData
            if isinstance(raw_data, str):
                assets_list = json.loads(raw_data)
            else:
                assets_list = raw_data
            
            # Convert to dictionary format
            actives = {}
            for asset in assets_list:
                if len(asset) >= 4:
                    symbol = asset[1]
                    actives[symbol] = {
                        'id': asset[0],
                        'symbol': symbol,
                        'name': asset[2],
                        'type': asset[3],
                        # 'raw_data': asset
                    }
                    # Add more fields if available
                    if len(asset) > 4:
                        actives[symbol]['field4'] = asset[4]
                    if len(asset) > 5:
                        actives[symbol]['field5'] = asset[5]
                    if len(asset) > 10:
                        actives[symbol]['pair_id'] = asset[10]
                    if len(asset) > 14:
                        actives[symbol]['is_otc'] = asset[14]
            
            # Save as JSON
            json_path = os.path.join(data_dir, "actives.json")
            with open(json_path, 'w') as f:
                json.dump(actives, f, indent=2)
            print(f"✅ Saved {len(actives)} assets to {json_path}")
            
            # Save as pickle
            pkl_path = os.path.join(data_dir, "actives.pkl")
            with open(pkl_path, 'wb') as f:
                pickle.dump(actives, f)
            print(f"✅ Saved {len(actives)} assets to {pkl_path}")
            
            # Also save a readable text version
            txt_path = os.path.join(data_dir, "actives.txt")
            with open(txt_path, 'w') as f:
                f.write(f"Total Assets: {len(actives)}\n")
                f.write("="*60 + "\n\n")
                for symbol, data in list(actives.items())[:50]:  # First 50
                    f.write(f"Symbol: {symbol}\n")
                    f.write(f"  Name: {data['name']}\n")
                    f.write(f"  Type: {data['type']}\n")
                    f.write(f"  ID: {data['id']}\n")
                    if data.get('is_otc') is not None:
                        f.write(f"  OTC: {data['is_otc']}\n")
                    f.write("-"*40 + "\n")
            print(f"✅ Saved readable version to {txt_path}")
            
            # Store in state for runtime access
            state.actives = actives
            
        except Exception as e:
            print(f"❌ Error saving assets: {e}")
    else:
        print("❌ No websocket data available. Please:")
        print("   1. Run example 1 (Connect & Get Balance)")
        print("   2. Wait for websocket to receive asset data")
        print("   3. Then run this example")

def example_get_payout():
    """
    EP#02: Get payout percentage for specific assets.
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: GET PAYOUT PERCENTAGES")
    print("="*60)
    
    # Test various assets
    test_assets = ["EURUSD_otc", "BTCUSD_otc", "XAUUSD_otc", "#AAPL"]
    
    for asset in test_assets:
        payout = client.GetPayout(asset)
        if payout:
            print(f"💰 {asset}: {payout}% payout")
        else:
            print(f"❌ {asset}: Could not get payout")


def example_change_symbol():
    """
    EP#02: Change active symbol and timeframe.
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: CHANGE SYMBOL")
    print("="*60)
    
    # Change to EURUSD with 60-second candles
    print("🔄 Changing to EURUSD_otc with 60s candles...")
    client.change_symbol("EURUSD_otc", 60)
    print("✅ Symbol changed")
    
    time.sleep(1)
    
    # Change to Bitcoin with 60-second candles
    print("🔄 Changing to BTCUSD_otc with 60s candles...")
    client.change_symbol("BTCUSD_otc", 60)
    print("✅ Symbol changed")


# ═══════════════════════════════════════════════════════════════════════
# 3. CANDLE DATA
# ═══════════════════════════════════════════════════════════════════════

def example_get_historical_candles():
    """
    EP#03: Get historical candlestick data.
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: GET HISTORICAL CANDLES")
    print("="*60)
    
    asset = "EURUSD_otc"
    period = 60  # 1-minute candles
    
    print(f"📊 Fetching {asset} {period}s candles...")
    
    # Get candles
    success = client.get_candles(asset, period=period, count_request=3)
    
    if success:
        # Access the stored dataframe
        if asset in state.pairs:
            df = state.pairs[asset].get('dataframe')
            if df is not None and not df.empty:
                print(f"✅ Retrieved {len(df)} candles")
                print("\nLast 5 candles:")
                print("-" * 70)
                print(df.tail())
            else:
                print("⚠️ Dataframe is empty")
        else:
            print("⚠️ No data found for asset")
    else:
        print("❌ Failed to get candles")


def example_get_current_price():
    """
    EP#03: Get current price from real-time data.
    """
    print("\n" + "="*60)
    print("EXAMPLE 8: GET CURRENT PRICE")
    print("="*60)
    
    asset = "EURUSD_otc"
    
    # First subscribe to get price updates
    client.change_symbol(asset, 60)
    time.sleep(2)
    
    # Get current price from state
    if asset in state.pairs and 'history' in state.pairs[asset]:
        history = state.pairs[asset]['history']
        if history:
            latest = history[-1]
            print(f"💰 {asset} current price: {latest['price']:.5f}")
            print(f"🕐 Last update: {datetime.fromtimestamp(latest['time'])}")
        else:
            print("⚠️ No price data available")
    else:
        print("⚠️ Not subscribed to asset")


def example_get_history_data():
    """
    EP#03: Get raw history/tick data.
    """
    print("\n" + "="*60)
    print("EXAMPLE 9: GET HISTORY DATA")
    print("="*60)
    
    asset = "EURUSD_otc"
    period = 60
    
    print(f"📊 Fetching history for {asset}...")
    success = client.get_history(asset, period=period, count_request=1)
    
    if success:
        if asset in state.pairs and 'history' in state.pairs[asset]:
            history = state.pairs[asset]['history']
            print(f"✅ Retrieved {len(history)} ticks")
            
            # Show last 5 ticks
            print("\nLast 5 ticks:")
            for tick in history[-5:]:
                print(f"   Time: {datetime.fromtimestamp(tick['time'])} | Price: {tick['price']:.5f}")
        else:
            print("⚠️ No history data found")
    else:
        print("❌ Failed to get history")


# ═══════════════════════════════════════════════════════════════════════
# 4. TRADING
# ═══════════════════════════════════════════════════════════════════════

def example_expiration_times():
    """
    EP#04: Calculate expiration times for trades.
    """
    print("\n" + "="*60)
    print("EXAMPLE 10: EXPIRATION TIMES")
    print("="*60)
    
    now = time.time()
    print(f"🕐 Current time: {datetime.fromtimestamp(now)}")
    
    # Get expiration for different durations
    for duration in [1, 2, 5, 15]:
        expiry = get_expiration_time(now, duration=duration)
        remaining = expiry - now
        print(f"   {duration:>3}min expiry: {datetime.fromtimestamp(expiry)} ({remaining:.0f}s remaining)")
    
    # Get all available windows
    windows = get_remaning_time(now)
    print("\n📊 Available expiry windows:")
    for duration, remaining in windows[:10]:  # Show first 10
        print(f"   {duration:>3} minutes — {remaining}s remaining")


def example_place_trade():
    """
    EP#04: Place a binary options trade.
    """
    print("\n" + "="*60)
    print("EXAMPLE 11: PLACE BINARY OPTIONS TRADE")
    print("="*60)
    
    # Get balance before trade
    balance_before = client.get_balance()
    print(f"💰 Balance before: ${balance_before:.2f}")
    
    # Place a CALL trade (predict price will go UP)
    amount = 1  # $1 (minimum for demo)
    asset = "EURUSD_otc"
    action = "call"  # "call" for up, "put" for down
    expiration = 5  # 5 seconds
    
    print(f"\n📈 Placing {action.upper()} trade on {asset} (${amount})...")
    success, order_id = client.buy(
        amount=amount,
        active=asset,
        action=action,
        expirations=expiration
    )
    
    if success:
        print(f"✅ Trade placed! Order ID: {order_id}")
        
        # Wait for result
        print(f"⏳ Waiting {expiration} seconds for trade result...")
        profit, status = client.check_win(order_id)
        
        balance_after = client.get_balance()
        print(f"\n📊 TRADE RESULT:")
        print(f"   Status: {status.upper()}")
        print(f"   Profit: ${profit:+.2f}")
        print(f"   Balance after: ${balance_after:.2f}")
        print(f"   Balance change: ${balance_after - balance_before:+.2f}")
    else:
        print(f"❌ Trade failed: {order_id}")


def example_place_multiple_trades():
    """
    EP#04: Place multiple trades in sequence.
    """
    print("\n" + "="*60)
    print("EXAMPLE 12: PLACE MULTIPLE TRADES")
    print("="*60)
    
    trades = [
        {"asset": "EURUSD_otc", "action": "call", "amount": 1},
        {"asset": "BTCUSD_otc", "action": "put", "amount": 1},
        {"asset": "XAUUSD_otc", "action": "call", "amount": 1},
    ]
    
    order_ids = []
    balance_before = client.get_balance()
    
    print(f"💰 Starting balance: ${balance_before:.2f}\n")
    
    for i, trade in enumerate(trades, 1):
        print(f"Trade {i}: {trade['action'].upper()} on {trade['asset']} (${trade['amount']})")
        success, order_id = client.buy(
            amount=trade['amount'],
            active=trade['asset'],
            action=trade['action'],
            expirations=5
        )
        
        if success:
            print(f"   ✅ Order ID: {order_id}")
            order_ids.append(order_id)
        else:
            print(f"   ❌ Failed: {order_id}")
        
        time.sleep(2)  # Small delay between trades
    
    print(f"\n📊 Waiting for {len(order_ids)} trades to complete...")
    time.sleep(5)
    
    # Check results
    total_profit = 0
    for order_id in order_ids:
        profit, status = client.check_win(order_id)
        total_profit += profit
        print(f"   Order {order_id}: {status.upper()} | Profit: ${profit:+.2f}")
    
    balance_after = client.get_balance()
    print(f"\n💰 Final balance: ${balance_after:.2f}")
    print(f"📈 Total P&L: ${total_profit:+.2f}")


# ═══════════════════════════════════════════════════════════════════════
# 5. POSITION MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════

def example_get_open_orders():
    """
    EP#05: Get currently open orders.
    """
    print("\n" + "="*60)
    print("EXAMPLE 13: GET OPEN ORDERS")
    print("="*60)
    
    open_orders = client.check_open()
    
    if open_orders:
        print(f"📋 Found {len(open_orders)} open orders:")
        for order in open_orders:
            print(f"   Order ID: {order.get('id', 'N/A')} | Asset: {order.get('asset', 'N/A')}")
    else:
        print("📋 No open orders")


def example_get_closed_deals():
    """
    EP#05: Get closed deals history.
    """
    print("\n" + "="*60)
    print("EXAMPLE 14: GET CLOSED DEALS")
    print("="*60)
    
    deals = client.get_deals()
    
    if deals:
        print(f"📜 Found {len(deals)} closed deals")
        print("\nLast 5 deals:")
        print("-" * 80)
        print(deals)
        for deal in deals[:5]:

            print(f"   ID: {deal.get('id', 'N/A')} | Profit: ${deal.get('profit', 0):+.2f}")
    else:
        print("📜 No closed deals found")


def example_trade_outcome():
    """
    EP#05: Check outcome of a specific trade.
    """
    print("\n" + "="*60)
    print("EXAMPLE 15: CHECK TRADE OUTCOME")
    print("="*60)
    
    # First place a trade
    print("Placing a test trade...")
    success, order_id = client.buy(
        amount=1,
        active="EURUSD_otc",
        action="call",
        expirations=5
    )
    
    if success:
        print(f"✅ Trade placed: {order_id}")
        print("⏳ Waiting for result...")
        time.sleep(5)
        
        # Check outcome
        profit, status = client.check_win(order_id)
        print(f"\n📊 Trade {order_id}:")
        print(f"   Status: {status.upper()}")
        print(f"   Profit: ${profit:+.2f}")
    else:
        print("❌ Failed to place trade")


# ═══════════════════════════════════════════════════════════════════════
# 6. ADVANCED: SIMPLE TRADING BOT
# ═══════════════════════════════════════════════════════════════════════

def example_simple_trading_bot():
    """
    EP#06: Simple trading bot using candle direction.
    """
    print("\n" + "="*60)
    print("EXAMPLE 16: SIMPLE TRADING BOT")
    print("="*60)
    
    print(f"💰 Starting balance: ${client.get_balance():.2f}")
    print("🤖 Bot will trade based on candle direction\n")
    
    asset = "EURUSD_otc"
    period = 5
    
    # Subscribe to asset
    client.change_symbol(asset, period)
    time.sleep(2)
    
    trades_placed = 0
    max_trades = 3
    
    for trade_num in range(max_trades):
        print(f"\n--- Trade {trade_num + 1}/{max_trades} ---")
        
        # Get current price direction
        if asset in state.pairs and 'history' in state.pairs[asset]:
            history = state.pairs[asset]['history']
            if len(history) >= 2:
                current_price = history[-1]['price']
                previous_price = history[-2]['price']
                
                if current_price > previous_price:
                    action = "call"
                    direction = "UP 📈"
                else:
                    action = "put"
                    direction = "DOWN 📉"
                
                print(f"Current: {current_price:.5f} | Previous: {previous_price:.5f}")
                print(f"Direction: {direction}")
                
                # Place trade
                success, order_id = client.buy(
                    amount=1,
                    active=asset,
                    action=action,
                    expirations=5
                )
                
                if success:
                    trades_placed += 1
                    print(f"✅ Trade placed! Order ID: {order_id}")
                else:
                    print(f"❌ Trade failed: {order_id}")
            else:
                print("⚠️ Not enough history data")
        else:
            print("⚠️ No price data available")
        
        # Wait for next candle
        if trade_num < max_trades - 1:
            print("⏳ Waiting 5 seconds for next candle...")
            time.sleep(5)
    
    print(f"\n📊 Trading complete!")
    print(f"💰 Final balance: ${client.get_balance():.2f}")


# ═══════════════════════════════════════════════════════════════════════
# MENU SYSTEM FOR VIEWERS
# ═══════════════════════════════════════════════════════════════════════

def show_menu():
    """Interactive menu for viewers to choose examples."""
    print("\n" + "="*60)
    print("📚 POCKET OPTION API - EXAMPLE MENU")
    print("="*60)
    print("""
    1  - Connect & Get Balance
    2  - Server Time
    3  - Server Regions
    4  - Get Available Assets
    41  - Save Available Assets
    5  - Get Payout Percentages
    6  - Change Symbol
    7  - Get Historical Candles
    8  - Get Current Price
    9  - Get History Data
    10 - Expiration Times
    11 - Place Binary Trade
    12 - Place Multiple Trades
    13 - Get Open Orders
    14 - Get Closed Deals
    15 - Check Trade Outcome
    16 - Simple Trading Bot
    0  - Exit
    """)
    
    examples_map = {
        1: example_connect_and_get_balance,
        2: example_server_time,
        3: example_get_regions,
        4: example_get_assets,
        41:example_save_assets_to_file,
        5: example_get_payout,
        6: example_change_symbol,
        7: example_get_historical_candles,
        8: example_get_current_price,
        9: example_get_history_data,
        10: example_expiration_times,
        11: example_place_trade,
        12: example_place_multiple_trades,
        13: example_get_open_orders,
        14: example_get_closed_deals,
        15: example_trade_outcome,
        16: example_simple_trading_bot,
    }
    
    while True:
        try:
            choice = int(input("\n👉 Enter your choice: "))
            
            if choice == 0:
                print("👋 Goodbye! Happy trading!")
                break
            
            if choice in examples_map:
                examples_map[choice]()
            else:
                print("❌ Invalid choice. Please try again.")
                
        except ValueError:
            print("❌ Please enter a number.")
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
    
    # Disconnect when done
    client.disconnect()
    print("🔌 Disconnected")


# ═══════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║     POCKET OPTION API - COMPLETE EXAMPLES                      ║
    ║     YouTube: @BytecodeAutomation                               ║
    ║                                                                ║
    ║     ⚠️  IMPORTANT: Update YOUR_SSID variable or                ║
    ║        set POCKET_SSID in .env file before running!            ║
    ╚════════════════════════════════════════════════════════════════╝
    """)

    # Show interactive menu
    show_menu()