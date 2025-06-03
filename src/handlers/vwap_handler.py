from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from services.hashkey_api import HashkeyAPI
from utils.logger import logger

logger.info("Logger in vwap_handler.py is initialized")

async def handle_vwap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /vwap command")

    try:
        symbol = context.args[0] if context.args else "BTCUSD"
        logger.info(f"Fetching VWAP and market data for symbol: {symbol}")
        
        # Fetch VWAP
        vwap = HashkeyAPI.get_vwap(symbol)
        vwap_rounded = round(vwap, 2)  # Round VWAP to 2 decimal places
        
       # Fetch 24-hour ticker price change data
        price_change_data = HashkeyAPI.get_24hr_ticker_price_change(symbol)
        timestamp = price_change_data["timestamp"]
        last_price = round(price_change_data["last_price"], 2)
        high_price = round(price_change_data["high_price"], 2)
        low_price = round(price_change_data["low_price"], 2)
        opening_price = round(price_change_data["opening_price"], 2)
        bid_price = round(price_change_data["bid_price"], 2)
        ask_price = round(price_change_data["ask_price"], 2)
        base_volume = round(price_change_data["base_volume"], 2)
        quote_volume = round(price_change_data["quote_volume"], 2)
        
        logger.info(f"VWAP fetched and rounded: {vwap_rounded}")
        logger.info(f"24-hour ticker price change data fetched: {price_change_data}")
        
        # Send response
        await update.message.reply_text(
            f"The 24-hour prices: \n"
            f"VWAP for {symbol} is: {vwap_rounded}\n"
            f"Last Price: {last_price}\n"
            f"High Price: {high_price}\n"
            f"Low Price: {low_price}\n"
            f"Opening Price: {opening_price}\n"
            f"Bid Price: {bid_price}\n"
            f"Ask Price: {ask_price}\n"
        )
    except Exception as e:
        logger.error(f"Error in handle_vwap: {str(e)}")
        await update.message.reply_text(f"Error fetching VWAP or market data: {str(e)}")