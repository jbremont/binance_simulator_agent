import re
from binance_interface_new import Binance_Interface_New

#0v1# JC  June  6, 2018  Initial setup

#> binance_interface is direct interface
#> see: order_manager.py for sample orders

#<see order_object.py for details>
#class Order_Object(object):
    #<orderId>: 8292808
    #<clientOrderId>: fTsDOWeJp59DwaPZjBnjNS
    #<symbol>: CMTETH
    #<timeInForce>: GTC
    #<price>: 0.00144180
    #<stopPrice>: 0.00000000
    #<origQty>: 7.00000000
    #<icebergQty>: 0.00000000
    #<isWorking>: True
    #<status>: FILLED
    #<executedQty>: 7.00000000
    #<time>: 1524254161718
    #<type>: LIMIT
    #<side>: BUY

class Trading_Desk(object):
    def __init__(self):
        self.BI=Binance_Interface_New() #auto connects
        self.open_orders={} #index by id
        return
    
    def cancel_all_orders(self):
        #[] for initialize
        print ("[cancel_all_orders]  []")
        return
    
    def refresh_order_status(self):
        return self.BI.SIM_refresh_order_status()
    
    def list_open_orders_SIM(self):
        #assume called externally#  self.refresh_order_status()
        return self.BI.list_open_orders_SIM()
    
    def trade_details_ref_SIM(self):
        return self.BI.closed_trade_details_SIM()
    
    def place_orders(self,orders_to_place):
        #>created in sim_master .create_orders
        new_buy_order_ids=[]
        new_sell_order_ids=[]
        for order in orders_to_place:
            if not order['action'] in ['buy','sell']:a=bad_setup

            if order['action']=='buy':
                order_object=self.order_create_limit_buy(order['ticker'], order['quantity'], order['price'])
                orderId=order_object['orderId']
                new_buy_order_ids+=[orderId]
            elif order['action']=='sell':
                order_object=self.order_create_limit_sell(order['ticker'], order['quantity'], order['price'])
                orderId=order_object['orderId']
                new_sell_order_ids+=[orderId]
            else:a=hard_fail
            
            #Note activity
            self.open_orders[orderId]=True
        return new_buy_order_ids,new_sell_order_ids
    
    def shutdown(self):
        self.BI.shutdown()
        return
    
    def order_create_limit_sell(self,symbol,quantity,price):
        #<via order_manager.py>
        order_object={}
        order_object = self.BI.place_test_order(ticker=symbol, quantity=quantity, price=price,side='SELL')
        #Order=Order_Object(order_object=order_object)
        return order_object

    def order_create_limit_buy(self,symbol,quantity,price):
        order_object = self.BI.place_test_order(ticker=symbol, quantity=quantity, price=price,side='BUY')
        return order_object
    

    #############################################
    # via order_manager.py
    #############################################
    #

    ## ORDERS
    #########
    # https://github.com/sammchardy/python-binance/blob/master/docs/account.rst
    
    #>order_create_limit_sell / buy
    #>order_status
    #>order_cancel
    #>get_symbol_info
    #>validate trade
    #
    
    def get_open_orders(self,ticker,verbose=True):
        a=see_sim
        orders=[]
        for oo in self.BI.client.get_open_orders(symbol=ticker):
            Order=Order_Object(order_object=oo)
            orders+=[Order]
            if verbose:
                print ("[open order] "+str(ticker)+": "+str(Order))
        return orders
    
    
def dev1():
    Desk=Trading_Desk()
    Desk.BI.test_connection()
    Desk.BI.account_review()
    
    print ("DONE test trading desk")
    return

if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()




