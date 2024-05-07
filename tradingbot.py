from dotenv import load_dotenv
import os
from lumibot.brokers import Alpaca
from lumibot.backtesting import YahooDataBacktesting
from lumibot.strategies.strategy import Strategy
from lumibot.traders import Trader
from datetime import datetime
from alpaca_trade_api.rest import REST
from timedelta import Timedelta
from utils import estimate_sentiment

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
        self.api = REST(base_url=BASE_URL, key_id=API_KEY, secret_key=API_SECRET)

    def position_sizing(self):
        value = self.get_cash()
        last_price = self.get_last_price(self.symbol)
        quantity = round(value * self.cash_risk / last_price, 0)
        return value, last_price, quantity
    
    def get_dates(self): 
        today = self.get_datetime()
        three_days_prior = today - Timedelta(days=3)
        return today.strftime('%Y-%m-%d'), three_days_prior.strftime('%Y-%m-%d')
    
    def get_sentiment(self):
        today, three_days_ago = self.get_dates()
        news = self.api.get_news(symbol=self.symbol, start=three_days_ago, end= today)

        news = [ev.__dict__["_raw"]["headline"] for ev in news]
        probability, sentiment = estimate_sentiment(news)
        return probability, sentiment

    def on_trading_iteration(self):
        value, last_price, quantity = self.position_sizing()
        probability, sentiment = self.get_sentiment()
        if value > last_price:
            if sentiment == "positive" and probability > .999:
                if self.last_trade == "sell":
                    self.sell_all
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
            elif sentiment == "negative" and probability > .999:
                if self.last_trade == "buy":
                    self.sell_all()
                order = self.create_order(
                    self.symbol,
                    quantity,
                    "sell",
                    type="bracket",
                    take_profit_price=last_price * .8,
                    stop_loss_price=last_price * 1.05,
                )
                self.submit_order(order)
                self.last_trade = "sell"
        
start_date = datetime(2020, 1, 1)
end_date = datetime(2023, 1, 1)  # Corrected to use 'end_date' instead of the second 'start_date'

broker = Alpaca(ALPACA_CREDS)
strategy = MLTrader(name='MLTrader', broker=broker, parameters={"symbol": "SPY", "cash_risk": .5})

strategy.backtest(
    YahooDataBacktesting,
    start_date,
    end_date,
    parameters={"symbol": "SPY", "cash_risk": .5}
)
