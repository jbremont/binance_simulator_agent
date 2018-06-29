import time
import re
from sim_master import Sim_Master
from signals import The_Signals
from trading_desk import Trading_Desk


#0v1# JC  June  6, 2018  Initial setup

ACTIVE_TICKERS=['ETHBTC']
ACTIVE_TICKERS=['ETHBTC','TRXBTC','TRXETH']

def run_simulation():
    global ACTIVE_TICKERS

    running=True
    cycle_time=3

    print ("Running simulation...")
    
    tickers=['BNBBTC'] #dev
    
    tickers=ACTIVE_TICKERS
    

    Master=Sim_Master()
    

    print ("/start environment...")
    Signals=The_Signals()
    Signals.register_tickers(tickers)
    Signals.start_websockets()
    
    Desk=Trading_Desk()
    
    print ("Initialize agents...")
    Master.initialize_agents(tickers)
    
    print ("/Reset environment...")
    Desk.cancel_all_orders()

    print ("/starting trade cycles...")

    ccount=0
    while running:
        ccount+=1
        print (str(ccount)+") ...")
        
        #/get open orders
        open_tickers=Desk.refresh_order_status()
        open_orders_ids=Desk.list_open_orders_SIM()
        closed_orders=Desk.trade_details_ref_SIM()

        for Agent in Master.agents:
            actions=Agent.get_actions(open_orders_ids,closed_orders)
            if actions:
                print ("[debug actions]: "+str(actions)) #PLACE_BID,PLACE_SELL

                order_details=Agent.fetch_order_creation_details(actions)
                
                orders_to_place=Master.create_orders(Signals,order_details)
                
                new_buys,new_sells=Desk.place_orders(orders_to_place)

                Agent.note_orders_placed(new_buys,new_sells)
                
            if not ccount%5: #not print always
                Agent.print_report()

        time.sleep(cycle_time)


    Signals.shutdown()
    Desk.shutdown()
    print ("Done simulation")
    return


if __name__=='__main__':
    branches=['run_simulation']

    for b in branches:
        globals()[b]()
































