from binance.client import Client

API = ''
SECRET = ''


class BinanceClient:

    def __init__(self):
        print("Loading Binance client...")
        self.client = Client(api_key=API, api_secret=SECRET)

    def get_asset_price(self, pair):
        if pair == 'XRPUSDT':
            return round(float(self.client.get_avg_price(symbol=pair)['price']), 4)
        return round(float(self.client.get_avg_price(symbol=pair)['price']), 2)

    def get_asset_24hr_price_change(self, pair):
        if pair == 'XRPUSDT':
            return round(float(self.client.get_ticker(symbol=pair)['priceChange']), 4)
        return round(float(self.client.get_ticker(symbol=pair)['priceChange']), 2)

    def get_crypto_info(self):
        print("Crypto info has been requested...")
        assets = ["BTCUSDT", "ETHUSDT", "LTCUSDT", "XRPUSDT"]
        info = f'```diff\n+ Price is up over 24hrs\n- Price is down over 24hrs```\n'
        for asset in assets:
            current_price = self.get_asset_price(asset)
            price_change = abs(self.get_asset_24hr_price_change(asset))
            percent_change = round(abs(float(price_change / current_price)) * 100, 2)
            if price_change < 0:
                info += f'**{asset}**\n```diff\n- Price: ${self.get_asset_price(asset)}\n- 24hr Change: ${price_change}\n- Percent Change: %{percent_change}```\n`'
            else:
                info += f'**{asset}**\n```diff\n+ Price: ${self.get_asset_price(asset)}\n+ 24hr Change: ${price_change}\n+ Percent Change: %{percent_change}```\n'
        return info

    @staticmethod
    def place_value(number):
        return "{:,.2f}".format(number).replace('-', '')
