from flask import Flask, jsonify
from flask_caching import Cache
import time
import requests
import json
import numpy as np
import talib

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/parabolic_sar')
def get_parabolic_sar_data():
    symbols = ["ETHUSDT", "BTCUSDT", "BNBUSDT", "RSRUSDT", "LUNAUSDT", "BUSDUSDT", "SHIBUSDT", "CHZUSDT", "ADAUSDT", "SUNUSDT", "LITUSDT", "ATOMUSDT", "XRPUSDT"]
    intervals = ['15m', '30m', '1h', '4h', '1d']
    limit = 102
    result = {}

    for symbol in symbols:
        for interval in intervals:
            response = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}")
            if response.status_code != 200:
                continue

            data = response.json()

            close_prices = np.array([float(item[4]) for item in data])
            high_prices = np.array([float(item[2]) for item in data])
            low_prices = np.array([float(item[3]) for item in data])

            # Calculate Parabolic SAR
            sar = talib.SAR(high_prices, low_prices, acceleration=0.02, maximum=0.2)

            current_sar = sar[-1]
            previous_sar = sar[-2]

            # Generate signal
            signal = ''
            if previous_sar < close_prices[-2] and current_sar > close_prices[-1]:
                signal = 'BUY'
            elif previous_sar > close_prices[-2] and current_sar < close_prices[-1]:
                signal = 'SELL'

            timestamp = int(time.time() * 1000)

            if signal:
                if symbol not in result:
                    result[symbol] = []
                result[symbol].append({
                    'coin': symbol,
                    'sar': current_sar,
                    'signal': signal,
                    'date': timestamp,
                    'interval': interval
                })

    cache.set('parabolic_sar_data', result, timeout=3600)
    return jsonify(result)

@app.route('/parabolic_sar/<string:interval>')
def get_parabolic_sar_interval(interval):
    data = cache.get('parabolic_sar_data')
    if data is None:
        return jsonify({'error': 'Parabolic SAR data not available'})

    result = {symbol: [entry for entry in data[symbol] if entry['interval'] == interval] for symbol in data}
    result = {k: v for k, v in result.items() if v}  # Remove empty entries
    cache.set('parabolic_sar_data_interval', result, timeout=3600)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
