import requests
import pandas as pd
import numpy as np
import json

# API Keys
COINMARKETCAP_API_KEY = "07a86387-ea6f-40f9-b81e-03261c529152"
LUNARCRUSH_API_KEY = "vrhi6fbieidevfpq5wqboxy6hhm4a429mk6b4t6qx"
CRYPTOCOMPARE_API_KEY = "e66a3793b0b278c054bd5fc67f20cea64c32d66206ed63400112e189c34f8166"
ALPHA_VANTAGE_API_KEY = "VJKPIK7L2NTUKR9V"

# KuCoin Endpoint
KUCOIN_API_URL = "https://api.kucoin.com/api/v1/market/allTickers"

# 1. Fetch data from KuCoin
def fetch_kucoin_data():
    try:
        response = requests.get(KUCOIN_API_URL)
        response.raise_for_status()
        tickers = response.json()['data']['ticker']
        df = pd.DataFrame(tickers)
        df = df[['symbol', 'last', 'vol', 'changeRate']]
        df['last'] = df['last'].astype(float)
        df['vol'] = df['vol'].astype(float)
        df['percent_change_24h'] = df['changeRate'].astype(float) * 100  # Convert to percentage
        df.rename(columns={'last': 'price', 'vol': 'volume_24h'}, inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching KuCoin data: {e}")
        return pd.DataFrame()

# 2. Fetch data from CoinMarketCap
def fetch_coinmarketcap_data():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {"X-CMC_PRO_API_KEY": COINMARKETCAP_API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()['data']
        df = pd.DataFrame(data)
        df = df[['symbol', 'quote']]
        df['price'] = df['quote'].apply(lambda x: x['USD']['price'])
        df['volume_24h'] = df['quote'].apply(lambda x: x['USD']['volume_24h'])
        df['percent_change_24h'] = df['quote'].apply(lambda x: x['USD']['percent_change_24h'])
        return df
    except Exception as e:
        print(f"Error fetching CoinMarketCap data: {e}")
        return pd.DataFrame()

# 3. Fetch data from CoinGecko
def fetch_coingecko_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 50,
        "page": 1,
        "sparkline": False
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data)
        df = df[['symbol', 'current_price', 'total_volume', 'price_change_percentage_24h']]
        df.rename(columns={
            'current_price': 'price',
            'total_volume': 'volume_24h',
            'price_change_percentage_24h': 'percent_change_24h'
        }, inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching CoinGecko data: {e}")
        return pd.DataFrame()

# 4. Fetch data from LunarCrush
def fetch_lunarcrush_data():
    url = "https://api.lunarcrush.com/v2/assets"
    params = {
        "data": "assets",
        "key": LUNARCRUSH_API_KEY,
        "sort": "galaxy_score",
        "limit": 50
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()['data']
        df = pd.DataFrame(data)
        df = df[['symbol', 'galaxy_score', 'alt_rank', 'social_volume', 'social_score']]
        return df
    except Exception as e:
        print(f"Error fetching LunarCrush data: {e}")
        return pd.DataFrame()

# 5. Combine and rank tokens by potential gainers
def rank_gainers(data_sources):
    try:
        combined_data = pd.DataFrame()

        # Merge all data sources on 'symbol'
        for source in data_sources:
            if not source.empty:
                combined_data = source if combined_data.empty else pd.merge(combined_data, source, on='symbol', how='outer')

        # Fill missing columns with default values
        for column in ['price', 'volume_24h', 'percent_change_24h', 'galaxy_score']:
            if column not in combined_data.columns:
                combined_data[column] = np.nan

        # Fill NaNs for combined data
        combined_data.fillna(0, inplace=True)

        # Sort by percent_change_24h
        combined_data.sort_values(by='percent_change_24h', ascending=False, inplace=True)

        # Add reasoning column
        combined_data['reason'] = combined_data.apply(
            lambda row: f"Social activity: {row.get('social_score', 'N/A')}, Price Change: {row['percent_change_24h']}%",
            axis=1
        )

        # Return top gainers
        return combined_data[['symbol', 'price', 'percent_change_24h', 'volume_24h', 'galaxy_score', 'reason']].head(10)
    except Exception as e:
        print(f"Error during ranking: {e}")
        return pd.DataFrame()

# Main function
if __name__ == "__main__":
    kucoin_data = fetch_kucoin_data()
    cmc_data = fetch_coinmarketcap_data()
    coingecko_data = fetch_coingecko_data()
    lunar_data = fetch_lunarcrush_data()

    # Collect all data sources
    data_sources = [kucoin_data, cmc_data, coingecko_data, lunar_data]

    predictions = rank_gainers(data_sources)

    if not predictions.empty:
        predictions_json = predictions.to_dict(orient="records")
        # Write ONLY the JSON data to predictions.json
        with open("predictions.json", "w") as f:
            json.dump(predictions_json, f, indent=4)
        print("Predictions saved to predictions.json")
    else:
        print("No data available to calculate predictions.")
