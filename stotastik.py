from flask import Flask, jsonify
from flask_caching import Cache
import time
import requests
import json
import numpy as np
import talib

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/stoch')
def get_stoch_data():
    symbols = ["ETHUSDT", "BTCUSDT", "BNBUSDT", "RSRUSDT", "LUNAUSDT", "BUSDUSDT", "SHIBUSDT", "CHZUSDT", "ADAUSDT", "SUNUSDT", "LITUSDT", "ATOMUSDT", "XRPUSDT"]
    intervals = ['15m', '30m', '1h', '4h', '1d']
    limit = 101
    result = {}

    for symbol in symbols:
        for interval in intervals:
            response = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}")
            if response.status_code != 200:
                continue

            data = response.json()

            high_prices = [float(item[2]) for item in data]
            low_prices = [float(item[3]) for item in data]
            close_prices = [float(item[4]) for item in data]

            high_prices_np = np.array(high_prices)
            low_prices_np = np.array(low_prices)
            close_prices_np = np.array(close_prices)

            slowk, slowd = talib.STOCH(high_prices_np, low_prices_np, close_prices_np)

            previous_slowk, previous_slowd = slowk[-2], slowd[-2]
            current_slowk, current_slowd = slowk[-1], slowd[-1]

            if previous_slowk > previous_slowd and current_slowk < current_slowd and current_slowk>80:
                signal = 'SELL'
            elif previous_slowk < previous_slowd and current_slowk > current_slowd and current_slowk<20:
                signal = 'BUY'
            else:
                signal = ''

            timestamp = int(time.time() * 1000)

            if signal:
                if symbol not in result:
                    result[symbol] = []
                result[symbol].append({
                    'coin': symbol,
                    'cross': signal,
                    'slowk': current_slowk,
                    'slowd': current_slowd,
                    'date': timestamp,
                    'interval': interval
                })

    result = {k: v for k, v in result.items() if v}  # Remove empty entries
    cache.set('stoch_data', result, timeout=3600)
    return jsonify(result)


@app.route('/stoch/<string:interval>')
def get_stoch_interval(interval):
    data = cache.get('stoch_data')
    if data is None:
        return jsonify({'error': 'Stochastic data not available'})

    result = {symbol: [entry for entry in data[symbol] if entry['interval'] == interval] for symbol in data}
    result = {k: v for k, v in result.items() if v}  # Remove empty entries
    cache.set('stoch_data_interval', result, timeout=3600)
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
