# import asyncio, websockets, json, ssl
# from datetime import datetime, timedelta, timezone

# import pocketoptionapi.constants as OP_code
# import pocketoptionapi.state as state
# from pocketoptionapi.constants import REGION
# from pocketoptionapi.ws.objects.timesync import TimeSync
# from pocketoptionapi.ws.objects.time_sync import TimeSynchronizer

# # logger = logging.getLogger(__name__)

# timesync = TimeSync()
# sync = TimeSynchronizer()


# async def on_open():
#     state.logger("CONNECTED SUCCESSFUL", "INFO")
#     state.logger("Websocket client connected.", "DEBUG")
#     state.websocket_is_connected = True


# async def send_ping(ws):
#     while state.websocket_is_connected is False:
#         await asyncio.sleep(0.1)
#     pass
#     while True:
#         await asyncio.sleep(20)
#         await ws.send('42["ps"]')


# async def process_message(message):
#     try:
#         data = json.loads(message)
#         print(data)
#         state.logger("Received message: %s" % str(data), "DEBUG")

#         if isinstance(data, dict) and 'uid' in data:
#             uid = data['uid']
#             state.logger("UID: %s" % str(uid), "DEBUG")
#         elif isinstance(data, list) and len(data) > 0:
#             event_type = data[0]
#             event_data = data[1]
#             state.logger("Event type: %s, Event data: %s" %(str(event_type), str(event_data)), "DEBUG")

#     except json.JSONDecodeError as e:
#         state.logger("JSON decode error: %s" % str(e), "ERROR")
#     except KeyError as e:
#         state.logger("Key error: %s" % str(e), "ERROR")
#     except Exception as e:
#         state.logger("Error processing message: %s" % str(e), "ERROR")


# class WebsocketClient(object):
#     def __init__(self, api) -> None:
#         self.updateHistoryNew = None
#         self.updateStream = None
#         self.loadHistoryPeriod = None
#         self.updateClosedDeals = False
#         self.successcloseOrder = False
#         self.updateStream = False
#         self.api = api
#         self.message = None
#         self.url = None
#         self.ssid = state.SSID
#         self.websocket = None
#         self.region = REGION()
#         self.loop = asyncio.get_event_loop()

#     async def websocket_listener(self, ws):
#         try:
#             async for message in ws:
#                 await self.on_message(message)
#         except Exception as e:
#             # logger.warning(f"Error occurred: {e}")
#             state.logger("Error occurred: %s" % str(e), "WARNING")

#     async def connect(self):
#         ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
#         ssl_context.check_hostname = False
#         ssl_context.verify_mode = ssl.CERT_NONE

#         try:
#             await self.api.close()
#         except:
#             pass

#         while not state.websocket_is_connected:
#             for url in self.region.get_regions(state.DEMO):
#                 state.logger(str(url), "INFO")
#                 try:
#                     async with websockets.connect(
#                             url,
#                             ssl=ssl_context,
#                             additional_headers={
#                                 "Origin": "https://pocketoption.com",
#                                 "Cache-Control": "no-cache",
#                                 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
#                             }
#                     ) as ws:
#                         self.websocket = ws
#                         self.url = url
#                         state.websocket_is_connected = True

#                         # Create and run tasks
#                         on_message_task = asyncio.create_task(self.websocket_listener(ws))
#                         sender_task = asyncio.create_task(self.send_message(self.message))
#                         ping_task = asyncio.create_task(send_ping(ws))

#                         await asyncio.gather(on_message_task, sender_task, ping_task)

#                 except websockets.ConnectionClosed as e:
#                     state.websocket_is_connected = False
#                     await self.on_close(e)
#                     # logger.warning("Trying another server")
#                     state.logger("Trying another server", "WARNING")

#                 except Exception as e:
#                     state.websocket_is_connected = False
#                     await self.on_error(e)

#             await asyncio.sleep(1)

#         return True

#     async def send_message(self, message):
#         while state.websocket_is_connected is False:
#             await asyncio.sleep(0.1)

#         self.message = message

#         if state.websocket_is_connected and message is not None:
#             try:
#                 await self.websocket.send(message)
#             except Exception as e:
#                 # logger.warning(f"Error sending message: {e}")
#                 state.logger("Error sending message: %s" % str(e), "WARNING")
#         elif message is not None:
#             # logger.warning("WebSocket not connected")
#             state.logger("WebSocket not connected", "WARNING")

