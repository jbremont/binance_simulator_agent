import time
try:
    import ConfigParser #py2
except:
    import configparser as ConfigParser #py3

from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.enums import *

#0v2# JC  June 6, 2018  Extend to binance_interface_new
#0v1# JC  Apr 13, 2018  Initial setup


# LOAD CONFIG SETTINGS
############################################
Config = ConfigParser.ConfigParser()
Config.read("settings.ini")

API_KEY=Config.get('api', 'key')
API_SECRET=Config.get('api', 'secret')
    

class Binance_Interface(object):
    global API_KEY,API_SECRET

    def __init__(self,mode='dev'):
        self.verbose=True
        self.connect()
        self.symbol=''
        return
    
    def connect(self):
        self.client = Client(API_KEY, API_SECRET)
        self.bm = BinanceSocketManager(self.client)
        return
    
    def test_connection(self):
        #pdf api
        self.client.ping()
        self.client.get_server_time()
        self.client.get_system_status()
        self.client.get_exchange_info()
        return
    
    
    #####################
    # Friendly interface
    #####################
    def set_symbol(self,symbol):
        self.symbol=symbol
        return
    def get_symbol(self):
        return self.symbol
    
    
    
    def start_websocket_ticker(self,ticker):
        print ("dev only, use Order book and other price wraps")
        self.bm.start_aggtrade_socket(ticker, self.process_message)
        self.bm.start()
        return
    def test_websocket(self):
        #See pdf api
        ticker='BNBBTC'
        print ("test> Starting websocket for: "+ticker)
        self.start_websocket_ticker(ticker)

        return
    
    def process_message(self,msg):
        print("message type: {}".format(msg['e']))
        print(msg)
        # do something
        return
    
    def shutdown(self):
        self.bm.close() #close all connections
        return
    
    def place_test_order(self,ticker='BNBBTC',quantity=100,price='0.00001'):
        #via pdf docs
        order = self.client.create_test_order(
        symbol=ticker,
        side=SIDE_BUY,
        type=ORDER_TYPE_LIMIT,
        timeInForce=TIME_IN_FORCE_GTC,
        quantity=quantity,
        price=price)
        return order
    
    def get_order(self,orderId):
        #order = client.get_order(
        #symbol='BNBBTC',
        #orderId='orderId')
        return self.client.get_order(orderId=orderId)
    
    def get_balance(self,ticker):
        #ACCOUNT balance = self.client.get_asset_balance(asset=ticker) #BTC
        #account = self.client.get_account()#asset=ticker) #BTC
        #, {u'locked': u'0.00000000', u'asset': u'CMT', u'free': u'6.99300000'},
        #{u'buyerCommission': 0, u'updateTime': 1524254161718L, u'canWithdraw': True, 
        #u'takerCommission': 10, u'canTrade': True, u'makerCommission': 10, 
        #u'balances': [{u'locked': u'0.00000000', u'asset': u'BTC', u'free': u'0.00000000'}, 
        #{u'locked': u'0.00000000', u'asset': u'ETH', u'free': u'0.04827219'},
        balance_locked=0
        balance_free=0

        for symbol,locked,free in self.iter_balances():#
            if ticker==symbol:
                balance_free=free
                break
        return balance_free
    
    def iter_balances(self):
        for asset in self.client.get_account()['balances']:
            yield asset['asset'],float(asset['locked']),float(asset['free'])
        return
    
    def iter_tickers(self):
        #Only include if balance
        for ticker,locked,free in self.iter_balances():
            if locked>0 or free>0:
                if not self.is_base(ticker):
                    print ("L: "+str(locked))
                    print ("L: "+str(free))
                    yield ticker
        return
    
    def is_base(self,given):
        if given.upper() in ['BTC','ETH']: return True
        return False
    
    def account_review(self):
        #orders = client.get_all_orders(symbol='BNBBTC', limit=10)
        #ALL trades = BI.client.get_historical_trades(symbol='BNBBTC')
        currency='ETH'
        total_daily_value=0
        for ticker in self.iter_tickers():
            symbol=ticker+currency
            trades = self.client.get_my_trades(symbol=symbol)
            for trade_object in trades:
                if False:
                    Order=Order_Object(order_object=trade_object)
                    if Order.age()<=24:
                        if Order.isBuyer:
                            the_value=Order.price*Order.qty
                            total_daily_value+=the_value
        return total_daily_value
    
    
    
    
def dev1():
    BI=Binance_Interface()
    
    b=['test_websocket']
    b=['test_connection']
    
    if 'test_websocket' in b:
        BI.test_websocket()
        time.sleep(5)
        BI.shutdown()

    if 'test_connection' in b:
        print ("Testing connection...")
        BI.test_connection()

    print ("<done dev1>")
    return

if __name__=='__main__':
    branches=['dev1']
    for b in branches:
        globals()[b]()




