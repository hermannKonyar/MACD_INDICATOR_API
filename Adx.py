from flask import Flask, jsonify
from flask_caching import Cache
import time
import requests
import json
import numpy as np
import talib

app = Flask(__name__)

# Configuration for the first cache set (simple cache type)
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 3600
cache_simple = Cache(app)

# Configuration for the second cache set (memcached cache type)
app.config['CACHE_TYPE'] = 'memcached'
app.config['CACHE_MEMCACHED_SERVERS'] = ['127.0.0.1:11211']
app.config['CACHE_DEFAULT_TIMEOUT'] = 3600
cache_memcached = Cache(app)

@app.route('/macd')
def get_macd_data():
    symbols = ["ETHUSDT", "BTCUSDT", "BNBUSDT", "RSRUSDT", "LUNAUSDT", "BUSDUSDT", "SHIBUSDT", "CHZUSDT", "ADAUSDT", "SUNUSDT", "LITUSDT", "ATOMUSDT", "XRPUSDT"]
    intervals = ['15m', '30m', '1h', '4h', '1d']
    limit = 101
    result = {}  # Define an empty dictionary

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

    cache_simple.set('macd_data', result, timeout=3600)
    cache_memcached.set('macd_data', result, timeout=3600)
    return jsonify(result)

@app.route('/macd/<string:interval>')
def get_macd_interval(interval):
    data_simple = cache_simple.get('macd_data')
    data_memcached = cache_memcached.get('macd_data')

    if data_simple is None or data_memcached is None:
        return jsonify({'error': 'MACD data not available'})

    result_simple = {symbol: [entry for entry in data_simple[symbol] if entry['interval'] == interval] for symbol in data_simple}
    result_memcached = {symbol: [entry for entry in data_memcached[symbol] if entry['interval'] == interval] for symbol in data_memcached}

    cache_simple.set('macd_interval_data', result_simple, timeout=3600)
    cache_memcached.set('macd_interval_data', result_memcached, timeout=3600)

    return jsonify({'result_simple': result_simple, 'result_memcached': result_memcached})


if __name__ == '__main__':
    app.run(debug=True)
