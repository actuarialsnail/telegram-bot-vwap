from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from services.hashkey_api import HashkeyAPI
from utils.logger import logger

logger.info("Logger in vwap_handler.py is initialized")


async def handle_vwap(message, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /vwap command")

    try:
        symbol = context.args[0] if context.args else "BTCUSD"
        logger.info(f"Fetching VWAP and market data for symbol: {symbol}")

        # Fetch VWAP
        vwap_24hr = HashkeyAPI.get_vwap(
            symbol=symbol, interval="3m", limit=480)
        vwap_rounded = round(vwap_24hr)

        # Calculate VWAP for the last 7 days using 1-hour intervals
        vwap_7d = HashkeyAPI.get_vwap(
            symbol=symbol, interval="15m", limit=672)  # 4* 168 hours = 7 days
        vwap_7d_rounded = round(vwap_7d)

        # Calculate VWAP for the last 30 days using 1-hour intervals
        vwap_30d = HashkeyAPI.get_vwap(
            symbol=symbol, interval="1h", limit=720)  # 720 hours = 30 days
        vwap_30d_rounded = round(vwap_30d)

       # Fetch 24-hour ticker price change data
        price_change_data = HashkeyAPI.get_24hr_ticker_price_change(symbol)
        timestamp = price_change_data["timestamp"]
        last_price = round(price_change_data["last_price"])
        high_price = round(price_change_data["high_price"])
        low_price = round(price_change_data["low_price"])
        opening_price = round(price_change_data["opening_price"])
        bid_price = round(price_change_data["bid_price"])
        ask_price = round(price_change_data["ask_price"])
        base_volume = round(price_change_data["base_volume"])
        quote_volume = round(price_change_data["quote_volume"])

        # Calculate VWAP position within High and Low
        vwap_within_range = ((vwap_24hr - low_price) / (high_price -
                             low_price)) * 100 if high_price > low_price else 0
        vwap_within_range_rounded = round(vwap_within_range, 2)

        # Calculate Last Price position within High and Low
        last_price_within_range = (
            (last_price - low_price) / (high_price - low_price)) * 100 if high_price > low_price else 0
        last_price_within_range_rounded = round(last_price_within_range, 2)

        # Create a text-based progress bar
        bar_length = 20  # Length of the progress bar
        vwap_filled_length = int((vwap_within_range / 100) * bar_length)
        last_price_filled_length = int(
            (last_price_within_range / 100) * bar_length)

        # Build the progress bar with markers for VWAP and Last Price
        progress_bar = ["-"] * bar_length
        if vwap_filled_length == last_price_filled_length:  # Handle overlap
            # Determine whether to use "VL" or "LV" based on which is larger
            if vwap_within_range > last_price_within_range:
                progress_bar[vwap_filled_length] = "LV"  # VWAP is larger
            else:
                progress_bar[vwap_filled_length] = "VL"  # Last Price is larger
        else:
            if vwap_filled_length < bar_length:
                progress_bar[vwap_filled_length] = "V"  # Mark VWAP position
            if last_price_filled_length < bar_length:
                # Mark Last Price position
                progress_bar[last_price_filled_length] = "L"
        progress_bar = "".join(progress_bar)

        logger.info(f"VWAP fetched and rounded: {vwap_rounded}")
        logger.info(
            f"24-hour ticker price change data fetched: {price_change_data}")

        # Send response
        await message.reply_text(
            f"<pre>"
            f"The 24-hour prices for {symbol}:\n"
            f"{'VWAP':<10}: {vwap_rounded:>7,}\n"
            f"{'Last':<10}: {last_price:>7,}\n"
            f"{'High':<10}: {high_price:>7,}\n"
            f"{'Low':<10}: {low_price:>7,}\n"
            f"{'Opening':<10}: {opening_price:>7,}\n"
            f"{'Bid':<10}: {bid_price:>7,}\n"
            f"{'Ask':<10}: {ask_price:>7,}\n"
            f"{'VWAP %':<10}: {vwap_within_range_rounded:>6,}%\n"
            f"{'Last %':<10}: {last_price_within_range_rounded:>6,}%\n"
            f"{'Position':<10}: [{progress_bar}]\n"
            f"Other timeframes:\n"
            f"{'VWAP 7d':<10}: {vwap_7d_rounded:>7,}\n"  # Add VWAP for 7 days
            f"{'VWAP 30d':<10}: {vwap_30d_rounded:>7,}\n"  # Add VWAP for 30 days
            f"</pre>",
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in handle_vwap: {str(e)}")
        await message.reply_text(f"Error fetching VWAP or market data: {str(e)}")
