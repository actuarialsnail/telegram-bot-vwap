from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from handlers.command_handler import handle_help
from handlers.vwap_handler import handle_vwap
from utils.logger import logger
from services.websocket_service import WebSocketClient
import json
import asyncio
import os
import inspect

# Initialize the WebSocket client
websocket_client = WebSocketClient()
application = None


def save_bot_data(application):
    """Save bot_data to a local JSON file in the config folder."""
    config_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), '../config/bot_data.json')
    with open(config_path, 'w') as f:
        # Access bot_data attribute of application
        json.dump(application.bot_data, f)
    logger.info("Bot data saved to ../config/bot_data.json.")


def load_bot_data(application):
    """Load bot_data from a local JSON file in the config folder."""
    config_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), '../config/bot_data.json')
    try:
        with open(config_path, 'r') as f:
            # Access bot_data attribute of application
            application.bot_data = json.load(f)
        logger.info("Bot data loaded from ../config/bot_data.json.")
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
    """Handle the /vwap command and display options for BTCUSD, ETHUSD and ALL pairs."""
    buttons = [
        [InlineKeyboardButton("BTCUSD", callback_data="vwap_BTCUSD")],
        [InlineKeyboardButton("ETHUSD", callback_data="vwap_ETHUSD")],
        [InlineKeyboardButton("ALL", callback_data="vwap_ALL")]  # new button for all pairs
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        "Choose a pair for VWAP calculation:",
        reply_markup=reply_markup
    )


async def handle_vwap_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the user's selection of BTCUSD, ETHUSD or ALL."""
    query = update.callback_query
    await query.answer()  # Acknowledge the callback query

    pair = query.data.split("_", 1)[1]  # Extract the pair from callback data

    if pair == "ALL":
        # trigger VWAP for both pairs
        pairs = ["BTCUSD", "ETHUSD"]
        await query.edit_message_text("Calculating VWAP for all pairs...")
        for p in pairs:
            context.args = [p]
            await handle_vwap(query.message, context)
    else:
        await query.edit_message_text(f"Calculating VWAP for {pair}...")
        context.args = [pair]
        await handle_vwap(query.message, context)


async def handle_bbo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /latest command to fetch the latest data from the WebSocket."""
    try:
        # get_bbo_data is blocking; run in thread to avoid blocking handler
        if hasattr(asyncio, "to_thread"):
            data = await asyncio.to_thread(websocket_client.get_bbo_data)
        else:
            loop = asyncio.get_running_loop()
            data = await loop.run_in_executor(None, websocket_client.get_bbo_data)
        await update.message.reply_text(f"Latest data: {data}")
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


# --- Replaced blocking/threaded monitor/connect with async-safe background tasks ---
async def monitor_websocket_async(application):
    """Run inside the application's event loop. Use to_thread or run_in_executor for blocking calls."""
    loop = asyncio.get_running_loop()
    try:
        while True:
            try:
                if hasattr(asyncio, "to_thread"):
                    data = await asyncio.to_thread(websocket_client.get_bbo_data)
                else:
                    data = await loop.run_in_executor(None, websocket_client.get_bbo_data)

                if not data:
                    logger.warning("Received empty data from WebSocket.")
                    await asyncio.sleep(10)
                    continue

                for chat_id in application.bot_data.get('subscribed_chat_ids', []):
                    if application.bot is None:
                        logger.error("Bot instance is not initialized!")
                        continue
                    try:
                        await application.bot.send_message(chat_id=chat_id, text=f"{data}")
                        logger.info(f"Message sent to chat_id {chat_id}")
                    except Exception as send_error:
                        logger.error(f"Failed to send message to chat_id {chat_id}: {send_error}")

                await asyncio.sleep(10)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in WebSocket monitoring loop: {e}")
                await asyncio.sleep(5)
    finally:
        logger.info("monitor_websocket_async stopped.")


async def start_websocket_background(application):
    """Run inside post_init: schedule connect and monitor using asyncio.create_task.
    Handles both coroutine and blocking connect() implementations and prevents
    exceptions from escaping post_init.
    """
    application.bot_data.setdefault("ws_tasks", [])
    loop = asyncio.get_running_loop()

    try:
        # Helper to run blocking connect safely and log exceptions
        def _blocking_connect():
            try:
                websocket_client.connect()
            except Exception as e:
                logger.error(f"WebSocket connect failed (blocking): {e}")

        # Helper to run coroutine connect safely and log exceptions
        async def _coro_connect_wrapper():
            try:
                await websocket_client.connect()
            except Exception as e:
                logger.error(f"WebSocket connect failed (coroutine): {e}")

        # Create connect task depending on whether connect is async or blocking
        if inspect.iscoroutinefunction(getattr(websocket_client, "connect", None)):
            connect_task = asyncio.create_task(_coro_connect_wrapper(), name="ws_connect_coro")
        else:
            if hasattr(asyncio, "to_thread"):
                connect_task = asyncio.create_task(asyncio.to_thread(_blocking_connect), name="ws_connect_thread")
            else:
                # run_in_executor returns a Future; ensure_future accepts it
                connect_future = loop.run_in_executor(None, _blocking_connect)
                connect_task = asyncio.ensure_future(connect_future, loop=loop)

        # Start monitor (always a coroutine)
        monitor_task = asyncio.create_task(monitor_websocket_async(application), name="ws_monitor")

        # Save tasks for shutdown cancellation/await
        application.bot_data["ws_tasks"].extend([connect_task, monitor_task])

    except Exception as e:
        # Log and do not re-raise — post_init must not raise otherwise run_until_complete fails
        logger.error(f"Failed to start websocket background tasks: {e}")


async def stop_websocket_background(application):
    """Cancel and await websocket tasks and ensure websocket disconnected."""
    tasks = application.bot_data.get("ws_tasks", [])
    # cancel tasks
    for t in tasks:
        try:
            t.cancel()
        except Exception:
            pass

    # await tasks completion
    for t in tasks:
        try:
            await t
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.debug(f"ws task error during shutdown: {e}")

    # ensure websocket is disconnected (run blocking disconnect in thread)
    try:
        if hasattr(asyncio, "to_thread"):
            await asyncio.to_thread(websocket_client.disconnect)
        else:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, websocket_client.disconnect)
    except Exception as e:
        logger.error(f"Error while disconnecting websocket_client: {e}")


def main():
    # Get the absolute path to the config file relative to this script
    config_path = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), '../config/config.json')

    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    bot_token = config['DEFAULT']['telegram_bot_token']
    # register both start and shutdown hooks so background tasks are created and cleaned up correctly
    application = (
        Application.builder()
        .token(bot_token)
        .post_init(start_websocket_background)
        .post_shutdown(stop_websocket_background)
        .build()
    )

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
        # run_polling starts the application's event loop and will execute post_init callbacks
        application.run_polling()  # Start polling for Telegram updates
    except KeyboardInterrupt:
        logger.info("Bot is shutting down...")
    finally:
        logger.info("Cleaning up resources...")
        try:
            websocket_client.disconnect()  # Ensure WebSocket is terminated
        except Exception as e:
            logger.error(f"Error while disconnecting websocket_client: {e}")
        logger.info("Bot stopped.")


if __name__ == '__main__':
    main()
