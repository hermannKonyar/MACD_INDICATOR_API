from flask import Flask, jsonify
import time
import requests
import numpy as np
import talib
import hmac
import hashlib
import json

app = Flask(__name__)


API_KEY = 'wrfybb7xo2Cvze0Ii0zOO8FNkWIX4UCIWtBdONPZH7PD5nmP10pWVGDig9zFuffF'
API_SECRET = 'oPEp31iGEumVcl9NLcDTkwq3Q8F3A653ua2QYy33N1puebUsTbNdQo5gc8kP4UOR'
BASE_URL = 'https://api.binance.com'

@app.route('/stoch_rsi')
def get_stoch_rsi_data():
    symbols = ["ETHUSDT", "BTCUSDT", "BNBUSDT", "RSRUSDT", "LUNAUSDT", "BUSDUSDT", "SHIBUSDT", "CHZUSDT", "ADAUSDT", "SUNUSDT", "LITUSDT", "ATOMUSDT", "XRPUSDT"]
    intervals = ['15m', '30m', '1h', '4h', '1d']
    limit = 102
    result = {}

    for symbol in symbols:
        for interval in intervals:
            endpoint = '/api/v3/klines'
            params = {
                'symbol': symbol,
                'interval': interval,
                'limit': limit
            }
            url = BASE_URL + endpoint
            response = send_signed_request(url, params)

            if response.status_code != 200:
                continue

            data = response.json()

            close_prices = np.array([float(item[4]) for item in data])

            # Calculate RSI
            rsi = talib.RSI(close_prices)

            # Drop the NaN values from the computed RSI
            rsi = rsi[~np.isnan(rsi)]

            # Calculate Stochastic RSI
            fastk, fastd = talib.STOCHRSI(rsi, timeperiod=14, fastk_period=5, fastd_period=3)
            current_fastk, current_fastd = fastk[-1], fastd[-1]
            previous_fastk, previous_fastd = fastk[-2], fastd[-2]

            # Generate signal
            signal = ''
            if previous_fastk < previous_fastd and current_fastk > current_fastd and current_fastk < 20 and (abs(current_fastk-current_fastd)<2 or abs(current_fastd-current_fastk)<2):
                signal = 'BUY'
            elif previous_fastk > previous_fastd and current_fastk < current_fastd and current_fastk > 80 and (abs(current_fastk-current_fastd)<2 or abs(current_fastd-current_fastk)<2):
                signal = 'SELL'

            timestamp = int(time.time() * 1000)

            if signal:
                if symbol not in result:
                    result[symbol] = []
                result[symbol].append({
                    'coin': symbol,
                    'fastk': current_fastk,
                    'fastd': current_fastd,
                    'signal': signal,
                    'date': timestamp,
                    'interval': interval
                })

    return jsonify(result)

def send_signed_request(url, params):
    timestamp = int(time.time() * 1000)
    query_string = '&'.join([f'{key}={params[key]}' for key in params])
    signature = hmac.new(API_SECRET.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()

    headers = {
        'X-MBX-APIKEY': API_KEY
    }

    url += f'?{query_string}&signature={signature}'

    response = requests.get(url, headers=headers)

    return response

if __name__ == '__main__':
    app.run(debug=True)
