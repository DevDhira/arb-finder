import os
import time
import pandas as pd
from binance.client import Client

# Set up Binance client (use your own API key and secret)
api_key = 'Binance Api Key'
api_secret = 'Binance Secret'
client = Client(api_key, api_secret)

# Function to get the current price for a trading pair
def get_price(symbol):
    ticker = client.get_ticker(symbol=symbol)
    return float(ticker['lastPrice'])

# Function to calculate percentage difference
def calc_percentage_difference(price1, price2):
    return (abs(price1 - price2) / ((price1 + price2) / 2)) * 100

# Function to get low-priced coins with adjustable volume filter
#def get_low_priced_high_volume_coins(limit_price=1.0, min_volume=1e6, investment_amount=100):
def get_low_priced_high_volume_coins(min_volume, investment_amount):
    coins_data = []
    tickers = client.get_ticker()
    limit_price=1.0 
    # Get the current BTC/USDT price to convert BTC pair prices to USD
    btc_usdt_price = get_price('BTCUSDT')

    # Filter coins based on price and volume
    for ticker in tickers:
        symbol = ticker['symbol']
        if symbol.endswith('USDT'):
            price_usdt = float(ticker['lastPrice'])
            volume = float(ticker['quoteVolume'])

            # Check if price is below the limit and volume is greater than the threshold
            if price_usdt < limit_price and volume > min_volume:
                coin = symbol.replace('USDT', '')

                # Get price for BTC pair and convert to USD
                try:
                    price_btc = get_price(f'{coin}BTC')
                    price_btc_usd = price_btc * btc_usdt_price  # Convert BTC pair price to USD
                except:
                    price_btc_usd = None

                # Calculate percentage difference and potential profit
                if price_btc_usd:
                    price_diff = calc_percentage_difference(price_btc_usd, price_usdt)
                    
                    # Calculate potential profit based on lower buying price and higher selling price
                    lower_price = min(price_btc_usd, price_usdt)
                    higher_price = max(price_btc_usd, price_usdt)
                    profit = investment_amount * ((higher_price - lower_price) / lower_price)
                    
                    coins_data.append({
                        'Coin': coin,
                        'BTC Pair Price (USD)': price_btc_usd,
                        'USDT Pair Price': price_usdt,
                        'Price Difference (%)': price_diff,
                        'Potential Profit ($)': profit,
                        'Volume (USDT)': volume
                    })

    return coins_data

# Function to display data in a formatted table
def display_table(coins_data):
    df = pd.DataFrame(coins_data)
    
    # Sort by 'Price Difference (%)' in descending order and select top 10
    df = df.sort_values(by='Price Difference (%)', ascending=False).head(15)

    # Formatting for centering text
    print(f"{'Coin':^12} {'BTC Pair Price (USD)':^22} {'USDT Pair Price':^18} {'Price Difference (%)':^22} {'Potential Profit ($)':^22} {'Volume (USDT)':^18}")
    print("=" * 112)

    # Center values
    for _, row in df.iterrows():
        print(f"{row['Coin']:^12} {row['BTC Pair Price (USD)']:^22.4f} {row['USDT Pair Price']:^18.4f} {row['Price Difference (%)']:^22.4f} {row['Potential Profit ($)']:^22.4f} {row['Volume (USDT)']:^18.4f}")

# Main loop to update table every 30 seconds
while True:
    # min_volume = float(input("Enter minimum volume (e.g., 1e6 for 1 million): "))  # Adjust volume
    # investment_amount = float(input("Enter investment amount in USD (e.g., 100): "))  # Adjust investment

    min_volume = 1e6
    investment_amount = 15

    # Get the current BTC/USDT price
    btc_usdt_price = get_price('BTCUSDT')

    print(f"Fetching data for coins priced below $1, volume greater than {min_volume}, and top 10 price differences...\n")
    
    # Display the current BTC/USDT price in USD format
    print(f"Current BTC/USDT price: ${btc_usdt_price:,.2f} USD\n")

    # Fetch and display data
    coins_data = get_low_priced_high_volume_coins(min_volume=min_volume, investment_amount=investment_amount)
    if coins_data:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen before displaying updated data
        display_table(coins_data)
    else:
        print("No coins meet the criteria at this moment.")

    # Wait for 30 seconds before updating
    time.sleep(10)