from flask import Flask, jsonify
from flask_caching import Cache
import time
import requests
import json
import numpy as np
import talib

app = Flask(__name__)
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/stoch_rsi')
def get_stoch_rsi_data():
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

            # Calculate RSI
            rsi = talib.RSI(close_prices_np)

            # Calculate Stochastic RSI
            fastk, fastd = talib.STOCHRSI(rsi)
            current_fastk, current_fastd = fastk[-1], fastd[-1]

            # Generate signal
            signal = ''
            if current_fastk < 30:
                signal = 'BUY'
            elif current_fastk > 70:
                signal = 'SELL'
            else:
                continue

            timestamp = int(time.time() * 1000)

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

    cache.set('stoch_rsi_data', result, timeout=3600)
    return jsonify(result)

@app.route('/stoch_rsi/<string:interval>')
def get_stoch_rsi_interval(interval):
    data = cache.get('stoch_rsi_data')
    if data is None:
        return jsonify({'error': 'Stochastic RSI data not available'})

    result = {symbol: [entry for entry in data[symbol] if entry['interval'] == interval] for symbol in data}
    cache.set('stoch_rsi_data_interval', result, timeout=3600)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
