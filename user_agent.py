import re
import decimal

#0v1# JC  June  6, 2018  Initial setup

def remove_exponent(value):
    """
       >>>(Decimal('5E+3'))
       Decimal('5000.00000000')
    """
    decimal_places = 8
    max_digits = 16

    if isinstance(value, decimal.Decimal):
        context = decimal.getcontext().copy()
        context.prec = max_digits
        return "{0:f}".format(value.quantize(decimal.Decimal(".1") ** decimal_places, context=context))
    else:
        return "%.*f" % (decimal_places, value)

class Trade_Logger(object):
    #>watch atomic writes

    def __init__(self):
        self.filename='trade_logs.tsv'
        return
    
    def note_trade(self,tdict):
        #required
        ii=['order_time','fill_time','ticker','side','quantity','price','fill_price','buy_position','sell_position']
        
        #Adjust datetimes to strings
        tdict['order_time']=str(tdict['order_time'])
        tdict['fill_time']=str(tdict['fill_time'])
        
        #Adjust exponential floats to floats
        tdict['price']=remove_exponent(tdict['price'])
        tdict['fill_price']=remove_exponent(tdict['fill_price'])

        
        stats=[]
        for key in ii:
            stats+=[str(tdict[key])]

        try: fp=open(self.filename,'a')
        except: fp=open(self.filename,'w')
        liner="\t".join(stats)
        fp.write(liner+"\n")
        fp.close()
        return
    
    def close(self):
        #fp.close() above but highlights need for atomic writes
        return

class Agent(object):
    def __init__(self,ticker='',buy_position=0,sell_position=0,agent_name=''):
        self.agent_name=agent_name
        self.buy_position=buy_position
        self.sell_position=sell_position
        self.ticker=ticker
        self.open_buys={} #true if opened
        self.open_sells={}
        return
    
    def note_resolved_order(self,closed_id,closed_orders):
        #>optionally clean info out of closed once noted
        
        order=closed_orders[closed_id] #Hard fail good

        #Review attributes
        if False:
            ticker=order['ticker']
            quantity=order['quantity']
    
            BUY_or_SELL=order['side']
            order_price=order['price']
            fill_price=order['fill_price']
    
            order_time=order['order_time']
            fill_time=order['fill_time']
        

        #Pass local agent details to order dictionary (as it's not tracked on Exchange side ie/ sell_position)
        ###########################
        order['buy_position']=self.buy_position
        order['sell_position']=self.sell_position
        
        TL=Trade_Logger()
        TL.note_trade(order)
        TL.close()
        
        return
    
    def get_actions(self,open_orders,closed_orders):
        actions=[]
        #/ Initialize with double buys
        if not self.open_buys and not self.open_sells:
            #ASSUME BEGIN WITH NO OPENED ORDERS
            actions+=['PLACE_BID']
            actions+=['PLACE_SELL']
        else:
            #/ Set local variable state
            for id in self.open_buys:
                if self.open_buys[id]: #Then thinks opened
                    if not id in open_orders: #Then order closed
                        self.open_buys[id]=False
                        self.note_resolved_order(id, closed_orders)
                        actions+=['PLACE_BID']
                        print("PLacing bid because this not found: "+str(id)+" in opened: "+str(open_orders))
            for id in self.open_sells:
                if self.open_sells[id]: #Then thinks opened
                    if not id in open_orders: #Then order closed
                        self.open_sells[id]=False
                        self.note_resolved_order(id, closed_orders)
                        actions+=['PLACE_SELL']
        return actions
    
    def fetch_order_creation_details(self,actions):
        order_details=[]
        for action in actions:
            if action=='PLACE_BID':
                order_details+=[(self.ticker,'buy',self.buy_position)]
            if action=='PLACE_SELL':
                order_details+=[(self.ticker,'sell',self.sell_position)]
        return order_details
    
    def note_orders_placed(self,new_buys,new_sells):
        for id in new_buys:
            self.open_buys[id]=True
        for id in new_sells:
            self.open_sells[id]=True
        return
    
    def print_report(self):
        for id in self.open_buys:
            if self.open_buys[id]:
                pass
                #print (self.agent_name+" open buy id: "+str(id))
        for id in self.open_sells:
            if self.open_sells[id]:
                pass
                #print (self.agent_name+" open sell id: "+str(id))
        return
    
    
    
if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        




