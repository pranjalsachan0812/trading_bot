import logging
from binance.client import Client
from binance.enums import *
import getpass

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True):
        self.client = Client(api_key, api_secret)
        if testnet:
            self.client.API_URL = 'https://testnet.binancefuture.com/fapi'
        self.logger = logging.getLogger('BasicBot')
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler('bot.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        side = side.upper()
        order_type = order_type.upper()
        try:
            if order_type == "MARKET":
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=SIDE_BUY if side == "BUY" else SIDE_SELL,
                    type=ORDER_TYPE_MARKET,
                    quantity=quantity)
            elif order_type == "LIMIT":
                if price is None:
                    raise ValueError("Price must be specified for LIMIT order")
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=SIDE_BUY if side == "BUY" else SIDE_SELL,
                    type=ORDER_TYPE_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=quantity,
                    price=str(price))
            elif order_type == "STOP_LIMIT":
                if price is None or stop_price is None:
                    raise ValueError("Price and stop price must be specified for STOP_LIMIT order")
                order = self.client.futures_create_order(
                    symbol=symbol,
                    side=SIDE_BUY if side == "BUY" else SIDE_SELL,
                    type=ORDER_TYPE_STOP_LOSS_LIMIT,
                    timeInForce=TIME_IN_FORCE_GTC,
                    quantity=quantity,
                    price=str(price),
                    stopPrice=str(stop_price))
            else:
                self.logger.error(f"Unsupported order type: {order_type}")
                print(f"Unsupported order type: {order_type}")
                return None

            self.logger.info(f"Order placed successfully: {order}")
            print(f"Order details:\n{order}")
            return order

        except Exception as e:
            self.logger.error(f"Error placing order: {e}")
            print(f"Error placing order: {e}")
            return None


def validate_input(prompt, valid_options=None, input_type=str, optional=False):
    while True:
        user_input = input(prompt).strip()
        if optional and user_input == '':
            return None
        try:
            value = input_type(user_input)
            if valid_options and value.upper() not in valid_options:
                print(f"Invalid input. Choose from {valid_options}")
                continue
            return value
        except ValueError:
            print(f"Invalid input type. Please enter a valid {input_type.__name__}.")


def main():
    print("=== Binance Futures Testnet Trading Bot ===")
    api_key = input("Enter your API Key: ")
    api_secret = getpass.getpass("Enter your API Secret: ")

    bot = BasicBot(api_key, api_secret, testnet=True)

    while True:
        symbol = input("Enter symbol (e.g., BTCUSDT): ").upper()
        side = validate_input("Enter side (BUY/SELL): ", valid_options=["BUY", "SELL"], input_type=str).upper()
        order_type = validate_input("Enter order type (MARKET, LIMIT, STOP_LIMIT): ",
                                    valid_options=["MARKET", "LIMIT", "STOP_LIMIT"], input_type=str).upper()
        quantity = validate_input("Enter quantity: ", input_type=float)
        price = None
        stop_price = None

        if order_type == "LIMIT":
            price = validate_input("Enter limit price: ", input_type=float)
        elif order_type == "STOP_LIMIT":
            stop_price = validate_input("Enter stop price: ", input_type=float)
            price = validate_input("Enter limit price: ", input_type=float)

        order = bot.place_order(symbol, side, order_type, quantity, price, stop_price)

        cont = input("Place another order? (yes/no): ").strip().lower()
        if cont != 'yes':
            print("Exiting trading bot.")
            break


if __name__ == "__main__":
    main()
