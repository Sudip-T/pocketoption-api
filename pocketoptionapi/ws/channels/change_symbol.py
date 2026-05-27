from pocketoptionapi.ws.channels.base import Base
import time, random


class ChangeSymbol(Base):
    """Class for Pocket option change symbol websocket chanel."""
    # pylint: disable=too-few-public-methods

    name = "sendMessage"

    def __call__(self, active_id, interval):

        data_stream = ["changeSymbol", {
            "asset": active_id,
            "period": interval}]

        self.send_websocket_request(self.name, data_stream)


class Subscribe(Base):
    """Class for PocketOption subscribe websocket channel."""
    # pylint: disable=too-few-public-methods

    name = "sendMessage"

    def __call__(self, active_id):
        """Method to send message to subscribe websocket channel.

        :param active_id: The active/asset identifier (e.g., "AEDCNY_otc").
        """

        # New PocketOption message format: 42["subfor","AEDCNY_otc"]
        data = ["subfor", active_id]

        self.send_websocket_request(self.name, data)


class Unsubscribe(Base):
    """Class for PocketOption unsubscribe websocket channel."""
    # pylint: disable=too-few-public-methods

    name = "sendMessage"

    def __call__(self, active_id):
        """Method to send message to unsubscribe websocket channel.

        :param active_id: The active/asset identifier (e.g., "AEDCNY_otc").
        """

        # New PocketOption message format: 42["unsubfor","AEDCNY_otc"]
        data = ["unsubfor", active_id]

        self.send_websocket_request(self.name, data)
