#!/usr/bin/python
from __future__ import print_function

import sys
import socket
import json
from random import randint

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("test-exch-GIZA", 25000))
    return s.makefile('rw', 1)

def write(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read(exchange):
    return json.loads(exchange.readline())

def main():
    exchange = connect()
    write(exchange, {"type": "hello", "team": "GIZA"})
    hello_from_exchange = read(exchange)    
    print("The exchange replied:", hello_from_exchange, file=sys.stderr)
    for s in hello_from_exchange['symbols']:
	if(s['symbol'] == 'VALE' and s['position'] == 10):
	   order_id = randint(1, 200000000);
	   write(exchange, {"type": "convert", "symbol": 'VALE', "order_id":order_id, "dir": "SELL", "size": 10 })

    market_value = 0
    counter = 0
    orders = []
    filled_orders = []
    vale_orders = []
    valbz_orders = []
    fillc = 0
    while(counter<5000):
	exch_book = read(exchange)
	if(len(filled_orders) < 10):
	    if (exch_book['type'] == 'fill'):
	        print('FILL: ', exch_book, file=sys.stderr)
	        filled_orders.append(exch_book['order_id'])
	        if(exch_book['symbol'] == 'VALE'):
		    vale_orders.append(exch_book)
	        if(exch_book['symbol'] == 'VALBZ'):
		    valbz_orders.append(exch_book)
	    elif ('symbol' in exch_book and exch_book['type'] == 'book' and exch_book['symbol'] == 'VALE'):    
    	        print("Book: ", exch_book, file=sys.stderr)
	        for i in exch_book["sell"]:
		    if(i[0] < market_value):
		        print("MAKING A TRADE")
		        buy_order_id = randint(1, 2000000000)
		        sell_order_id = randint(1, 2000000000)
		        convert_order_id = randint(1, 2000000000)

		        orders.append(buy_order_id)
		        orders.append(sell_order_id)
		        orders.append(convert_order_id)
				
		        write(exchange, {"type": "add", "symbol": "VALE", "dir": "BUY", "order_id": buy_order_id, "price": i[0], "size": 1})	
		        write(exchange, {"type": "add", "symbol": "VALBZ", "dir": "SELL", "order_id": sell_order_id, "price": market_value, "size": 1})
		        print(read(exchange))
	    elif ('symbol' in exch_book and exch_book['type'] == 'trade' and exch_book['symbol'] == 'VALBZ'):    
    	        print("TRADE: ", exch_book, file=sys.stderr)
	        market_value = exch_book['price']
	else:	
    	    cancel_these = list(set(orders)-set(filled_orders))
    	    for c in cancel_these:
	        write(exchange, {"type": "cancel", "order_id": c})
	    filled_orders = []	
		   
	if(len(vale_orders)>9): 
	    order_id = randint(1, 200000000);
	    write(exchange, {"type": "convert", "symbol": 'VALE', "order_id":order_id, "dir": "SELL", "size": 10 })

	counter = counter + 1

    cancel_these = list(set(orders)-set(filled_orders))
    for c in cancel_these:
	write(exchange, {"type": "cancel", "order_id": c})

    while(1):
	print("test")
if __name__ == "__main__":
    main()
