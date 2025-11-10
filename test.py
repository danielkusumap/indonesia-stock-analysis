import requests
import pandas as pd

def get_idx_top_gainers():
    """Get top gainers from IDX website (example)"""
    try:
        # This is a conceptual example - you'd need to find the actual API
        url = "https://www.idx.co.id/umbraco/Surface/TradingSummary/GetStockSummary"
        params = {
            'sort': 'PercentGain',
            'order': 'desc',
            'limit': 10
        }
        response = requests.get(url, params=params)
        data = response.json()
        return data
    except:
        return None

print(get_idx_top_gainers())