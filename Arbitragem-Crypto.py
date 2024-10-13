import requests
import hmac
import hashlib
import time


class ArbitrageAgent:
    BINANCE_API = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    COINBASE_API = "https://api.coinbase.com/v2/prices/BTC-USD/spot"
    KRAKEN_API = "https://api.kraken.com/0/public/Ticker?pair=BTCUSD"

    def __init__(self, binance_api_key=None, binance_secret_key=None):
        self.binance_price = None
        self.coinbase_price = None
        self.kraken_price = None
        self.binance_api_key = binance_api_key
        self.binance_secret_key = binance_secret_key

    def fetch_prices(self):
        """Coleta os preços de Bitcoin em três exchanges diferentes."""
        self.binance_price = self._fetch_binance_price()
        self.coinbase_price = self._fetch_coinbase_price()
        self.kraken_price = self._fetch_kraken_price()

    def _fetch_binance_price(self):
        response = requests.get(self.BINANCE_API)
        data = response.json()
        return float(data['price'])

    def _fetch_coinbase_price(self):
        response = requests.get(self.COINBASE_API)
        data = response.json()
        return float(data['data']['amount'])

    def _fetch_kraken_price(self):
        response = requests.get(self.KRAKEN_API)
        data = response.json()
        return float(data['result']['XXBTZUSD']['c'][0])

    def find_arbitrage_opportunities(self):
        """Compara os preços coletados e identifica oportunidades de arbitragem."""
        opportunities = []

        if self.binance_price < self.coinbase_price:
            opportunities.append(f"Buy on Binance ({self.binance_price}) and sell on Coinbase ({self.coinbase_price})")

        if self.coinbase_price < self.binance_price:
            opportunities.append(f"Buy on Coinbase ({self.coinbase_price}) and sell on Binance ({self.binance_price})")

        if self.binance_price < self.kraken_price:
            opportunities.append(f"Buy on Binance ({self.binance_price}) and sell on Kraken ({self.kraken_price})")

        if self.kraken_price < self.binance_price:
            opportunities.append(f"Buy on Kraken ({self.kraken_price}) and sell on Binance ({self.binance_price})")

        return opportunities

    def execute_binance_trade(self, symbol, side, quantity):
        """Executa uma ordem de trade de mercado na Binance."""
        base_url = 'https://api.binance.com'
        endpoint = '/api/v3/order'
        timestamp = int(time.time() * 1000)
        query = f"symbol={symbol}&side={side}&type=MARKET&quantity={quantity}&timestamp={timestamp}"
        signature = hmac.new(self.binance_secret_key.encode(), query.encode(), hashlib.sha256).hexdigest()

        url = f"{base_url}{endpoint}?{query}&signature={signature}"
        headers = {"X-MBX-APIKEY": self.binance_api_key}

        response = requests.post(url, headers=headers)
        return response.json()

    def act(self):
        """Método principal para executar o comportamento do agente."""
        # Coleta os preços
        self.fetch_prices()

        # Encontra e exibe oportunidades de arbitragem
        opportunities = self.find_arbitrage_opportunities()
        if opportunities:
            for opportunity in opportunities:
                print(opportunity)
                # Opcional: Executar trade automático, com base nas oportunidades
                # Exemplo: self.execute_binance_trade("BTCUSDT", "BUY", 0.001)
        else:
            print("Nenhuma oportunidade de arbitragem foi encontrada.")


# Exemplo de uso da classe ArbitrageAgent
if __name__ == "__main__":
    print("Init Arbitrage bot")
    agent = ArbitrageAgent(binance_api_key="YOUR_BINANCE_API_KEY", binance_secret_key="YOUR_BINANCE_SECRET_KEY")
    while True:
        agent.act()
        time.sleep(60)  # Executar a cada minuto
