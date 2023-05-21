import talib
import numpy as np
from binance.client import Client
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import threading

TELEGRAM_BOT_TOKEN = '6247116301:AAFShT7Nk9yn-Hm5AfbPYPAO7EMDBV5TYOY'  # Replace with your Telegram Bot Token
BINANCE_API_KEY = "wrfybb7xo2Cvze0Ii0zOO8FNkWIX4UCIWtBdONPZH7PD5nmP10pWVGDig9zFuffF"  # Replace with your Binance API Key
BINANCE_SECRET_KEY = "oPEp31iGEumVcl9NLcDTkwq3Q8F3A653ua2QYy33N1puebUsTbNdQo5gc8kP4UOR"  # Replace with your Binance Secret Key
TELEGRAM_CHAT_ID = '804636818'  # Replace with your Telegram Chat ID

client = Client(BINANCE_API_KEY, BINANCE_SECRET_KEY)
symbols = ["ETHTRY", "BTCTRY"]
def calculate_indicators(symbol, interval='30m', limit=500):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    
    high_prices = np.array([float(item[2]) for item in klines])
    low_prices = np.array([float(item[3]) for item in klines])
    close_prices = np.array([float(item[4]) for item in klines])

    macd, macdsignal, _ = talib.MACD(close_prices)
    slowk, slowd = talib.STOCH(high_prices, low_prices, close_prices, fastk_period=14)

    previous_macd, previous_macdsignal = macd[-2], macdsignal[-2]
    current_macd, current_macdsignal = macd[-1], macdsignal[-1]

    previous_slowk, previous_slowd = slowk[-2], slowd[-2]
    current_slowk, current_slowd = slowk[-1], slowd[-1]

    signal = None

    if previous_macd < previous_macdsignal and current_macd > current_macdsignal and current_slowk < 20 and previous_slowk < current_slowk:
        signal = 'BUY'
    elif previous_macd > previous_macdsignal and current_macd < current_macdsignal and current_slowk > 80 and previous_slowk > current_slowk:
        signal = 'SELL'

    return signal, current_macd, current_macdsignal, current_slowk, current_slowd



def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Bot started!')

def run_bot(context: CallbackContext):
    for symbol in symbols:
        signal, current_macd, current_macdsignal, current_slowk, current_slowd = calculate_indicators(symbol)
        if signal == 'BUY':
            context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"Buy signal for {symbol}. Current MACD: {current_macd}, MACD Signal: {current_macdsignal}, Stochastic K: {current_slowk}, Stochastic D: {current_slowd}")
        elif signal == 'SELL':
            context.bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=f"Sell signal for {symbol}. Current MACD: {current_macd}, MACD Signal: {current_macdsignal}, Stochastic K: {current_slowk}, Stochastic D: {current_slowd}")


def main():
    updater = Updater(token=TELEGRAM_BOT_TOKEN)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))

    updater.start_polling()

    job_queue = updater.job_queue
    job_queue.run_repeating(run_bot, interval=60)

    updater.idle()

if __name__ == '__main__':
    main()
