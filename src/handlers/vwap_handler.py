from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from services.hashkey_api import HashkeyAPI
from utils.logger import logger

logger.info("Logger in vwap_handler.py is initialized")

async def handle_vwap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Received /vwap command")

    try:
        symbol = context.args[0] if context.args else "BTCUSD"
        logger.info(f"Fetching VWAP for symbol: {symbol}")
        vwap = HashkeyAPI.get_vwap(symbol)
        vwap_rounded = round(vwap, 2)  # Round VWAP to 2 decimal places
        logger.info(f"VWAP fetched and rounded: {vwap_rounded}")
        await update.message.reply_text(f"The 24-hour VWAP for {symbol} is: {vwap_rounded}")
    except Exception as e:
        logger.error(f"Error in handle_vwap: {str(e)}")
        await update.message.reply_text(f"Error fetching VWAP: {str(e)}")