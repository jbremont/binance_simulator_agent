import sys,os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), "."))
from binance_interface import Binance_Interface
from order_book import Order_Book


GLOBAL_TICKER='FUELETH'

class Binance_Exchange_Simulator(object):
    #Recall, can import either (similar to tk)
    #>do as exercise and document in coding templates
    def __init__(self):
        return

class Binance_Export(Binance_Interface):
    def __init__(self):
        mode='dev'
        super(Binance_Export,self).__init__(mode=mode)
        self.OBook=Order_Book(BI=self,auto_start=False)
        return
    
    def initialize(self,ticker=''):
        if ticker:
            
            # ORDER BOOK
            self.OBook.start_depth_cache(ticker=ticker)
            
            # For depth, price, deltas: see data_logging.py classes

        return
    
def dev1():
    global GLOBAL_TICKER
    symbol=GLOBAL_TICKER

    BI=Binance_Export()

    BI.test_connection()
    
    print ("/test MM required")
    BI.set_symbol(symbol)
    symbol=BI.get_symbol()
    print ("[x] active symbol: "+symbol)
    
    
    ##
    print ("/test websockets")
    #DIRECT#  BI.start_websocket_ticker(symbol)
    BI.initialize(ticker=symbol)
    
    ##

    
    
    
    time.sleep(5)
    BI.shutdown()  #Shutdown 4 websocket
    print ("Done binance export test")
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()




