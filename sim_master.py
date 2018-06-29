import re

from user_agent import Agent

#0v1# JC  June  6, 2018  Initial setup

class Sim_Master(object):
    def __init__(self):
        self.agents=[]
        return
    
    def initialize_agents(self,tickers):
        #Strategy
        agent_c=0
        ss=[]
#            ss+=[('BNBTC',20,20)]
        for ticker in tickers:
            ss+=[(ticker,20,20)]
            ss+=[(ticker,20,40)]
        
        for ticker,buy_position,sell_position in ss:
            agent_c+=1
            agent_name="Agent_"+str(agent_c)
            self.agents+=[Agent(ticker=ticker,buy_position=buy_position,sell_position=sell_position,agent_name=agent_name)]

        return
    
    def create_orders(self,Signals,order_details,default_quantity=100):
        orders_to_place=[]
        for ticker,bs,book_position in order_details:
            order={}
            order['action']=bs
            order['ticker']=ticker
            order['quantity']=default_quantity
            order['price']=Signals.get_ticker_orderbook_price(ticker,book_position,bs)
            
            print ("CREATE ORDER PRICE: "+str(order['price'])+" for "+order['action']+"--> "+str(order))
            
            orders_to_place+=[order]
            
            #IMMEDIATE VALIDATE ORDERS
            #print ("[] validate orders ie price>x ")

        return orders_to_place

if __name__=='__main__':
    branches=['dev1']

    for b in branches:
        globals()[b]()




