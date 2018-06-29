import time
import datetime
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.depthcache import DepthCacheManager

try:
    import ConfigParser
except:
    import configparser as ConfigParser

try:
    from db_interface_plus import Database_Base
except:pass

#0v3# JC  June  6 2018  Into binance sim (backwards compatible)
#0v2# JC  May 25, 2018  Integrate into binance export
#0v1# JC  Apr 13, 2018  Initial setup

# LOAD CONFIG SETTINGS
############################################
Config = ConfigParser.ConfigParser()
Config.read("settings.ini")
API_KEY=Config.get('api', 'key')
API_SECRET=Config.get('api', 'secret')


#Depth options:
#1/ depth rest query
#2/ depth socket on diffs
#3/ depth socket top 5,10,20
#4/ depth cache manager!
#   - http://python-binance.readthedocs.io/en/latest/_modules/binance/depthcache.html



class Order_Book(object):

    def __init__(self,BI='',auto_start=True,ticker='BNBBTC'):
        self.ticker=ticker
        try: self.DB=Database_Base()
        except:self.DB=''
        self.client=''
        if BI: self.client=BI.client
        self.connect()
        if auto_start:
            self.start_depth_cache(ticker=ticker)
        
        self.last_top_ask=0
        self.last_top_bid=0
        self.ticker=''
        return
    
    def connect(self):
        if not self.client:
            self.client = Client(API_KEY, API_SECRET)
#        self.bm = BinanceSocketManager(self.client)
        return
    
    def process_message(self,msg):
        print("message type: {}".format(msg['e']))
        print(msg)
        # do something
        return
    
    def shutdown(self):
        try:self.bm.close() #close all connections
        except:pass
        try: self.dcm.close()
        except:pass
        return
    
    def depth_rest(self):
        ticker='BNBBTC'
        if False:
            depth = self.client.get_order_book(symbol=ticker)
            print ("DEPTH: "+str(depth))
        diff_key = self.bm.start_depth_socket('BNBBTC', self.process_message)
        partial_key=self.bm.start_depth_socket('BNBBTC', self.process_message, depth=BinanceSocketManager.WEBSOCKET_DEPTH_5)
        print ("Started socket diff key: "+str(diff_key))
        return
    
    def process_depth(self,depth_cache):
        return
        if depth_cache is not None:
            print("symbol {}".format(depth_cache.symbol))
            print("top 5 bids")
            print(depth_cache.get_bids()[:5])
            print("top 5 asks")
            print(depth_cache.get_asks()[:5])
        else:
            # depth cache had an error and needs to be restarted
            pass
        return
        
    def start_depth_cache(self,ticker='BNBBTC'):
        self.dcm = DepthCacheManager(self.client, ticker, callback=self.process_depth, refresh_interval=60*30) #30 min refresh
        self.ticker=ticker
        return
    
    def get_depth_object(self):
        #At any time the current DepthCache object can be retrieved from the DepthCacheManager
        depth_cache = OB.dcm.get_depth_cache()
        print(depth_cache.get_bids()[:5])
        return
    
    def refresh(self):
        depth_cache = self.dcm.get_depth_cache()
        self.bids=depth_cache.get_bids()
        self.asks=depth_cache.get_asks()
        return
    
    def get_spread(self):
        self.refresh()
        top_bid=self.bids[0][0]
        top_ask=self.asks[0][0]
        spread=top_ask-top_bid

        self.last_top_ask=top_ask
        self.last_top_bid=top_bid
        return top_ask,top_bid
    
    def spread_direction(self,window=''):
        last_top_ask=self.last_top_ask
        last_top_bid=self.last_top_bid
        
        top_ask,top_bid=self.get_spread()
        
        old_spread=last_top_ask-last_top_bid
        new_spread=top_ask-top_bid
        
        spread_diff=new_spread-old_spread
        return spread_diff
    
    def print_spread(self):
        self.refresh()
        print ("BIDS: "+str(self.bids[:10]))
        print ("ASKS: "+str(self.asks[:10]))
        return
    
    def get_spread_dict(self):
        #For DB
        self.refresh()
        dd={}
        dd['the_date']=str(datetime.datetime.now())
        dd['ticker']=self.ticker
        dd['strategy_id']='dev1'
        c=0
        while c<10:
            c+=1
            idx='bid_p_'+str(c)
            dd[idx]=self.bids[c-1][0] #assume min 10
            idx='bid_s_'+str(c)
            dd[idx]=self.bids[c-1][1]
            idx='ask_p_'+str(c)
            dd[idx]=self.asks[c-1][0] #assume min 10
            idx='ask_s_'+str(c)
            dd[idx]=self.asks[c-1][1]
        return dd

    def store_spread(self):
        #> see db_manage for table creation
        dd=self.get_spread_dict()
        sql=self.DB.dict2query(dd,table='spread',force_update=True)
        print ("store: "+str(sql))
        self.DB.query(sql)
        return
    
    def get_order_at(self,the_type,depth):
        #**REFRESH**
        self.refresh()
        
        #price,size
        try:
            if the_type=='bid':
                price,size=self.bids[depth]
            else:
                price,size=self.asks[depth]
            pass
        except:
            price=0
            size=0
        return price,size
    
