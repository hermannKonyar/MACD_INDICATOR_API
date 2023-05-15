from flask import Flask, jsonify
import time
import requests
import json
import numpy as np
import talib

app = Flask(__name__)
macd_data = None
last_calculated_time = None


def get_macd_data():
    global macd_data, last_calculated_time

    if macd_data is None or time.time() - last_calculated_time > 3600:  # every hour recalculate

        symbols = ["ETHUSDT", "BTCUSDT", "BNBUSDT", "RSRUSDT", "LUNAUSDT", "BUSDUSDT", "SHIBUSDT", "CHZUSDT", "ADAUSDT", "SUNUSDT", "LITUSDT", "ATOMUSDT", "XRPUSDT",]
        intervals = [ '15m', '30m',  '1h',  '4h', '1d']
        limit = 101
        result = {}

        for symbol in symbols:
            result[symbol] = {}
            for interval in intervals:
                response = requests.get(f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}")
                data = json.loads(response.text)

                close_prices = [float(item[4]) for item in data]
                close_prices_np = np.array(close_prices)

                # Calculate MACD and MACD Signal
                macd, macdsignal, _ = talib.MACD(close_prices_np)

                # Generate signals
                previous_macd, previous_macdsignal = macd[-2], macdsignal[-2]
                current_macd, current_macdsignal = macd[-1], macdsignal[-1]

                if previous_macd < previous_macdsignal and current_macd > current_macdsignal:
                    signal = 'BUY'
                elif previous_macd > previous_macdsignal and current_macd < current_macdsignal:
                    signal = 'SELL'
                else:
                    signal = ''

                timestamp = int(time.time() * 1000)

                # Only add to result if there is a cross signal
                if signal:
                    result[symbol][interval] = {
                        'coin': symbol,
                        'timeframe': interval,
                        'cross': signal,
                        'macd': current_macd,
                        'macdsignal': current_macdsignal,
                        'date': timestamp
                    }

        macd_data = result
        last_calculated_time = time.time()

    return macd_data

data=get_macd_data()

@app.route('/macd')
def getMacd():
    return jsonify({symbol : data[symbol] for symbol in data})

@app.route('/macd15m')
def getMacd15m():
    
    return jsonify({symbol: data[symbol]['15m'] for symbol in data if '15m' in data[symbol]})

@app.route('/macd30m')
def getMacd30m():
    
    return jsonify({symbol: data[symbol]['30m'] for symbol in data if '30m' in data[symbol]})

@app.route('/macd1h')
def getMacd1h():
   
    return jsonify({symbol: data[symbol]['1h'] for symbol in data if '1h' in data[symbol]})

@app.route('/macd4h')
def getMacd4h():
    
    return jsonify({symbol: data[symbol]['4h'] for symbol in data if '4h' in data[symbol]})

@app.route('/macd1d')
def getMacd1d():
    
    return jsonify({symbol: data[symbol]['1d'] for symbol in data if '1d' in data[symbol]})

if __name__ == '__main__':
    app.run(debug=True)
