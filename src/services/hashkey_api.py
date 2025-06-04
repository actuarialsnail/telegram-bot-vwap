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
    def get_vwap(symbol: str, interval: str = "3m", limit: int = 480) -> float:
        """
        Calculate VWAP using Kline data for a given symbol, interval, and limit.
        
        Args:
            symbol (str): The trading pair symbol (e.g., "ETHUSDT").
            interval (str): The interval for Kline data (e.g., "1m", "5m", "1h").
            limit (int): The number of Kline bars to fetch (max 1000).
        
        Returns:
            float: The calculated VWAP value.
        """
        # Fetch Kline data using the specified interval and limit
        endpoint = f"{HashkeyAPI.BASE_URL}/quote/v1/klines"
        params = {"symbol": symbol, "interval": interval, "limit": limit}
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        kline_data = response.json()

        # Ensure Kline data is available
        if not kline_data or len(kline_data) == 0:
            logger.error("No Kline data available for VWAP calculation.")
            return 0

        # Calculate VWAP using Kline data
        total_volume = 0
        total_price_volume = 0
        for kline in kline_data:
            price = float(kline[4])  # Close price
            volume = float(kline[5])  # Base asset volume
            total_volume += volume
            total_price_volume += price * volume

        return total_price_volume / total_volume if total_volume > 0 else 0
    
    @staticmethod
    def get_24hr_ticker_price_change(symbol: str) -> dict:
        # Fetch the 24-hour rolling price change data for the given symbol.
        endpoint = f"{HashkeyAPI.BASE_URL}/quote/v1/ticker/24hr"
        params = {"symbol": symbol}
        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        
        # Parse the JSON response
        data = response.json()
        
        # If the response is a list, extract the first element
        if isinstance(data, list) and len(data) > 0:
            data = data[0]  # Extract the first element
        
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
