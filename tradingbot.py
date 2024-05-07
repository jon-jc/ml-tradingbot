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
API_SECRET = os.getenv('API_SECRET')
BASE_URL = os.getenv('BASE_URL')

ALPACA_CREDS = {
    'API_KEY': API_KEY,
    'API_SECRET': API_SECRET,
    'PAPER': True,
}

class MLTrader(Strategy):
    def initialize(self, symbol:str="SPY", cash_risk:float=.5):
        self.symbol = symbol
        self.sleeptime = "24H"
        self.last_trade = None
        self.cash_risk = cash_risk

    def position_sizing(self):
        value = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(value * self.cash_risk / last_price, 0)
        return value, last_price, quantity

    def on_trading_iteration(self):
        value, last_price, quantity = self.position_sizing()
        if value > last_price:
            if self.last_trade == None:
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "buy",
                    type="bracket",
                    take_profit_price=last_price * 1.20,
                    stop_loss_price=last_price * .95,
                )
                self.submit_order(order)
                self.last_trade = "buy"

start_date = datetime(2023, 12, 15)
end_date = datetime(2023, 12, 31)  # Corrected to use 'end_date' instead of the second 'start_date'

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name='MLTrader', broker=broker, parameters={"symbol": "SPY", "cash_risk": .5})

strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters={"symbol": "SPY", "cash_risk": .5}
)
