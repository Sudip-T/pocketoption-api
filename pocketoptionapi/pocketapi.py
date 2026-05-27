import asyncio, threading, sys, json, time, operator
from datetime import datetime
from tzlocal import get_localzone
from pocketoptionapi.api import PocketOptionAPI
import pocketoptionapi.constants as OP_code
import pocketoptionapi.state as state
from collections import defaultdict
from collections import deque
import pandas as pd

local_zone_name = get_localzone()

# logger = logging.getLogger(__name__)

def get_balance():
    return state.balance

class PocketOption:
    __version__ = "1.0.0"

    def __init__(self, ssid, demo):
        self.size = [1, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800,
                     3600, 7200, 14400, 28800, 43200, 86400, 604800, 2592000]
        state.SSID = ssid
        state.DEMO = demo
        state.logger("Modo Demo: %s" % str(demo), "INFO")
        self.suspend = 0.5
        self.thread = None
        self.subscribe_candle = []
        self.subscribe_candle_all_size = []
        self.subscribe_mood = []
        self.get_realtime_strike_list_temp_data = {}
        self.get_realtime_strike_list_temp_expiration = 0
        self.SESSION_HEADER = {
            "User-Agent": r"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          r"Chrome/66.0.3359.139 Safari/537.36"}
        self.SESSION_COOKIE = {}
        self.api = PocketOptionAPI()
        self.loop = asyncio.get_event_loop()

    def get_server_timestamp(self):
        return self.api.time_sync.server_timestamp
        
    def Stop(self):
        sys.exit()

    def get_server_datetime(self):
        return self.api.time_sync.server_datetime

    def set_session(self, header, cookie):
        self.SESSION_HEADER = header
        self.SESSION_COOKIE = cookie

    def get_async_order(self, buy_order_id=None):
        if buy_order_id:
            if self.api.order_async["deals"][0]["id"] == buy_order_id:
                return self.api.order_async["deals"][0]
            else:
                return None
        else:
            return self.api.order_async

    def get_async_order_id(self, buy_order_id):
        return self.api.order_async["deals"][0][buy_order_id]

    def start_async(self):
        asyncio.run(self.api.connect())
        
    def disconnect(self):
        try:
            if state.websocket_is_connected:
                asyncio.run(self.api.close())
                state.websocket_is_connected = False
                # logger.debug("WebSocket connection closed successfully.")
                state.logger("WebSocket connection closed successfully.", "DEBUG")
            else:
                # logger.debug("WebSocket was not connected.")
                state.logger("WebSocket was not connected.", "DEBUG")

            if self.loop is not None:
                for task in asyncio.all_tasks(self.loop):
                    task.cancel()

                if not self.loop.is_closed():
                    self.loop.stop()
                    self.loop.close()
                    # logger.debug("Event loop stopped and closed successfully.")
                    state.logger("Event loop stopped and closed successfully.", "DEBUG")

            if self.api.websocket_thread is not None and self.api.websocket_thread.is_alive():
                self.api.websocket_thread.join()
                # logger.debug("WebSocket thread closed successfully.")
                state.logger("WebSocket thread closed successfully.", "DEBUG")

        except Exception as e:
            # logging.error(f"Error during disconnection: {e}")
            state.logger("Error during disconnection: %s" % str(e), "ERROR")

    def connect(self):
        try:
            websocket_thread = threading.Thread(target=self.api.connect, daemon=True)
            websocket_thread.start()

        except Exception as e:
            # logging.error(f"Error connecting: {e}")
            state.logger("Error connecting: %s" % str(e), "ERROR")
            return False
        return True
    
    def GetPayout(self, pair):
        try:
            data = self.api.GetPayoutData()
            data = json.loads(data)
            data2 = None
            for i in data:
                if i[1] == pair:
                    data2 = i
            return data2[5]
        except:
            return None

    @staticmethod
    def check_connect():
        if state.websocket_is_connected == 0:
            return False
        elif state.websocket_is_connected is None:
            return False
        else:
            return True

    @staticmethod
    def get_balance():
        if state.balance_updated:
            return state.balance
        else:
            return None
            
    @staticmethod
    def check_open():
        return state.order_open
        
    @staticmethod
    def check_order_closed(ido):
        while ido not in state.order_closed:
            time.sleep(0.1)

        for pack in state.stat:
            if pack[0] == ido:
               # logger.debug('Closed Order',pack[1])
               state.logger("Closed Order %s" % str(pack[1]), "DEBUG")

        return pack[0]
    
    def buy(self, amount, active, action, expirations):
        self.api.buy_multi_option = {}
        self.api.buy_successful = None
        req_id = "buy"

        try:
            if req_id not in self.api.buy_multi_option:
                self.api.buy_multi_option[req_id] = {"id": None}
            else:
                self.api.buy_multi_option[req_id]["id"] = None
        except Exception as e:
            state.logger("Error initializing buy_multi_option: %s" % str(e), "ERROR")
            return False, None

        state.order_data = None
        state.result = None

        self.api.buyv3(amount, active, action, expirations, req_id)

        start_t = time.time()
        while True:
            if state.result is not None and state.order_data is not None:
                break
            if time.time() - start_t >= 5:
                if isinstance(state.order_data, dict) and "error" in state.order_data:
                    state.logger(str(state.order_data["error"]), "ERROR")
                else:
                    state.logger("Unknown error occurred during purchase operation", "ERROR")
                return False, None
            time.sleep(0.1)

        return state.result, state.order_data.get("id", None)

    def check_win(self, id_number=None):
        if not id_number:
            order_info = self.get_async_order()
            return order_info
        start_t = time.time()
        order_info = None

        while True:
            try:
                order_info = self.get_async_order(id_number)
                if order_info and "id" in order_info and order_info["id"] is not None:
                    break
            except:
                pass

            if time.time() - start_t >= 180:
                # logger.error("Timeout: Unable to retrieve order information in time.")
                state.logger("Timeout: Unable to retrieve order information in time.", "ERROR")
                return None, "unknown"

            time.sleep(0.1)

        if order_info and "profit" in order_info:
            status = "win" if order_info["profit"] > 0 else "loose"
            return order_info["profit"], status
        else:
            # logger.error("Invalid order information retrieved.")
            state.logger("Invalid order information retrieved.", "ERROR")
            return None, "unknown"

    @staticmethod
    def last_time(timestamp, period):
        timestamp_arredondado = (timestamp // period) * period
        return int(timestamp_arredondado)

    def get_payout(self):
        return self.api.GetPayoutData()

    def get_deals(self):
        return self.api.GetClosedDeals()

    @staticmethod
    def process_data_history(data, period):
        df = pd.DataFrame(data['history'], columns=['timestamp', 'price'])
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')
        df['minute_rounded'] = df['datetime'].dt.floor(f'{period / 60}min')

        ohlcv = df.groupby('minute_rounded').agg(
            open=('price', 'first'),
            high=('price', 'max'),
            low=('price', 'min'),
            close=('price', 'last')
        ).reset_index()

        ohlcv['time'] = ohlcv['minute_rounded'].apply(lambda x: int(x.timestamp()))
        ohlcv = ohlcv.drop(columns='minute_rounded')

        ohlcv = ohlcv.iloc[:-1]

        ohlcv_dict = ohlcv.to_dict(orient='records')

        return ohlcv_dict

    @staticmethod
    def process_candle(candle_data, period):
        data_df = pd.DataFrame(candle_data)
        data_df.sort_values(by='time', ascending=True, inplace=True)
        data_df.drop_duplicates(subset='time', keep="first", inplace=True)
        data_df.reset_index(drop=True, inplace=True)
        data_df.ffill(inplace=True)

        diferencas = data_df['time'].diff()
        diff = (diferencas[1:] == period).all()
        return data_df, diff

    def change_symbol(self, active, period):
        return self.api.change_symbol(active, period)

    def sync_datetime(self):
        return self.api.synced_datetime

    def get_history(self, active, period, start_time=None, end_time=None, count_request=1):
        try:
            if start_time is None:
                time_sync = self.get_server_timestamp()
                time_red = self.last_time(time_sync, period)
            else:
                time_red = start_time
                time_sync = self.get_server_timestamp()

            all_candles = []

            time_red = int(datetime.now().timestamp())
            while True:
                try:
                    self.api.history_data = None
                    self.api.getcandles(active, period, time_red)

                    for i in range(1, 100):
                        if self.api.history_data is None:
                            time.sleep(0.1)
                        elif self.api.history_data is not None or i == 99:
                            break

                    if self.api.history_data is not None:
                        all_candles.extend(self.api.history_data)
                        if end_time is None:
                            break
                        else:
                            self.api.history_data = sorted(self.api.history_data, key=lambda x: x["time"])
                            _ = int(self.api.history_data[len(self.api.history_data)-1]["time"]) - int(self.api.history_data[0]["time"])
                            time_red = time_red - _
                            if time_red < end_time:
                                break
                except Exception as e:
                    state.logger(str(e), "ERROR")
            all_candles = sorted(all_candles, key=lambda x: x["time"])
            state.set_cache(state.pairs[active]["id"], all_candles)
            return True

            if len(his['candles']) > 0:
                for can in his['candles']:
                    c = {'time': can[0], 'open': can[1], 'high': can[3], 'low': can[4], 'close': can[2]}
                    c0.append(c)
                c0 = sorted(c0, key=lambda x: x["time"])
            for hist in his['history']:
                h = {'time': hist[0], 'price': hist[1]}
                c1.append(h)
            c1 = sorted(c1, key=lambda x: x["time"])
            if active in state.pairs:
                state.pairs[active]['history'] = c1
                if len(c0) > 0:
                    df = pd.DataFrame(c0)
                    df = df.sort_values(by='time').reset_index(drop=True)
                    df['time'] = pd.to_datetime(df['time'], unit='s')
                    df.set_index('time', inplace=True)
                    df.reset_index(inplace=True)
                    state.pairs[active]['dataframe'] = df

        except:
            state.logger("except get_candles", "DEBUG")
            return False

    def get_candles(self, active, period, start_time=None, count=6000, count_request=3):
        try:
            if start_time is None:
                time_sync = self.get_server_timestamp()
                time_red = self.last_time(time_sync, period)
            else:
                time_red = start_time
                time_sync = self.get_server_timestamp()

            all_candles = []

            self.api.history_new = None

            i = 0
            while True:
                i += 1
                try:
                    self.api.change_symbol(active, period)

                    for i in range(1, 100):
                        if self.api.history_new is None:
                            time.sleep(0.1)
                        elif self.api.history_new is not None or i == 99:
                            break

                    if self.api.history_new is not None:
                        his = self.api.history_new
                        break

                except Exception as e:
                    # logging.error(e)
                    state.logger(str(e), "ERROR")
            c0, c1 = [], []
            if period < 60 or count_request > 1:
                time_red = int(datetime.now().timestamp())
                x = 0
                while True:
                    x += 1
                    try:
                        self.api.history_data = None
                        self.api.getcandles(active, period, time_red)

                        for i in range(1, 100):
                            if self.api.history_data is None:
                                time.sleep(0.1)
                            elif self.api.history_data is not None or i == 99:
                                break

                        if self.api.history_data is not None:
                            c1.extend(self.api.history_data)
                            if x == count_request:
                                break
                            else:
                                self.api.history_data = sorted(self.api.history_data, key=lambda x: x["time"])
                                _ = int(self.api.history_data[len(self.api.history_data)-1]["time"]) - int(self.api.history_data[0]["time"])
                                time_red = time_red - _

                    except Exception as e:
                        # logger.error(e)
                        state.logger(str(e), "ERROR")
            if len(his['candles']) > 0:
                for can in his['candles']:
                    c = {'time': can[0], 'open': can[1], 'high': can[3], 'low': can[4], 'close': can[2]}
                    c0.append(c)
            c0 = sorted(c0, key=lambda x: x["time"])
            for hist in his['history']:
                h = {'time': hist[0], 'price': hist[1]}
                c1.append(h)
            c1 = sorted(c1, key=lambda x: x["time"])
            if active in state.pairs:
                state.pairs[active]['history'] = c1
                if len(c0) > 0:
                    df = pd.DataFrame(c0)
                    df = df.sort_values(by='time').reset_index(drop=True)
                    df['time'] = pd.to_datetime(df['time'], unit='s')
                    df.set_index('time', inplace=True)
                    df.reset_index(inplace=True)
                    state.pairs[active]['dataframe'] = df
            return True

        except:
            state.logger("except get_candles", "DEBUG")
            return False