#     @staticmethod
#     def dict_queue_add(self, dict, maxdict, key1, key2, key3, value):
#         if key3 in dict[key1][key2]:
#             dict[key1][key2][key3] = value
#         else:
#             while True:
#                 try:
#                     dic_size = len(dict[key1][key2])
#                 except:
#                     dic_size = 0
#                 if dic_size < maxdict:
#                     dict[key1][key2][key3] = value
#                     break
#                 else:
#                     # Remove the smallest key
#                     del dict[key1][key2][sorted(dict[key1][key2].keys(), reverse=False)[0]]

#     async def on_message(self, message):
#         """Method for processing websocket messages."""
#         if type(message) is bytes:
#             message2 = message.decode('utf-8')
#             message = message.decode('utf-8')
#             message = json.loads(message)

#             print(message)

#             if "balance" in message:
#                 if "uid" in message:
#                     state.balance_id = message["uid"]
#                 state.balance = message["balance"]
#                 state.balance_type = message["isDemo"]

#             elif "requestId" in message and message["requestId"] == 'buy':
#                 state.order_data = message
#                 #global_value.open_orders.insert(0, message)

#             elif self.updateClosedDeals and isinstance(message, list):
#                 state.closed_deals = message
#                 self.updateClosedDeals = False

#             elif self.successcloseOrder and isinstance(message, dict):
#                 self.api.closed_deals.append(message)
#                 self.api.order_async = message
#                 #global_value.closed_orders.insert(0, message)
#                 self.successcloseOrder = False

#             elif self.loadHistoryPeriod and isinstance(message, dict):
#                 self.loadHistoryPeriod = False
#                 self.api.history_data = message["data"]

#             elif self.updateStream and isinstance(message, list):
#                 self.updateStream = False
#                 if len(message[0]) == 3:
#                     self.api.time_sync.server_timestamp = message[0][1]
#                     if message[0][0] in state.pairs:
#                         if 'history' in state.pairs[message[0][0]]:
#                             h = {'time': message[0][1], 'price': message[0][2]}
#                             state.pairs[message[0][0]]['history'].append(h)

#             elif self.updateHistoryNew and isinstance(message, dict):
#                 self.updateHistoryNew = False
#                 self.api.history_new = message

#             elif '[[5,"#AAPL","Apple","stock' in message2:
#                 state.PayoutData = message2
#             return

#         else:
#             pass

#         if message.startswith('0') and "sid" in message:
#             await self.websocket.send("40")

#         elif message == "2":
#             await self.websocket.send("3")

#         elif "40" and "sid" in message:
#             await self.websocket.send(self.ssid)

#         elif message.startswith('451-['):
#             json_part = message.split("-", 1)[1]

#             message = json.loads(json_part)

#             if message[0] == "successauth":
#                 await on_open()

#             elif message[0] == "successupdateBalance":
#                 state.balance_updated = True
#             elif message[0] == "successopenOrder":
#                 state.result = True

#             elif message[0] == "updateClosedDeals":
#                 self.updateClosedDeals = True

#             elif message[0] == "successcloseOrder":
#                 self.successcloseOrder = True

#             elif message[0] == "loadHistoryPeriod":
#                 self.loadHistoryPeriod = True

#             elif message[0] == "updateStream":
#                 self.updateStream = True

#             elif message[0] == "updateHistoryNew":
#                 self.updateHistoryNew = True

#         elif message.startswith("42") and "NotAuthorized" in message:
#             # logging.error("User not Authorized: Please Change SSID for one valid")
#             state.logger("User not Authorized: Please Change SSID for one valid", "ERROR")
#             state.ssl_Mutual_exclusion = False
#             await self.websocket.close()

#     async def on_error(self, error):
#         # logger.error(error)
#         state.logger(str(error), "ERROR")
#         state.websocket_error_reason = str(error)
#         state.check_websocket_if_error = True

#     async def on_close(self, error):
#         # logger.debug("Websocket connection closed.")
#         # logger.warning(f"Websocket connection closed. Reason: {error}")
#         state.websocket_is_connected = False



import os
import json

import asyncio, websockets, json, ssl
from datetime import datetime, timedelta, timezone

import pocketoptionapi.constants as OP_code
import pocketoptionapi.state as state
from pocketoptionapi.constants import REGION
from pocketoptionapi.ws.objects.timesync import TimeSync
from pocketoptionapi.ws.objects.time_sync import TimeSynchronizer

# logger = logging.getLogger(__name__)

timesync = TimeSync()
sync = TimeSynchronizer()


async def on_open():
    state.logger("CONNECTED SUCCESSFULLY", "INFO")
    state.logger("Websocket client connected.", "DEBUG")
    state.websocket_is_connected = True


