from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from handlers.market_data_handler import handle_market_data
from handlers.calculation_handler import handle_calculation
from handlers.command_handler import handle_start, handle_help
from handlers.vwap_handler import handle_vwap  # Import the VWAP handler

from services.hashkey_api import HashkeyAPI
from utils.logger import logger
import json


def main():
    with open('../config/config.json', 'r') as config_file:
        config = json.load(config_file)

    bot_token = config['DEFAULT']['telegram_bot_token']
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(CommandHandler("vwap", handle_vwap))  # Add VWAP command

    # application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_market_data))
    # application.add_handler(MessageHandler(filters.Regex(
    #     r'^\d+(\.\d+)?\s*[\+\-\*\/]\s*\d+(\.\d+)?$'), handle_calculation))

    logger.info("Bot is starting...")
    application.run_polling()
    logger.info("Polling started")

if __name__ == '__main__':
    main()
