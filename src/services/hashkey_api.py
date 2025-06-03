import requests
import logging

logger = logging.getLogger(__name__)

class HashkeyAPI:

    BASE_URL = "https://api-pro.hashkey.com"

    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api-pro.hashkey.com"

    def get_market_data(self, symbol):
        endpoint = f"{self.base_url}/market_data/{symbol}"
        response = self._make_request(endpoint)
        return response

    def _make_request(self, endpoint):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
    
    @staticmethod
    def get_vwap(symbol: str) -> float:
        # Fetch historical trade data for the past 24 hours
        endpoint = f"{HashkeyAPI.BASE_URL}/quote/v1/trades"
        params = {"symbol": symbol, "limit": 100}  # Adjust limit as needed
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        trades = response.json()
        logger.info("trades:", trades)


        # Calculate VWAP
        total_volume = 0
        total_price_volume = 0
        for trade in trades:
            price = float(trade["p"])
            volume = float(trade["q"])
            total_volume += volume
            total_price_volume += price * volume

        return total_price_volume / total_volume if total_volume > 0 else 0
    
    def get_24hr_ticker_price_change(self, symbol: str) -> dict:
        # Fetch the 24-hour rolling price change data for the given symbol.
        endpoint = f"{self.base_url}/quote/v1/ticker/24hr"
        params = {"symbol": symbol}
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # Extract relevant data from the parsed response
        price_change_data = {
            "timestamp": int(data.get("t", 0)),
            "symbol": data.get("s", ""),
            "last_price": float(data.get("c", 0)),
            "high_price": float(data.get("h", 0)),
            "low_price": float(data.get("l", 0)),
            "opening_price": float(data.get("o", 0)),
            "bid_price": float(data.get("b", 0)),
            "ask_price": float(data.get("a", 0)),
            "base_volume": float(data.get("v", 0)),
            "quote_volume": float(data.get("qv", 0))
        }
        return price_change_data
