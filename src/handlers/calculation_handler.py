from services.calculation_service import perform_calculation
from telegram import Update
from telegram.ext import CallbackContext

def handle_calculation(update: Update, context: CallbackContext):
    user_input = ' '.join(context.args)
    
    if not user_input:
        update.message.reply_text("Please provide a calculation request.")
        return

    try:
        result = perform_calculation(user_input)
        update.message.reply_text(f"The result of your calculation is: {result}")
    except Exception as e:
        update.message.reply_text(f"Error processing your request: {str(e)}")