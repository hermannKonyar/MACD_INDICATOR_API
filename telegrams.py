import time
import pandas as pd
import pandas_ta as ta
from binance.client import Client
from python_telegram_bot import telegram

binance_client = Client("wrfybb7xo2Cvze0Ii0zOO8FNkWIX4UCIWtBdONPZH7PD5nmP10pWVGDig9zFuffF", "oPEp31iGEumVcl9NLcDTkwq3Q8F3A653ua2QYy33N1puebUsTbNdQo5gc8kP4UOR")
bot = telegram.Bot(token="6247116301:AAFShT7Nk9yn-Hm5AfbPYPAO7EMDBV5TYOY")

def get_stoch(symbol, interval, k, d):
    klines = binance_client.get_klines(symbol=symbol, interval=interval)
    df = pd.DataFrame(klines, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore'])
    df = df.astype(float)
    stoch = ta.stoch(df['high'], df['low'], df['close'], k=k, d=d)
    return stoch

def send_signal(symbol, chat_id):
    try:
        stoch = get_stoch(symbol, "1m", 14, 3)
        if stoch.iloc[-1]['STOCHk_14_3_3'] > stoch.iloc[-1]['STOCHd_14_3_3']:
            bot.send_message(chat_id=chat_id, text=f"{symbol} Al")
        elif stoch.iloc[-1]['STOCHk_14_3_3'] < stoch.iloc[-1]['STOCHd_14_3_3']:
            bot.send_message(chat_id=chat_id, text=f"{symbol} Sat")
    except Exception as e:
        bot.send_message(chat_id=chat_id, text=f"Error occurred: {e}")

if __name__ == "__main__":
    while True:
        send_signal("ETHTRY", "804636818")
        send_signal("BTCTRY", "804636818")
        time.sleep(60)  # 1 dakika boyunca uyut
