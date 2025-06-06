import hashlib
import hmac
import json
import time
import websocket
import logging
import threading


class WebSocketClient:
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._ws = None
        self._ping_thread = None
        self._bbo_data = {}

    def _on_message(self, ws, message):
        self._logger.info(f"Received message: {message}")
        data = json.loads(message)
        if "pong" in data:
            # Received a pong message from the server
            self._logger.info("Received pong message")
        # Handle the received market data here
        elif data.get("topic") == "bbo" and "data" in data:
            # Handle the received BBO data here
            bbo_data = data["data"]
            symbol = bbo_data.get("s")
            if symbol:
                self._bbo_data[symbol] = {
                    "bid_price": bbo_data.get("b"),
                    "bid_quantity": bbo_data.get("bz"),
                    "ask_price": bbo_data.get("a"),
                    "ask_quantity": bbo_data.get("az"),
                    "timestamp": bbo_data.get("t"),
                }
                self._logger.info(
                    f"Stored BBO Data for {symbol}: {self._bbo_data[symbol]}")

    def get_bbo_data(self, symbol=None):
        """Retrieve the latest BBO data for a specific symbol or all symbols."""
        if symbol:
            return self._bbo_data.get(symbol)
        return self._bbo_data

    def _on_error(self, ws, error):
        self._logger.error(f"WebSocket error: {error}")

    def _on_close(self, ws):
        self._logger.info("Connection closed")

    def _on_open(self, ws):
        self._logger.info("Subscribe topic")
        sub = {
            "topic": "bbo",
            "event": "sub",
            "params": {
                "symbol": "ETHUSDT"
            }
        }
        ws.send(json.dumps(sub))

        # Start the ping thread after connecting
        self._start_ping_thread()

    def _start_ping_thread(self):
        def send_ping():
            while self._ws:
                ping_message = {
                    # Send a timestamp as the ping message
                    "ping": int(time.time() * 1000)
                }
                self._ws.send(json.dumps(ping_message))
                self._logger.info(f"Send ping message: {ping_message}")
                time.sleep(5)

        self._ping_thread = threading.Thread(target=send_ping)
        self._ping_thread.daemon = True
        self._ping_thread.start()

    def unsubscribe(self):
        if self._ws:
            self._logger.info("Unsubscribe topic")
            unsub = {
                "topic": "bbo",
                "event": "sub",
                "params": {
                    "symbol": "ETHUSDT"
                }
            }
            self._ws.send(json.dumps(unsub))

    def connect(self):
        base_url = 'wss://stream-pro.hashkey.com'
        endpoint = 'quote/ws/v2'
        stream_url = f"{base_url}/{endpoint}"
        self._logger.info(stream_url)
        self._logger.info(f"Connecting to {stream_url}")

        self._ws = websocket.WebSocketApp(stream_url,
                                          on_message=self._on_message,
                                          on_error=self._on_error,
                                          on_close=self._on_close)
        self._ws.on_open = self._on_open

        self._ws.run_forever()

# if __name__ == '__main__':
#     logging.basicConfig(level=logging.INFO)

#     client = WebSocketClient()
#     client.connect()
