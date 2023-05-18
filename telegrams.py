

import logging
import time
import talib
import requests
import numpy as np
from telegram.ext import Updater, CallbackContext

# Telegram botunun günlük kayıtlarını tutmak için loglama ayarları
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)

# Botun anlık olarak coin bilgilerini kontrol ettiği fonksiyon
def check_coin(context: CallbackContext):
    # ETHTRY için anlık fiyatı alma
    response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=ETHTRY")
    data = response.json()
    current_price = float(data['price'])

    # Son 26 gün için ETHTRY fiyat verilerini alma
    response = requests.get("https://api.binance.com/api/v3/klines?symbol=ETHTRY&interval=1d&limit=26")
    data = response.json()
    close_prices = np.array([float(entry[4]) for entry in data])

    # MACD hesaplama
    macd, macd_signal, _ = talib.MACD(close_prices)

    # MACD histogramını kontrol etme
    last_macd_histogram = macd[-2] - macd_signal[-2]
    current_macd_histogram = macd[-1] - macd_signal[-1]

    # Alım, satım veya bekle mesajı oluşturma
    message = ""
    if last_macd_histogram < 0 and current_macd_histogram > 0:
        message = f"ALIM: ETHTRY - Fiyat: {current_price}"
    elif last_macd_histogram > 0 and current_macd_histogram < 0:
        message = f"SATIM: ETHTRY - Fiyat: {current_price}"
    else:
        message = "BEKLE: ETHTRY"

    # Mesajı gönderin
    context.bot.send_message(chat_id='804636818', text=message)

def main():
    # Telegram botunun tokenini girin
    updater = Updater(token='6247116301:AAFShT7Nk9yn-Hm5AfbPYPAO7EMDBV5TYOY', use_context=True)
    dispatcher = updater.dispatcher

    # Botun coin kontrol fonksiyonunu çalıştırması için bir handler ekleyin
    job_queue = updater.job_queue
    job_queue.run_repeating(check_coin, interval=300, first=0)

    # Botu çalıştırın
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
