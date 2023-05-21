import talib
import numpy as np
from binance.client import Client
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext




class Data:
    def __int__(self,interval,symbol,period):
        self.interval = interval
        self.symbol = symbol
        self.period = period

    def fetchData(self):
        pass

    def sendData(self,):
        pass
class Telegram:
    def __init__(self,TOKEN,CHAT_ID):
        self.token=TOKEN
        self.chat_id=CHAT_ID
        self.runBot(self.token)


    def runBot(self,token):
        updater=Updater(token=self.token)
        dispatcher=updater.dispatcher
        dispatcher.add_handler(CommandHandler('start',self.basla))
        updater.start_polling()
        updater.idle()

    def basla(self,update:Update,_:CallbackContext):
        update.message.reply_text('Merhaba')




if __name__=='__main__':
    token='6247116301:AAFShT7Nk9yn-Hm5AfbPYPAO7EMDBV5TYOY'
    chat_id='804636818'
    x=Telegram(token,chat_id)

