from flask import Flask, jsonify
from flask_caching import Cache
import time
import requests
import json
import numpy as np
import talib

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/macd')
def get_macd_data():
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

            close_prices = [float(item[4]) for item in data]
            close_prices_np = np.array(close_prices)

            macd, macdsignal, _ = talib.MACD(close_prices_np)

            previous_macd, previous_macdsignal = macd[-2], macdsignal[-2]
            current_macd, current_macdsignal = macd[-1], macdsignal[-1]

            if previous_macd < previous_macdsignal and current_macd > current_macdsignal:
                signal = 'BUY'
            elif previous_macd > previous_macdsignal and current_macd < current_macdsignal:
                signal = 'SELL'
            else:
                signal = ''

            timestamp = int(time.time() * 1000)

            if signal:
                if symbol not in result:
                    result[symbol] = []
                result[symbol].append({
                    'coin': symbol,
                    'cross': signal,
                    'macd': current_macd,
                    'macdsignal': current_macdsignal,
                    'date': timestamp,
                    'interval': interval
                })

    cache.set('macd_data', result, timeout=3600)
    return jsonify(result)

@app.route('/macd/<string:interval>')
def get_macd_interval(interval):
    data = cache.get('macd_data')
    if data is None:
        return jsonify({'error': 'MACD data not available'})

    result = {symbol: [entry for entry in data[symbol] if entry['interval'] == interval] for symbol in data}
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
