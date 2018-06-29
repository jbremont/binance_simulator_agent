import re
import time
import datetime
from binance_interface_new import Binance_Interface_New
from order_book import Order_Book

#0v1# JC  June  6, 2018  Initial setup

BI=Binance_Interface_New() #auto connects


class A_Signal_Set(object):
    #A signal set
    def __init__(self,ticker):
        self.ticker=ticker
        return
    
    def connect_websockets(self):
        print ("Connecting to order book for: "+self.ticker)
        self.OB=Order_Book(BI=BI,ticker=self.ticker)
        self.OB.print_spread()
        self.test_order_get()
        return
    
    def test_order_get(self):
        print ("Bid at 20: "+str(self.OB.get_order_at('bid',20)))
        #price,size
        return
    
    ####################/  Access
    def get_bid_at(self,position):
        price,size=self.OB.get_order_at('bid',position)
        return price

    def get_sell_at(self,position):
        price,size=self.OB.get_order_at('sell',position)
        return price
    
    def disconnect(self):
        self.OB.shutdown()
        return


class The_Signals(object):
    def __init__(self):
        self.signals=[]
        self.active_time=''
        return
    
    def auto_refresh_if_needed(self):
        REFRESH_EVERY=20*60*60 #seconds
        seconds_running=datetime.datetime.now()-self.active_time
        if seconds_running>REFRESH_EVERY:
            print ("[AUTO REFRESH WEBSOCKETS!]")
            print ('[debug] stopping all websocket order books...')
            self.end_websockets()
            print ('[debug] Starting all websocket order books...')
            self.start_websockets()
            print ('[debug] refresh done')
        return
    
    def connect(self):
        print ("Connecting to binance exchange...")
        return
    
    def register_tickers(self,tickers):
        self.ticker_list=tickers
        for ticker in self.ticker_list:
            self.signals+=[A_Signal_Set(ticker)]
        return
    
    def start_websockets(self):
        for Signal in self.signals:
            Signal.connect_websockets()
        self.active_time=datetime.datetime.now()
        return
    def end_websockets(self):
        for Signal in self.signals:
            Signal.disconnect()
        return
    
    
    def get_ticker_orderbook_price(self,gticker,position,buy_sell):
        price=0
        found=False
        for Signal in self.signals:
            if gticker==Signal.ticker:
                if buy_sell=='buy':
                    price=Signal.get_bid_at(position)
                    found=True
                    break
                elif buy_sell=='sell':
                    price=Signal.get_sell_at(position)
                    found=True
                    break
                else:
                    print ("SETUP BAD REQUEST: "+str(buy_sell))
                    a=hard_fail
        if not found:
            print ("SETUP ERR COULD NOT FIND ORDERBOOK FOR: "+gticker)
            a=hard_fail
        return price
    
    def shutdown(self):
        for Signal in self.signals:
            Signal.shutdown()
        return


def dev_websockets():
    global BI

    #**NOTE:  Support for multiple pairs
    tickers=['BNBBTC']
    Signals=The_Signals()
    
    Signals.register_tickers(tickers)
    
    Signals.start_websockets()

    print ("Closing in 5...")
    time.sleep(5)
    print ("Done")
    BI.shutdown()
    return

if __name__=='__main__':
    branches=['dev_websockets']

    for b in branches:
        globals()[b]()




