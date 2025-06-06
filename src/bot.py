from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from handlers.command_handler import handle_help
from handlers.vwap_handler import handle_vwap
from utils.logger import logger
from services.websocket_service import WebSocketClient
import json
import threading

# Initialize the WebSocket client
websocket_client = WebSocketClient()


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command and send a keyboard with buttons."""
    buttons = [['/help', '/vwap']]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome! Choose a command using the buttons below:",
        reply_markup=reply_markup
    )


async def show_vwap_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /vwap command and display options for BTCUSD and ETHUSD."""
    buttons = [
        [InlineKeyboardButton("BTCUSD", callback_data="vwap_BTCUSD")],
        [InlineKeyboardButton("ETHUSD", callback_data="vwap_ETHUSD")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        "Choose a pair for VWAP calculation:",
        reply_markup=reply_markup
    )


async def handle_vwap_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the user's selection of BTCUSD or ETHUSD."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    pair = query.data.split("_")[1]  # Extract the pair from callback data
    await query.edit_message_text(f"Calculating VWAP for {pair}...")

    # Set the pair as an argument for handle_vwap
    context.args = [pair]

    # Call the VWAP handler directly with query.message
    # Pass query.message to handle_vwap
    await handle_vwap(query.message, context)


async def handle_bbo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /latest command to fetch the latest data from the WebSocket."""
    try:
        bbo_data = websocket_client.get_bbo_data()  # Fetch the latest data
        await update.message.reply_text(f"Latest data: {bbo_data}")
    except Exception as e:
        logger.error(f"Error fetching latest data: {e}")
        await update.message.reply_text("Failed to fetch the BBO data. Please try again later.")

# Start the WebSocket service when the bot starts
def connect_websocket():
    logger.info("Background websocket is starting...")
    websocket_client.connect()


def main():
    with open('../config/config.json', 'r') as config_file:
        config = json.load(config_file)

    bot_token = config['DEFAULT']['telegram_bot_token']
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler(
        "start", handle_start))  # Updated start handler
    application.add_handler(CommandHandler("help", handle_help))
    # Renamed VWAP options handler
    application.add_handler(CommandHandler("vwap", show_vwap_options))
    # Callback handler for VWAP selection
    application.add_handler(CallbackQueryHandler(handle_vwap_selection))
    application.add_handler(CommandHandler("bbo", handle_bbo))

    # Start the WebSocket connection in a separate thread
    thread = threading.Thread(target=connect_websocket)
    thread.start()

    logger.info("Bot is starting...")
    application.run_polling()
    logger.info("Polling started")


if __name__ == '__main__':
    main()
