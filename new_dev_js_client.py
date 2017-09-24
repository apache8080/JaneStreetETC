#!/usr/bin/python
from __future__ import print_function

import sys
import socket
import json
from random import randint
import time


orders = []
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("production", 25000))
    return s.makefile('rw', 1)

def write(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read(exchange):
    return json.loads(exchange.readline())

def bondTrader(exchange):
    fairPrice = 1000    #change it 1000 later
    tradingCentral("BOND", "BUY", fairPrice - 1 , randint(10, 75), exchange)
    tradingCentral("BOND", "SELL", fairPrice + 1, randint(10,75), exchange)


def tradingCentral(symbol, direction, price, amount, exchange):
    N = str(randint(1, 2000000000))
    orders.append(N)
    json_string = '{"type": "add", "order_id": '+N+',"symbol": "' + symbol +'", "dir": "' +  direction + '", "price": ' + str(price) + ', "size" : ' + str(amount) + '}'
    print(json_string, file=sys.stderr)
    print(json_string, file=exchange)

def parseTradeData(messages):
    datum = json.loads(messages)
    if datum['type'] == "reject" and datum['error'] == "TRADING_CLOSED":
      sys.exit(2)

exch_book_basket = {"BOND": 0, "GS": 0, "MS": 0, "WFC": 0}
weights = {"BOND": 3, "GS": 2, "MS": 3, "WFC": 2}
def XLFCalculate(exch_book):
    print("Calculate xlf")

    global exch_book_basket
    buy_list = exch_book["buy"]
    sell_list = exch_book["sell"]
    total = 0
    counter = 0
    for item in buy_list:
        total += item[0]
        counter += 1
    for item in sell_list:
        total += item[0]
        counter += 1
    exch_book_basket[exch_book["symbol"]] += weights[exch_book["symbol"]] * (total / (counter * 1.0))

num_xlf = 0
def main():
    exchange = connect()
    write(exchange, {"type": "hello", "team": "GIZA"})
    hello_from_exchange = read(exchange)
     
    global exch_book_basket
    global num_xlf
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
    clear_counter = 0
    #print("The exchange replied:", hello_from_exchange, file=sys.stderr)   
    while(1):
        exch_book = read(exchange)
        if ('symbol' in exch_book and exch_book['symbol'] == 'BOND'):
            #print("Book: ", exch_book, file=sys.stderr)
            bondTrader(exchange)
	
        if (exch_book["type"] == "book" and exch_book['symbol'] == "BOND"):
            XLFCalculate(exch_book)
        if (exch_book["type"] == "book" and exch_book['symbol'] == "GS"):
            XLFCalculate(exch_book)
        if (exch_book["type"] == "book" and exch_book['symbol'] == "MS"):
            XLFCalculate(exch_book)
        if (exch_book["type"] == "book" and exch_book['symbol'] == "WFC"):
            XLFCalculate(exch_book)
        if (exch_book["type"] == "book" and exch_book['symbol'] == "XLF"):
            print(exch_book['sell'])
            if len(exch_book['sell']) != 0:
                sell_price = exch_book['sell'][0][0]
                calculated_xlf_value = 0
                for value in exch_book_basket.keys():
                    calculated_xlf_value += exch_book_basket[value]
                    
                if calculated_xlf_value < sell_price:
                    tradingCentral("XLF", "BUY", sell_price, 1, exchange)
                    tradingCentral("GS", "SELL", exch_book_basket["GS"], 2, exchange)                
                    tradingCentral("MS", "SELL", exch_book_basket["MS"], 3, exchange)                
                    tradingCentral("WFC", "SELL", exch_book_basket["WFC"], 2, exchange)
                else:
                    tradingCentral("XLF", "SELL", sell_price, 1, exchange)
                    tradingCentral("GS", "BUY", exch_book_basket["GS"], 2, exchange)                
                    tradingCentral("MS", "BUY", exch_book_basket["MS"], 3, exchange)                
                    tradingCentral("WFC", "BUY", exch_book_basket["WFC"], 2, exchange)
		
        if (exch_book['type'] == 'fill' and exch_book['symbol'] == 'XLF'):
            if exch_book['dir'] == 'BUY':
                num_xlf += 1
            if exch_book['dir'] == 'SELL':
                num_xlf -= 1
        if num_xlf == 10 or num_xlf == -10:
            rand_num = randint(0, 99999999)
            write(exchange, {"type": "convert", "order_id": rand_num, "symbol": "XLF", "dir": "SELL", "size": 10})
            num_xlf = 0
	
	if(len(vale_orders) >= 10): 
	    order_id = randint(1, 200000000);
	    write(exchange, {"type": "convert", "symbol": 'VALE', "order_id":order_id, "dir": "SELL", "size": 10 })
	    print("CONVERTING")
	    vale_orders = []

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
		print(str(i[0])+' --------- '+str(market_value))
		if(i[0] < market_value+1):
		    print("MAKING A TRADE")
		    buy_order_id = randint(1, 2000000000)
		    sell_order_id = randint(1, 2000000000)

		    orders.append(buy_order_id)
		    orders.append(sell_order_id)
				
		    write(exchange, {"type": "add", "symbol": "VALE", "dir": "BUY", "order_id": buy_order_id, "price": i[0], "size": 1})	
		    write(exchange, {"type": "add", "symbol": "VALBZ", "dir": "SELL", "order_id": sell_order_id, "price": market_value, "size": 1})
		else:
		    print("MAKING A TRADE")
		    buy_order_id = randint(1, 2000000000)
		    sell_order_id = randint(1, 2000000000)

		    orders.append(buy_order_id)
		    orders.append(sell_order_id)
				
		    write(exchange, {"type": "add", "symbol": "VALE", "dir": "SELL", "order_id": buy_order_id, "price": i[0], "size": 1})	
		    write(exchange, {"type": "add", "symbol": "VALBZ", "dir": "BUY", "order_id": sell_order_id, "price": market_value, "size": 1})

	elif ('symbol' in exch_book and exch_book['type'] == 'book' and exch_book['symbol'] == 'VALBZ'):    
	    sell_price = sum([s[0]*s[1] for s in exch_book['sell']])
	    buy_price = sum([b[0]*b[1] for b in exch_book['buy']])
	    buyers = sum([b[1] for b in exch_book['buy']])
	    sellers = sum([s[1] for s in exch_book['sell']])
	    market_value = (sell_price+buy_price)/(sellers + buyers)
	    print("VALBZ: ", market_value, file=sys.stderr)
   
	time.sleep(0.05) 

if __name__ == "__main__":
    main()

