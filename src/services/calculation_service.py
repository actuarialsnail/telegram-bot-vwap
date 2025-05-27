def convert_currency(amount, exchange_rate):
    return amount * exchange_rate

def calculate_profit_loss(entry_price, exit_price, quantity):
    return (exit_price - entry_price) * quantity

def calculate_percentage_change(old_value, new_value):
    return ((new_value - old_value) / old_value) * 100

def calculate_average_price(prices):
    if not prices:
        return 0
    return sum(prices) / len(prices)

def perform_calculation(expression):
    try:
        # Evaluate the mathematical expression safely
        result = eval(expression, {"__builtins__": None}, {})
        return result
    except Exception as e:
        raise ValueError(f"Invalid calculation: {str(e)}")