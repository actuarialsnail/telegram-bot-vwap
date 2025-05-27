# Hashkey Telegram Bot

This project is a Telegram bot that interacts with users to provide access to Hashkey exchange market data and perform simple calculations. 

## Features

- Retrieve market data from the Hashkey exchange.
- Perform simple calculations based on user input.
- User-friendly commands for easy interaction.

## Project Structure

```
hashkey-telegram-bot
├── src
│   ├── bot.py                  # Main entry point for the Telegram bot
│   ├── handlers
│   │   ├── market_data_handler.py  # Handles market data requests
│   │   ├── calculation_handler.py   # Handles calculation requests
│   │   └── command_handler.py       # Manages bot commands
│   ├── services
│   │   ├── hashkey_api.py          # Interacts with the Hashkey exchange API
│   │   └── calculation_service.py   # Performs specific calculations
│   └── utils
│       └── logger.py               # Logger utility for tracking events
├── config
│   └── config.json                # Configuration settings for the bot
├── requirements.txt               # Project dependencies
└── README.md                      # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd hashkey-telegram-bot
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure the bot by editing the `config/config.json` file with your API keys and bot tokens.

## Usage

To run the bot, execute the following command:
```
python src/bot.py
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.