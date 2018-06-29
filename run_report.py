import time
import re
from sim_master import Sim_Master
from signals import The_Signals
from trading_desk import Trading_Desk
import datetime

from dateutil import parser


#0v3# JC  June 14, 2018  Start tracking sells after first buy
#0v2# JC  June 13, 2018  Refine calculation
#0v1# JC  June 11, 2018  Initial setup


DATA_FILENAME='trade_logs_sample.tsv' #See user_agent.py
DATA_FILENAME='trade_logs.tsv' #See user_agent.py

TRADE_AMOUNT=0.05   #Assuming 0.1 per pair trade


class NestedDict(dict):
    def __getitem__(self, key):
        if key in self: return self.get(key)
        return self.setdefault(key, NestedDict())
    
class Report_Helper(object):
    def __init__(self):
        return
    
    def iter_stats(self):
        cols=['order_time','fill_time','ticker','side','quantity','price','fill_price','buy_position','sell_position']
        fp=open(DATA_FILENAME,'r')
        for line in fp.readlines():
            stats={}
            c=-1
            for col in re.split(r'\t',line.strip()): #convert to dict
                c+=1
                stats[cols[c]]=col
            yield stats
        fp.close()
        return
    
    def write_report(self,dd):

        report_output='report_0v1.tsv'
        fp=open(report_output,'w')
        for ticker in dd:
            for position in dd[ticker]:
                for window in dd[ticker][position]:
                    for w_idx in dd[ticker][position][window]:

                        aliners=[ticker]
                        pos=re.split('_',position) #30_20
                        aliners+=[pos[0]] #BUY
                        aliners+=[pos[1]] #SELL
                        
                        # day 122
                        aliners+=[window]
                        aliners+=[str(w_idx)]
                        
                        #For each additional stat category 
                        order_keep= ['high','low','amplitude','sell_trades_match','avg_profit','rolling_total']
                        unsorted={}
                        for stat in dd[ticker][position][window][w_idx]:
                            if not stat in order_keep: continue   #Filter to keep

                            unsorted[stat]=dd[ticker][position][window][w_idx][stat]

                        keep_line=True #Don't keep if no output

                        for key in order_keep:
                            aliners+=[key]


                            #Adjust values
                            if not key in unsorted:
                                the_stat=0
                            else:
                                the_stat=unsorted[key]
                            if str(the_stat)=='{}':the_stat=0

                            #Output only if sell_trades_match
                            if key=='sell_trades_match' and the_stat==0: keep_line=False

                            #Adjust output formats
                            if isinstance(the_stat,float):
                                aliners+=['%.8f'%the_stat]
                            else:
                                aliners+=[str(the_stat)]
                            
                        if keep_line:
                            fp.write(",".join(aliners)+"\n")
                            
        fp.close()
        print ("Wrote to: "+str(report_output))
        return
    
def date_is(given_date):
    #day of year,week of year,month of year
    day_of_year=given_date.timetuple().tm_yday
    month_of_year=given_date.month
    year=given_date.year
    return day_of_year,month_of_year,year

def calc_min(aa,bb):
    minn=0
    if not aa or not bb:
        minn=0
    else:
        minn=min([aa,bb])
    return minn