def print_spread():
    ticker='FUELETH'
    OB=Order_Book()
    OB.start_depth_cache(ticker=ticker)
    time.sleep(3)
    OB.print_spread()
    OB.store_spread()
    OB.shutdown()
    return

def dev_depth_cache():
    ticker='BNBBTC'
    ticker='FUELETH'

    OB=Order_Book()
    
    OB.start_depth_cache(ticker=ticker)
    print ("Depth cache manager started...")
    
    time.sleep(3)
    print ("Spread: "+str(OB.get_spread()))

    OB.shutdown()
    print ("Done depth")
    return


def spread_analytics():
    ticker='FUELETH'
    OB=Order_Book()
    OB.start_depth_cache(ticker=ticker)
    time.sleep(1)
    OB.get_spread()
    time.sleep(4)
    
    #1/  
    print ("Spread direction: "+str(OB.spread_direction()))
    return

    

if __name__=='__main__':
    branches=['dev_depth_cache']
    branches=['spread_analytics']
    branches=['print_spread']

    for b in branches:
        globals()[b]()



################################################################
#
################################################################

#DEPTH:
#DEPTH: {u'lastUpdateId': 61128872, 
#u'bids': [[u'0.00155680', u'165.06000000', []], 
#[u'0.00155660', u'59.41000000', []], [u'0.00155610', u'27.95000000', []], [u'0.00155600', u'140.27000000', []], [u'0.00155590', u'6.50000000', []], [u'0.00155580', u'0.65000000', []], [u'0.00155570', u'30.00000000', []], [u'0.00155560', u'10.00000000', []], [u'0.00155550', u'54.75000000', []], [u'0.00155540', u'1.00000000', []], [u'0.00155530', u'430.70000000', []], [u'0.00155510', u'45.79000000', []], [u'0.00155500', u'1235.74000000', []], [u'0.00155460', u'30.00000000', []], [u'0.00155450', u'10.89000000', []], [u'0.00155440', u'12.93000000', []], [u'0.00155410', u'42.00000000', []], [u'0.00155400', u'144.94000000', []], [u'0.00155390', u'2.00000000', []], [u'0.00155380', u'153.66000000', []], [u'0.00155370', u'17.27000000', []], [u'0.00155360', u'23.51000000', []], [u'0.00155350', u'12.00000000', []], [u'0.00155340', u'14.00000000', []], [u'0.00155330', u'8.00000000', []], [u'0.00155300', u'536.54000000', []], [u'0.00155290', u'1.00000000', []], [u'0.00155280', u'122.63000000', []], [u'0.00155270', u'41.75000000', []], [u'0.00155250', u'55.40000000', []], [u'0.00155230', u'0.65000000', []], [u'0.00155220', u'2.72000000', []], [u'0.00155210', u'50.14000000', []], [u'0.00155200', u'209.15000000', []], [u'0.00155190', u'13.00000000', []], [u'0.00155180', u'13.40000000', []], [u'0.00155170', u'33.02000000', []], [u'0.00155160', u'0.65000000', []], [u'0.00155150', u'10.00000000', []], [u'0.00155130', u'12.30000000', []], [u'0.00155120', u'42.50000000', []], [u'0.00155110', u'3.35000000', []], [u'0.00155100', u'719.13000000', []], [u'0.00155090', u'4.97000000', []], [u'0.00155080', u'150.74000000', []], [u'0.00155070', u'3.03000000', []], [u'0.00155060', u'197.81000000', []], [u'0.00155050', u'630.37000000', []], [u'0.00155040', u'1.00000000', []], [u'0.00155030', u'1.07000000', []], [u'0.00155020', u'5.00000000', []], [u'0.00155010', u'720.13000000', []], [u'0.00155000', u'4825.68000000', []], [u'0.00154990', u'415.70000000', []], [u'0.00154970', u'50.00000000', []], [u'0.00154960', u'18.77000000', []], [u'0.00154950', u'21.68000000', []], [u'0.00154920', u'28.00000000', []], [u'0.00154860', u'0.65000000', []], [u'0.00154850', u'113.50000000', []], [u'0.00154840', u'1.00000000', []], [u'0.00154830', u'23.11000000', []], [u'0.00154820', u'19.37000000', []], [u'0.00154810', u'5.00000000', []], [u'0.00154800', u'1.06000000', []], [u'0.00154760', u'38.56000000', []], [u'0.00154750', u'145.32000000', []], [u'0.00154730', u'0.65000000', []], [u'0.00154700', u'194.92000000', []], [u'0.00154680', u'200.00000000', []], [u'0.00154650', u'228.20000000', []], [u'0.00154640', u'4.65000000', []], [u'0.00154620', u'1.34000000', []], [u'0.00154590', u'13.94000000', []], [u'0.00154570', u'31.59000000', []], [u'0.00154560', u'1.00000000', []], [u'0.00154550', u'1.00000000', []], [u'0.00154540', u'4.24000000', []], [u'0.00154520', u'5.71000000', []], [u'0.00154510', u'42.39000000', []], [u'0.00154500', u'1584.83000000', []], [u'0.00154490', u'4.00000000', []], [u'0.00154450', u'0.65000000', []], [u'0.00154440', u'19.66000000', []], [u'0.00154420', u'4.00000000', []], [u'0.00154400', u'45.16000000', []], [u'0.00154380', u'0.77000000', []], [u'0.00154370', u'1.00000000', []], [u'0.00154360', u'44.35000000', []], [u'0.00154340', u'12.65000000', []], [u'0.00154330', u'4.00000000', []], [u'0.00154320', u'538.41000000', []], [u'0.00154310', u'3.20000000', []], [u'0.00154300', u'4.53000000', []], [u'0.00154290', u'9.73000000', []], [u'0.00154270', u'24.20000000', []], [u'0.00154250', u'121.95000000', []], [u'0.00154240', u'250.61000000', []], [u'0.00154210', u'98.09000000', []], [u'0.00154200', u'2813.81000000', []]], u'asks': [[u'0.00155730', u'0.61000000', []], [u'0.00155740', u'217.82000000', []], [u'0.00155750', u'2.12000000', []], [u'0.00155820', u'6.00000000', []], [u'0.00155830', u'86.35000000', []], [u'0.00155850', u'100.28000000', []], [u'0.00155860', u'654.11000000', []], [u'0.00155870', u'24.34000000', []], [u'0.00155890', u'1.51000000', []], [u'0.00155910', u'21.40000000', []], [u'0.00155920', u'85.11000000', []], [u'0.00155930', u'9.65000000', []], [u'0.00155970', u'4.54000000', []], [u'0.00155980', u'38.21000000', []], [u'0.00155990', u'303.81000000', []], [u'0.00156000', u'35.40000000', []], [u'0.00156020', u'12.00000000', []], [u'0.00156040', u'17.30000000', []], [u'0.00156070', u'335.23000000', []], [u'0.00156100', u'11.60000000', []], [u'0.00156110', u'8.17000000', []], [u'0.00156120', u'12.10000000', []], [u'0.00156130', u'13.50000000', []], [u'0.00156180', u'10.20000000', []], [u'0.00156190', u'14.10000000', []], [u'0.00156220', u'14.00000000', []], [u'0.00156290', u'200.00000000', []], [u'0.00156300', u'79.02000000', []], [u'0.00156310', u'12.40000000', []], [u'0.00156320', u'72.05000000', []], [u'0.00156330', u'14.30000000', []], [u'0.00156400', u'407.00000000', []], [u'0.00156410', u'61.05000000', []], [u'0.00156420', u'91.57000000', []], [u'0.00156430', u'68.68000000', []], [u'0.00156440', u'285.81000000', []], [u'0.00156460', u'55.95000000', []], [u'0.00156470', u'4.00000000', []], [u'0.00156500', u'12.00000000', []], [u'0.00156510', u'27.10000000', []], [u'0.00156530', u'379.57000000', []], [u'0.00156550', u'752.04000000', []], [u'0.00156560', u'54.34000000', []], [u'0.00156600', u'452.00000000', []], [u'0.00156630', u'5.59000000', []], [u'0.00156650', u'428.53000000', []], [u'0.00156670', u'222.54000000', []], [u'0.00156680', u'3.85000000', []], [u'0.00156690', u'65.21000000', []], [u'0.00156700', u'2604.86000000', []], [u'0.00156710', u'45.00000000', []], [u'0.00156720', u'2.13000000', []], [u'0.00156730', u'759.56000000', []], [u'0.00156740', u'2.00000000', []], [u'0.00156750', u'269.00000000', []], [u'0.00156760', u'4.80000000', []], [u'0.00156770', u'1.10000000', []], [u'0.00156780', u'87.98000000', []], [u'0.00156800', u'821.03000000', []], [u'0.00156830', u'7.27000000', []], [u'0.00156840', u'1.01000000', []], [u'0.00156850', u'369.02000000', []], [u'0.00156860', u'17.44000000', []], [u'0.00156870', u'2.13000000', []], [u'0.00156890', u'100.51000000', []], [u'0.00156900', u'479.48000000', []], [u'0.00156930', u'2.30000000', []], [u'0.00156950', u'601.35000000', []], [u'0.00156970', u'2.02000000', []], [u'0.00156980', u'0.68000000', []], [u'0.00157000', u'461.79000000', []], [u'0.00157010', u'4.32000000', []], [u'0.00157020', u'14.00000000', []], [u'0.00157030', u'7.01000000', []], [u'0.00157040', u'0.87000000', []], [u'0.00157050', u'6.37000000', []], [u'0.00157060', u'354.00000000', []], [u'0.00157100', u'287.04000000', []], [u'0.00157120', u'400.00000000', []], [u'0.00157140', u'2.71000000', []], [u'0.00157150', u'23.25000000', []], [u'0.00157160', u'10.18000000', []], [u'0.00157170', u'0.86000000', []], [u'0.00157180', u'3564.18000000', []], [u'0.00157200', u'17.17000000', []], [u'0.00157230', u'5.00000000', []], [u'0.00157240', u'70.00000000', []], [u'0.00157280', u'23.77000000', []], [u'0.00157300', u'64.27000000', []], [u'0.00157310', u'2.50000000', []], [u'0.00157340', u'9.00000000', []], [u'0.00157370', u'6.00000000', []], [u'0.00157390', u'8.26000000', []], [u'0.00157400', u'115.27000000', []], [u'0.00157410', u'515.00000000', []], [u'0.00157420', u'778.76000000', []], [u'0.00157450', u'0.98000000', []], [u'0.00157460', u'18.54000000', []], [u'0.00157490', u'20.00000000', []], [u'0.00157500', u'74.58000000', []]]}


# Get bid ask for all order books:
#Get first bid and ask entry in the order book for all markets.
#tickers = client.get_orderbook_tickers()


"""
{
"e": "depthUpdate", // Event type
"E": 123456789, // Event time
"s": "BNBBTC", // Symbol
"U": 157, // First update ID in event
"u": 160, // Final update ID in event
"b": [ // Bids to be updated
[
"0.0024", // price level to be updated
"10",
[] // ignore
]
],
"a": [ // Asks to be updated
[
"0.0026", // price level to be updated
"100", // quantity
[] // ignore
]
]
"""

