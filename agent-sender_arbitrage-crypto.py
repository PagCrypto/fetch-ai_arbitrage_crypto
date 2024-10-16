import requests
import hmac
import hashlib
import time

from uagents import Agent, Context, Model


BINANCE_API_KEY = os.environ.get("BINANCE_API_KEY", "BINANCE_API_KEY")
BINANCE_SECRET_KEY = os.environ.get("BINANCE_SECRET_KEY", "BINANCE_SECRET_KEY")

if BINANCE_API_KEY == "BINANCE_API_KEY":
    raise Exception("You need to provide an API key for BINANCE")

if BINANCE_SECRET_KEY == "BINANCE_SECRET_KEY":
    raise Exception("You need to provide an SECRET key for BINANCE")


agent = Agent()

agentSender = "agent1qvp58kzmem2nsc7r4kl5htt9hnvhsd9gxt6h4tzq5nv028hfrmrmsmnxev8"
agentConsumer = "agent1qw3ezrfth87498566uhe9jek7dhs73rcs7q0nc5rqdayn0l5xgn7z7pykg9"

BINANCE_API = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
COINBASE_API = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
KRAKEN_API = "https://api.kraken.com/0/public/Ticker?pair=BTCUSD"

binance_price = None
coinbase_price = None
kraken_price = None
binance_api_key = BINANCE_API_KEY
binance_secret_key = BINANCE_SECRET_KEY


class MessageRequest(Model):
    message: str

class OpportunitiesRequest(Model):
    opportunities = []

def fetch_prices():
    binance_price = fetch_binance_price()
    coinbase_price = fetch_coinbase_price()
    kraken_price = fetch_kraken_price()

def fetch_binance_price():
    response = requests.get(BINANCE_API)
    data = response.json()
    return float(data['price'])

def fetch_coinbase_price():
    response = requests.get(COINBASE_API)
    data = response.json()
    return float(data['data']['amount'])

def fetch_kraken_price():
    response = requests.get(KRAKEN_API)
    data = response.json()
    return float(data['result']['XXBTZUSD']['c'][0])

def find_arbitrage_opportunities():
    opportunities = []

    # Verifica se todos os preços foram coletados antes de comparar
    if binance_price is not None and coinbase_price is not None:
        if binance_price < coinbase_price:
            opportunities.append(f"Buy on Binance ({binance_price}) and sell on Coinbase ({coinbase_price})")

        if coinbase_price < binance_price:
            opportunities.append(f"Buy on Coinbase ({coinbase_price}) and sell on Binance ({binance_price})")

    if binance_price is not None and kraken_price is not None:
        if binance_price < kraken_price:
            opportunities.append(f"Buy on Binance ({binance_price}) and sell on Kraken ({kraken_price})")

        if kraken_price < binance_price:
            opportunities.append(f"Buy on Kraken ({kraken_price}) and sell on Binance ({binance_price})")

    return opportunities

def execute_binance_trade(symbol, side, quantity):
    base_url = 'https://api.binance.com'
    endpoint = '/api/v3/order'
    timestamp = int(time.time() * 1000)
    query = f"symbol={symbol}&side={side}&type=MARKET&quantity={quantity}&timestamp={timestamp}"
    signature = hmac.new(binance_secret_key.encode(), query.encode(), hashlib.sha256).hexdigest()

    url = f"{base_url}{endpoint}?{query}&signature={signature}"
    headers = {"X-MBX-APIKEY": binance_api_key}

    response = requests.post(url, headers=headers)
    return response.json()

# 'period' in seconds.
@agent.on_interval(period=5)
async def on_interval_opportunities(ctx: Context):
    fetch_prices()
    opportunities = find_arbitrage_opportunities()
    await ctx.send(agentConsumer, MessageRequest(opportunities=opportunities))


@agent.on_message(model=MessageRequest)
async def handle_message(ctx: Context, sender: str, msg: MessageRequest):
    ctx.logger.info(f"Received message from {sender} : {msg.message}")


@agent.on_message(model=OpportunitiesRequest)
async def handle_message(ctx: Context, sender: str, msg: OpportunitiesRequest):
    ctx.logger.info(f"Received message from {sender} : {msg.message}")

@agent.on_event("startup")
async def send_message(ctx: Context):
    ctx.logger.info(f"Looking for arbitrage opportunities")

if __name__ == "__main__":
    agent.run()
    
