
# Here we demonstrate how your agent can request data and send an alert to your wallet.

# To receive messages to your Fetch.ai wallet (set to the Dorado testnet), enter your wallet address below:
MY_WALLET_ADDRESS = "E8FF7ypWJCmcUquEbT28QtPTRMEgotzb7YxuCVUHiLK2"

# If the price goes over this threshold, you will receive a message in your wallet
THRESHOLD_EURO = 27000

BTC_PRICE_URL = 'https://api.coindesk.com/v1/bpi/currentprice.json'

def get_btc_price():
    response = requests.get(BTC_PRICE_URL) #You could also enter the URL directly here
    if response.status_code == 200:
        data = response.json()
        return data['bpi']['EUR']['rate']
    return None

@agent.on_interval(period=10)
async def log_btc_price(ctx: Context):
    price = get_btc_price()

    # Only produce an alert if the price has moved across the threshold in either direction
    alert = None
    if price:
        ctx.logger.info(f"The current Bitcoin price is: {price} EURO")
        if float(price.replace(",", "")) > THRESHOLD_EURO:
            alert = f"The BTC price is now over the specified threshold: {price} > {THRESHOLD_EURO} EURO"
        else:
            alert = f"The BTC price is back under the specified threshold: {price} < {THRESHOLD_EURO} EURO"
    else:
        ctx.logger.info(f"I couldn't get the Bitcoin price")

    if alert:
        ctx.logger.info(alert)
        if MY_WALLET_ADDRESS != "fetch1___":
            await ctx.send_wallet_message(MY_WALLET_ADDRESS, alert)
        #else:
            #ctx.logger.info("To receive wallet alerts, set 'MY_WALLET_ADDRESS' to your wallet address.")
            #When linking a real wallet, get an Alert here
