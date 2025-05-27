from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to the bot!")

async def handle_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Here is how you can use the bot...")

def register_handlers(dispatcher) -> None:
    dispatcher.add_handler(CommandHandler("start", handle_start))
    dispatcher.add_handler(CommandHandler("help", handle_help))