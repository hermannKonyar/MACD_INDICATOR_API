from flask import Flask, jsonify
from flask_caching import Cache
import time
import requests
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
            url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
            response = requests.get(url)
            
            if response.status_code != 200:
                continue

            data = response.json()
            
            high_prices = np.array([float(item[2]) for item in data])
            low_prices = np.array([float(item[3]) for item in data])
            close_prices = np.array([float(item[4]) for item in data])

            slowk, slowd = talib.STOCH(high_prices, low_prices, close_prices, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
            
            previous_slowk, previous_slowd = slowk[-2], slowd[-2]
            current_slowk, current_slowd = slowk[-1], slowd[-1]

            if (previous_slowk < previous_slowd) and (current_slowk > current_slowd) and (current_slowd > 20) and (current_slowk < 20) and (abs(current_slowd-current_slowk)<4 or abs(current_slowk-current_slowd<4)):
                signal = 'BUY'
            elif (previous_slowk > previous_slowd) and (current_slowk < current_slowd) and (current_slowd > 80) and (current_slowk > 80) and (abs(current_slowd-current_slowk)<4 or abs(current_slowk-current_slowd<4)):
                signal = 'SELL'
            else:
                signal = ''

            timestamp = int(time.time() * 1000)

            if signal:
                if symbol not in result:
                    result[symbol] = []
                result[symbol].append({
                    'coin': symbol,
                    'signal': signal,
                    'slowk': current_slowk,
                    'slowd': current_slowd,
                    'date': timestamp,
                    'interval': interval
                })

    cache.set('stoch_data', result, timeout=500)
    return jsonify(result)

@app.route('/stoch/<string:interval>')
def get_stoch_interval(interval):
    data = cache.get('stoch_data')
    if data is None:
        return jsonify({'error': 'Stochastic Oscillator data not available'})

    result = {symbol: [entry for entry in data[symbol] if entry['interval'] == interval] for symbol in data}
    cache.set('stoch_data_interval', result, timeout=500)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