def run_report():

    verbose=True

    Report=Report_Helper()
    
    dd=NestedDict()
    
    all_buys={}
    sells_index={}
    rolling_daily_total_amount={}
    groups=['day','week','month']
    for stats in Report.iter_stats():
        if not isinstance(stats,dict) or not 'side' in stats:
            print ("> log file error, reset stats: ")
            all_buys={}
            sells_index={}
            #print ("Skipping info line: "+str(stats))
            continue

        #Convert back to date objects
        stats['order_time']=parser.parse(stats['order_time'])
        stats['fill_time']=parser.parse(stats['fill_time'])
        
        stats['price']=float(stats['price'])
        stats['fill_price']=float(stats['fill_price'])
                                        
        ticker=stats['ticker']
        position=stats['buy_position']+"_"+stats['sell_position']
        tdx=ticker+"_"+str(position)  #Ticker position index (non time dependent)

        if not tdx in all_buys:all_buys[tdx]=[] #For tracking pairs
        if not tdx in sells_index:sells_index[tdx]=-1 #For tracking pairs

        #See user_agent - Trade_Logger() for output formats
        day,month,year=date_is(stats['order_time'])
        
        sum_tups=[('day',day),('month',month),('year',year)]

        if stats['side']=='BUY':
            #all_buys[stats['fill_time']]=stats['fill_price']
            all_buys[tdx]+=[stats['fill_price']]
            #**warning if gap then potential gap in buy-sell matching
        else:
            #Start sell index once buy exists
            if tdx in all_buys and all_buys[tdx]:
                sells_index[tdx]+=1  #Increase sell (ref ticker+position)
        
        #Iterate and sum over different spans
        for winstr,winidx in sum_tups:
            print ("Calc "+tdx+" on "+winstr+" #"+str(winidx)+" (buy queue: "+str(len(all_buys[tdx])))

            #Count trades
            ########################################
            try: dd[ticker][position][winstr][winidx]['trades']+=1
            except: dd[ticker][position][winstr][winidx]['trades']=1

            #Stats:  high, low
            ########################################
            if not 'high' in dd[ticker][position][winstr][winidx]:
                dd[ticker][position][winstr][winidx]['high']=stats['fill_price']
            elif stats['fill_price']> dd[ticker][position][winstr][winidx]['high']:
                dd[ticker][position][winstr][winidx]['high']=stats['fill_price']
            else:pass
            
            if not 'low' in dd[ticker][position][winstr][winidx]:
                dd[ticker][position][winstr][winidx]['low']=stats['fill_price']
            elif stats['fill_price']< dd[ticker][position][winstr][winidx]['low']:
                dd[ticker][position][winstr][winidx]['low']=stats['fill_price']
            else:pass

            
            # Avg buy/sell + avg profile
            #########################################
            if stats['side']=='BUY':
                try: dd[ticker][position][winstr][winidx]['buy_price']+=stats['fill_price']
                except: dd[ticker][position][winstr][winidx]['buy_price']=stats['fill_price']
                try: dd[ticker][position][winstr][winidx]['buy_trades']+=1
                except: dd[ticker][position][winstr][winidx]['buy_trades']=1
    
                dd[ticker][position][winstr][winidx]['avg_buy']=dd[ticker][position][winstr][winidx]['buy_price']/dd[ticker][position][winstr][winidx]['buy_trades']
            elif stats['side']=='SELL':
                try: dd[ticker][position][winstr][winidx]['sell_price']+=stats['fill_price']
                except: dd[ticker][position][winstr][winidx]['sell_price']=stats['fill_price']
                try: dd[ticker][position][winstr][winidx]['sell_trades']+=1
                except: dd[ticker][position][winstr][winidx]['sell_trades']=1
                dd[ticker][position][winstr][winidx]['avg_sell']=dd[ticker][position][winstr][winidx]['sell_price']/dd[ticker][position][winstr][winidx]['sell_trades']
            else: a=watch_setup

            # PROFIT2:  New profit model
            #########################################
            #- Track buy - sell pairs from beginning. If nth SELL in period X then find nth BUY in period Y.
            if stats['side']=='SELL':
                try: buy_price=all_buys[tdx][sells_index[tdx]]
                except:
                    print ("[warning] assumption:  Selling more times then bought.  Bought: "+str(len(all_buys[tdx]))+" Sold: "+str(sells_index[tdx]+1))
                    buy_price=0

                #patch option
                #if not all_buys[tdx]:
                #    buy_price=stats['fill_price'] #Use sell price so no profit if have never bought
                #else: #Use last buy price
                #    buy_price=all_buys[tdx][len(all_buys[tdx])-1]
                print ("[d5] considering "+tdx+" on "+winstr+" #"+str(winidx)+" bought at: "+str(buy_price)+" sold at: "+str(stats['fill_price']))
                if buy_price:
                    try: dd[ticker][position][winstr][winidx]['sell_trades_match']+=1
                    except: dd[ticker][position][winstr][winidx]['sell_trades_match']=1

                    #Capture buy-sell spread "profit" as absolute prices (calc avg profit below)
                    print ("[d4] "+tdx+" on "+winstr+" #"+str(winidx)+" bought at: "+str(buy_price)+" sold at: "+str(stats['fill_price']))
                    try: dd[ticker][position][winstr][winidx]['sell_percent_profit_total']+=(stats['fill_price']/buy_price)-1
                    except: dd[ticker][position][winstr][winidx]['sell_percent_profit_total']=(stats['fill_price']/buy_price)-1
                    print ("Percent profit total at "+winstr+" #"+str(winidx)+"NOW: "+str(dd[ticker][position][winstr][winidx]['sell_percent_profit_total']))

  
            
            #Note matched pairs (ie/ min # sell/buys
            dd[ticker][position][winstr][winidx]['pairs']=calc_min(dd[ticker][position][winstr][winidx]['sell_trades'],dd[ticker][position][winstr][winidx]['buy_trades'])
            
            #Calc ongoing avg profit
            if False:
                print (ticker+" AVG SELL: "+str(dd[ticker][position][winstr][winidx]['avg_sell']))
                print (ticker+" AVG BUY: "+str(dd[ticker][position][winstr][winidx]['avg_buy']))
                print (ticker+" trades "+str(dd[ticker][position][winstr][winidx]['pairs']))

            #Cal average profit in period based on sells + buys in PERIOD
            try: dd[ticker][position][winstr][winidx]['avg_profit_org']=dd[ticker][position][winstr][winidx]['avg_sell']/dd[ticker][position][winstr][winidx]['avg_buy']-1
            except:pass

            #PROFIT2
            try: dd[ticker][position][winstr][winidx]['avg_profit']=dd[ticker][position][winstr][winidx]['sell_percent_profit_total']/dd[ticker][position][winstr][winidx]['sell_trades_match']
            except:pass

            #Amplitude
            dd[ticker][position][winstr][winidx]['amplitude']=dd[ticker][position][winstr][winidx]['high']-dd[ticker][position][winstr][winidx]['low']

            #day_total_amount
            try: dd[ticker][position][winstr][winidx]['total_amount_increase']=dd[ticker][position][winstr][winidx]['sell_trades_match']*dd[ticker][position][winstr][winidx]['avg_profit']*TRADE_AMOUNT
            except: dd[ticker][position][winstr][winidx]['total_amount_increase']=0

            if winstr=='day':
                INITIAL_AMOUNT=TRADE_AMOUNT*2
                try: dd[ticker][position][winstr][winidx]['rolling_total']+=dd[ticker][position][winstr][winidx]['total_amount_increase']
                except: dd[ticker][position][winstr][winidx]['rolling_total']=INITIAL_AMOUNT+dd[ticker][position][winstr][winidx]['total_amount_increase']
                





    Report.write_report(dd)
    print ("DONE1")
    return


def dev1():
    now=datetime.datetime.now()
    date_is(now)
    return

if __name__=='__main__':

    branches=['dev1']
    branches=['run_report']

    for b in branches:
        globals()[b]()
