async def send_ping(ws):
    while state.websocket_is_connected is False:
        await asyncio.sleep(0.1)
    pass
    while True:
        await asyncio.sleep(20)
        await ws.send('42["ps"]')


async def process_message(message):
    try:
        data = json.loads(message)
        # print(data)  # removed: too noisy
        state.logger("Received message: %s" % str(data), "DEBUG")

        if isinstance(data, dict) and 'uid' in data:
            uid = data['uid']
            state.logger("UID: %s" % str(uid), "DEBUG")
        elif isinstance(data, list) and len(data) > 0:
            event_type = data[0]
            event_data = data[1]
            state.logger("Event type: %s, Event data: %s" %(str(event_type), str(event_data)), "DEBUG")

    except json.JSONDecodeError as e:
        state.logger("JSON decode error: %s" % str(e), "ERROR")
    except KeyError as e:
        state.logger("Key error: %s" % str(e), "ERROR")
    except Exception as e:
        state.logger("Error processing message: %s" % str(e), "ERROR")


class WebsocketClient(object):
    def __init__(self, api) -> None:
        self.updateHistoryNew = None
        self.updateStream = None
        self.loadHistoryPeriod = None
        self.updateClosedDeals = False
        self.successcloseOrder = False
        self.updateStream = False
        self.api = api
        self.message = None
        self.url = None
        self.ssid = state.SSID
        self.websocket = None
        self.region = REGION()
        self.loop = asyncio.get_event_loop()

    async def websocket_listener(self, ws):
        try:
            async for message in ws:
                await self.on_message(message)
        except Exception as e:
            # logger.warning(f"Error occurred: {e}")
            state.logger("Error occurred: %s" % str(e), "WARNING")

    async def connect(self):
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        try:
            await self.api.close()
        except:
            pass

        while not state.websocket_is_connected:
            for url in self.region.get_regions(state.DEMO):
                state.logger(str(url), "INFO")
                try:
                    async with websockets.connect(
                            url,
                            ssl=ssl_context,
                            additional_headers={
                                "Origin": "https://pocketoption.com",
                                "Cache-Control": "no-cache",
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
                            }
                    ) as ws:
                        self.websocket = ws
                        self.url = url
                        state.websocket_is_connected = True

                        # Create and run tasks
                        on_message_task = asyncio.create_task(self.websocket_listener(ws))
                        sender_task = asyncio.create_task(self.send_message(self.message))
                        ping_task = asyncio.create_task(send_ping(ws))

                        await asyncio.gather(on_message_task, sender_task, ping_task)

                except websockets.ConnectionClosed as e:
                    state.websocket_is_connected = False
                    await self.on_close(e)
                    # logger.warning("Trying another server")
                    state.logger("Trying another server", "WARNING")

                except Exception as e:
                    state.websocket_is_connected = False
                    await self.on_error(e)

            await asyncio.sleep(1)

        return True

    async def send_message(self, message):
        while state.websocket_is_connected is False:
            await asyncio.sleep(0.1)

        self.message = message

        if state.websocket_is_connected and message is not None:
            try:
                await self.websocket.send(message)
            except Exception as e:
                # logger.warning(f"Error sending message: {e}")
                state.logger("Error sending message: %s" % str(e), "WARNING")
        elif message is not None:
            # logger.warning("WebSocket not connected")
            state.logger("WebSocket not connected", "WARNING")

    @staticmethod
    def dict_queue_add(self, dict, maxdict, key1, key2, key3, value):
        if key3 in dict[key1][key2]:
            dict[key1][key2][key3] = value
        else:
            while True:
                try:
                    dic_size = len(dict[key1][key2])
                except:
                    dic_size = 0
                if dic_size < maxdict:
                    dict[key1][key2][key3] = value
                    break
                else:
                    # Remove the smallest key
                    del dict[key1][key2][sorted(dict[key1][key2].keys(), reverse=False)[0]]

    async def on_message(self, message):
        """Method for processing websocket messages."""
        if type(message) is bytes:
            message2 = message.decode('utf-8')
            message = message.decode('utf-8')
            message = json.loads(message)

            # print(message)  # removed: too noisy

            if "balance" in message:
                if "uid" in message:
                    state.balance_id = message["uid"]
                state.balance = message["balance"]
                state.balance_type = message["isDemo"]

            elif "requestId" in message and message["requestId"] == 'buy':
                state.order_data = message
                #global_value.open_orders.insert(0, message)

            elif self.updateClosedDeals and isinstance(message, list):
                state.closed_deals = message
                self.updateClosedDeals = False

            elif self.successcloseOrder and isinstance(message, dict):
                self.api.closed_deals.append(message)
                self.api.order_async = message
                #global_value.closed_orders.insert(0, message)
                self.successcloseOrder = False

            elif self.loadHistoryPeriod and isinstance(message, dict):
                self.loadHistoryPeriod = False
                self.api.history_data = message["data"]

            elif self.updateStream and isinstance(message, list):
                self.updateStream = False
                if len(message[0]) == 3:
                    asset = message[0][0]
                    ts    = message[0][1]
                    price = message[0][2]
                    self.api.time_sync.server_timestamp = ts
                    # Auto-initialize the pair dict so ticks always get stored
                    if asset not in state.pairs:
                        state.pairs[asset] = {}
                    if 'history' not in state.pairs[asset]:
                        state.pairs[asset]['history'] = []
                    state.pairs[asset]['history'].append({'time': ts, 'price': price})

            elif self.updateHistoryNew and isinstance(message, dict):
                self.updateHistoryNew = False
                self.api.history_new = message
                # Also store under the asset key for easy lookup
                asset = message.get("asset")
                if asset:
                    if asset not in state.pairs:
                        state.pairs[asset] = {}
                    state.pairs[asset]["history_new"] = message

            elif '[[5,"#AAPL","Apple","stock' in message2:
                state.PayoutData = message2

                # try:
                #     # Parse the message - it's a list of lists
                #     assets_data = json.loads(message2)
                    
                #     # Create directory if it doesn't exist
                #     data_dir = "data"
                #     if not os.path.exists(data_dir):
                #         os.makedirs(data_dir)
                    
                #     # Dictionary to store all assets
                #     actives = {}
                    
                #     # Define field names for better readability (based on data structure)
                #     # Index positions in each asset array:
                #     # 0: id, 1: symbol, 2: name, 3: type, 4: ?, 5: ?, 6: ?, 7: ?, 
                #     # 8: ?, 9: ?, 10: pair_id, 11: ?, 12: [], 13: timestamp, 14: is_otc, 
                #     # 15: expirations, 16: ?, 17: ?, 18: ?
                    
                #     for asset in assets_data:
                #         if len(asset) >= 11:  # Ensure we have enough elements
                #             actives[ asset[1]] = asset[0]
                    
                #     # Save to file
                #     file_path = os.path.join(data_dir, "actives.json")
                #     with open(file_path, 'w') as f:
                #         json.dump(actives, f, indent=2)
                    
                #     # Also save as Python pickle for faster loading (optional)
                #     import pickle
                #     pickle_path = os.path.join(data_dir, "actives.pkl")
                #     with open(pickle_path, 'wb') as f:
                #         pickle.dump(actives, f)
                    
                #     state.logger(f"Saved {len(actives)} assets to {file_path}", "INFO")
                    
                #     # Store in state for runtime access
                #     state.actives = actives
                    
                # except json.JSONDecodeError as e:
                #     state.logger(f"Error parsing assets data: {e}", "ERROR")
                # except Exception as e:
                #     state.logger(f"Error storing assets: {e}", "ERROR")
        
            return

        if message.startswith('0') and "sid" in message:
            await self.websocket.send("40")

        elif message == "2":
            await self.websocket.send("3")

        elif "40" and "sid" in message:
            await self.websocket.send(self.ssid)

        elif message.startswith('451-['):
            json_part = message.split("-", 1)[1]

            message = json.loads(json_part)

            if message[0] == "successauth":
                await on_open()

            elif message[0] == "successupdateBalance":
                state.balance_updated = True
            elif message[0] == "successopenOrder":
                state.result = True

            elif message[0] == "updateClosedDeals":
                self.updateClosedDeals = True

            elif message[0] == "successcloseOrder":
                self.successcloseOrder = True

            elif message[0] == "loadHistoryPeriod":
                self.loadHistoryPeriod = True

            elif message[0] == "updateStream":
                self.updateStream = True

            elif message[0] == "updateHistoryNew":
                self.updateHistoryNew = True

            elif message[0] == "updateHistoryNewFast":
                self.updateHistoryNew = True

        elif message.startswith("42") and "NotAuthorized" in message:
            # logging.error("User not Authorized: Please Change SSID for one valid")
            state.logger("User not Authorized: Please Change SSID for one valid", "ERROR")
            state.ssl_Mutual_exclusion = False
            await self.websocket.close()

    async def on_error(self, error):
        # logger.error(error)
        state.logger(str(error), "ERROR")
        state.websocket_error_reason = str(error)
        state.check_websocket_if_error = True

    async def on_close(self, error):
        # logger.debug("Websocket connection closed.")
        # logger.warning(f"Websocket connection closed. Reason: {error}")
        state.websocket_is_connected = False