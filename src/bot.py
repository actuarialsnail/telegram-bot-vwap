from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from handlers.command_handler import handle_help
from handlers.vwap_handler import handle_vwap
from utils.logger import logger
from services.websocket_service import WebSocketClient
import json
import threading
import time
import asyncio
from functools import partial

# Initialize the WebSocket client
websocket_client = WebSocketClient()
application = None


def save_bot_data(application):
    """Save bot_data to a local JSON file."""
    with open('bot_data.json', 'w') as f:
        # Access bot_data attribute of application
        json.dump(application.bot_data, f)
    logger.info("Bot data saved to bot_data.json.")


def load_bot_data(application):
    """Load bot_data from a local JSON file."""
    try:
        with open('bot_data.json', 'r') as f:
            # Access bot_data attribute of application
            application.bot_data = json.load(f)
        logger.info("Bot data loaded from bot_data.json.")
    except FileNotFoundError:
        # Initialize with an empty dictionary if the file doesn't exist
        application.bot_data = {}
        logger.info("Bot data file not found. Starting with empty bot_data.")
    except json.JSONDecodeError:
        # Initialize with an empty dictionary if the file is corrupted
        application.bot_data = {}
        logger.error(
            "Bot data file is corrupted. Starting with empty bot_data.")


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command and send a keyboard with buttons."""
    buttons = [['/help', '/vwap']]
    reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
    await update.message.reply_text(
        "Welcome! Choose a command using the buttons below:",
        reply_markup=reply_markup
    )
    # await context.application.bot.send_message(chat_id=2053201425, text="Test message")


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


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /subscribe command to add the user to the notification list."""
    chat_id = update.message.chat_id
    if 'subscribed_chat_ids' not in context.bot_data:
        context.bot_data['subscribed_chat_ids'] = []

    if chat_id not in context.bot_data['subscribed_chat_ids']:
        context.bot_data['subscribed_chat_ids'].append(chat_id)
        await update.message.reply_text("You have successfully subscribed to notifications!")
        logger.info(f"Chat ID {chat_id} subscribed.")
        save_bot_data(context)  # Save bot_data to file
    else:
        await update.message.reply_text("You are already subscribed to notifications.")


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /unsubscribe command to remove the user from the notification list."""
    chat_id = update.message.chat_id
    if 'subscribed_chat_ids' in context.bot_data and chat_id in context.bot_data['subscribed_chat_ids']:
        context.bot_data['subscribed_chat_ids'].remove(chat_id)
        await update.message.reply_text("You have successfully unsubscribed from notifications.")
        logger.info(f"Chat ID {chat_id} unsubscribed.")
        save_bot_data(context)  # Save bot_data to file
    else:
        await update.message.reply_text("You are not subscribed to notifications.")


def monitor_websocket(application):
    # Create and set an event loop for the current thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    while True:  # Infinite loop for monitoring WebSocket data
        try:
            # Fetch data from the WebSocket
            data = websocket_client.get_bbo_data()  # Access shared websocket_client object
            logger.info(f"Received data from WebSocket: {data}")

            # Send notifications to all subscribed users
            for chat_id in application.bot_data.get('subscribed_chat_ids', []):
                logger.info(f"Sending message to chat_id {chat_id}: {data}")
                # loop.run_in_executor(
                #     None, partial(application.bot.send_message, chat_id=chat_id, text=f"hello")
                # )

                async def test():

                    if application.bot is None:
                        logger.error("Bot instance is not initialized!")
                    else:
                        logger.info(
                            f"Bot instance is initialized: {application.bot.send_message}")

                    await application.bot.send_message(
                        chat_id=2053201425, text=f"HELLO")

                asyncio.run_coroutine_threadsafe(
                    test(), loop
                )
            time.sleep(10)  # Adjust the polling interval as needed
        except Exception as e:
            logger.error(f"Error in WebSocket monitoring: {e}")
            break


def connect_websocket(application):
    logger.info("Background websocket is starting...")
    # Start the WebSocket connection in a separate thread
    connect_thread = threading.Thread(target=websocket_client.connect)
    connect_thread.daemon = True  # Make the thread a daemon
    connect_thread.start()

    # Pass the application object to monitor_websocket
    monitor_thread = threading.Thread(
        target=monitor_websocket, args=(application,))
    monitor_thread.daemon = True  # Make the thread a daemon
    monitor_thread.start()


def main():
    with open('../config/config.json', 'r') as config_file:
        config = json.load(config_file)

    bot_token = config['DEFAULT']['telegram_bot_token']
    application = Application.builder().token(bot_token).build()

    # Load bot_data from file
    load_bot_data(application)

    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(CommandHandler("help", handle_help))
    application.add_handler(CommandHandler("vwap", show_vwap_options))
    application.add_handler(CallbackQueryHandler(handle_vwap_selection))
    application.add_handler(CommandHandler("bbo", handle_bbo))
    application.add_handler(CommandHandler(
        "subscribe", subscribe))  # Subscribe command
    application.add_handler(CommandHandler(
        "unsubscribe", unsubscribe))  # Unsubscribe command

    logger.info("Bot is starting...")
    try:
        connect_websocket(application)  # Start the WebSocket connection
        application.run_polling()  # Start polling for Telegram updates
    except KeyboardInterrupt:
        logger.info("Bot is shutting down...")
    finally:
        logger.info("Cleaning up resources...")
        websocket_client.disconnect()  # Ensure WebSocket is terminated
        save_bot_data(application.bot_data)  # Save bot_data before exiting
        logger.info("Bot stopped.")


if __name__ == '__main__':
    main()
