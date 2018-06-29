# binance_simulator_agent

System connects to the binance exchange and builds the real-time order book.  Websocket connections keep the connections alive and allow simulation agents to create orders in the binance market.  Note that because Binance doesn't offer a test environment -- the system simulates the orders and trade confirmations via tracking of the real-time market data for each trading pair.  (**abridged description -- contact developer for further details).
