def get_market_data(update, context):
    # Function to handle market data requests
    try:
        # Fetch market data from the Hashkey API
        market_data = hashkey_api.get_market_data()
        response_message = format_market_data(market_data)
        context.bot.send_message(chat_id=update.effective_chat.id, text=response_message)
    except Exception as e:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Error fetching market data.")
        logger.error(f"Error in get_market_data: {e}")

def format_market_data(market_data):
    # Function to format market data for user-friendly display
    formatted_data = "Market Data:\n"
    for item in market_data:
        formatted_data += f"Symbol: {item['symbol']}, Price: {item['price']}, Volume: {item['volume']}\n"
    return formatted_data

def handle_market_data(update, context):
    # Function to handle the /marketdata command
    get_market_data(update, context)