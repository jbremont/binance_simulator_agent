import re
import uuid
import time
import datetime
from binance_interface import Binance_Interface

#0v3# JC  June 13, 2018  Extra logic to reconnect if connection drops
#0v2# JC  June  8, 2018  Simulate exchange
#0v2# JC  June  7, 2018  Use in trading_desk
#0v1# JC  June  6, 2018  Initial setup

class Simulate_Exchange(object):
    def __init__(self):
        self.open_orders={}
        self.closed_orders={}
        self.last_price={}
        return
    
    def _get_id(self):
        return str(uuid.uuid1())
    def _get_time(self):
        return datetime.datetime.now()

    def receive_orders(self,order):
        order_id=self._get_id()
        order['order_time']=self._get_time()
        self.open_orders[order_id]=order
        return order_id
    
    def note_market_price(self,ticker,current_price):
        self.last_price[ticker]=current_price

        ids_to_close=[]
        for oid in self.open_orders:
            odict=self.open_orders[oid]
            if ticker==odict['ticker']:
                if odict['side']=='BUY':
                    if current_price<odict['price']:
                        print ("[d1] want to buy at price: "+str(odict['price'])+" current price; "+str(current_price))
                        self.open_orders[oid]['fill_price']=current_price
                        self.open_orders[oid]['fill_time']=self._get_time()
                        ids_to_close+=[oid]
                elif odict['side']=='SELL':
                    if current_price>odict['price']:
                        print ("[d1] want to sell at price: "+str(odict['price'])+" current price; "+str(current_price))
                        self.open_orders[oid]['fill_price']=current_price
                        self.open_orders[oid]['fill_time']=self._get_time()
                        ids_to_close+=[oid]
                else:
                    bad=setupp

        #/POP order from open to closed
        for id in ids_to_close:
            print ("--order executed (closed)--> "+str(id))
            self.closed_orders[id]=self.open_orders.pop(id)
        return
    
    def list_open_orders(self):
        #refresh first?
#D#        print ("EXCHANGE OPEN ORDERS: "+str(self.open_orders.keys()))
        self.print_debug_orders()
        return self.open_orders.keys()
    
    def iter_opened_tickers(self):
        buf=[]
        for oid in self.open_orders:
            odict=self.open_orders[oid]
            if not odict['ticker'] in buf: #single
                buf+=[odict['ticker']]
        for ticker in buf:
            yield ticker
        return
    
    def closed_trade_details_SIM(self):
        #Return resolved closed trade details
        #price: is order open price
        #<watch> dictionary size
        return self.closed_orders
    
    def print_debug_orders(self):
        for id in self.open_orders:
            order=self.open_orders[id]
            print (order['ticker']+" @"+str(self.last_price[order['ticker']])+":: "+str(order)+"> "+str(id))
        return

class Binance_Interface_New(Binance_Interface):
    def __init__(self):
        super(Binance_Interface_New,self).__init__()
        self.Exchange=Simulate_Exchange()
        print ("[using simulated exchange]")

        return
    
    def place_test_order(self,ticker='BNBBTC',quantity=100,price='0.00001',side='BUY'):
        #https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#test-new-order-trade
        #**See enaums.py

        current_price=self.get_market_price(ticker)
        
        odict={}
        odict['ticker']=ticker
        odict['quantity']=quantity
        odict['price']=price
        odict['side']=side

        #########################
        # VALIDATE LOCAL LOGIC
        #########################
        if side=='SELL' and price<current_price:
            print ("WARNING SELL REQUEST PRICE: "+str(price)+" is less then current_price; "+str(current_price))
            a=hard_debug
        if side=='BUY' and price>current_price:
            print ("WARNING BUY REQUEST PRICE: "+str(price)+" is greater then current_price; "+str(current_price))
            a=hard_debug
        
        #########################
        # VALIDATE w/ EXCHANGE
        #########################
        #via pdf docs
        try:
            order = self.client.create_test_order(
            symbol=ticker,
            side=side,
            type='LIMIT', #ORDER_TYPE_LIMIT,
            timeInForce='GTC', #good till cancelled TIME_IN_FORCE_GTC,
            quantity=quantity,
            price=price)
        except Exception as e:
            print ("[warning] real exchange has issues with order: "+str(e))
        
        order_id=self.Exchange.receive_orders(odict)
        
        order_response={}
        order_response['orderId']=order_id
        
        #[] double refresh after buy as it updates order status
        current_price=self.get_market_price(ticker) 

        return order_response
    
    def get_market_price(self,ticker):
        #Pass market price to Exchange so it can simulate buy/sells
        #>  client.get_server_time(self):
        got_price=False
        while not got_price:
            try:
                print ("[d3] fetch price for: "+ticker)
                price_info=self.client.get_symbol_ticker(symbol=ticker)
                got_price=True
            except Exception as e:
                print ("Could not fetch price info: "+str(e))
                self.handle_http_error(e,'get_market_price',ticker)
                print ("[d3] done handling error")
                time.sleep(1)
        print ("[d3] got price for: "+ticker+": "+str(price_info))

        current_price=float(price_info['price'])
        self.Exchange.note_market_price(ticker,current_price)
        return current_price
    
    def list_open_orders_SIM(self):
        #?refresh first?
        return self.Exchange.list_open_orders()
    def closed_trade_details_SIM(self):
        return self.Exchange.closed_trade_details_SIM()
    
    def SIM_refresh_order_status(self):
        tickers=[]
        for ticker in self.Exchange.iter_opened_tickers():
            self.get_market_price(ticker) #auto updates per above
            tickers+=[ticker]
        return tickers
    
    def handle_http_error(self,exception,method,parameter):
        #** note: specific to failing method

        if '502 Bad Gateway' in exception:
            print ("[error] 502 Bad Gateway. Attempting to reconnect all services...")
            time.sleep(10)
        if 'Connection reset' in exception:
            print ("[error] Connection reset. Attempting to reconnect all services...")
            time.sleep(10)

        return

def dev1():
    BI=Binance_Interface_New()
    BI.test_connection()

    print ("Done dev1")
    return

if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()





















