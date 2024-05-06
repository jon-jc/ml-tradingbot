from dotenv import load_dotenv
import os
from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime

# Load environment variables
load_dotenv()

# Retrieve API details and other configurations from environment variables
API_KEY = os.getenv('API_KEY')
API_KEY_SECRET = os.getenv('API_KEY_SECRET')
BASE_URL = os.getenv('BASE_URL')

ALPACA_CREDS = {
    'API_KEY': API_KEY,
    'API_KEY_SECRET': API_KEY_SECRET,
    'PAPER': True,
}

class MLTrader(Strategy):
    def initialize(self):
        pass
    def on_trading_iteration(self):
        pass

start_date = datetime(2023, 12, 15)
end_date = datetime(2023, 12, 31)  # Corrected to use 'end_date' instead of the second 'start_date'

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name='MLTrader', broker=broker, parameters={})

strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters={}
)
