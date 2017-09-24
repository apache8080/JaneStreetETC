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
    s.connect(("test-exch-giza", 25000))
    return s.makefile('rw', 1)

def write(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read(exchange):
    return json.loads(exchange.readline())

def bondTrader(exchange):
    fairPrice = 1000    #change it 1000 later
    tradingCentral("BOND", "BUY", fairPrice - 1 , randint(10, 35), exchange)
    tradingCentral("BOND", "SELL", fairPrice + 1, randint(10,35), exchange)


def tradingCentral(symbol, direction, price, amount, exchange):
    N = str(randint(1, 2000000000))
    orders.append(N)
    json_string = '{"type": "add", "order_id": '+N+',"symbol": "' + symbol +'", "dir": "' +  direction + '", "price": ' + str(price) + ', "size" : ' + str(amount) + '}'
    print(json_string, file=exchange)

def parseTradeData(messages):
    datum = json.loads(messages)
    if datum['type'] == "reject" and datum['error'] == "TRADING_CLOSED":
      sys.exit(2)

exch_book_basket = {"BOND": 0, "GS": 0, "MS": 0, "WFC": 0}
weights = {"BOND": 3, "GS": 2, "MS": 3, "WFC": 2}
def XLFCalculate(exch_book):
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
    if counter != 0:
        exch_book_basket[exch_book["symbol"]] += weights[exch_book["symbol"]] * 0.1 * (total / (counter * 1.0))

num_xlf = 0
def main():
    global exch_book_basket
    global num_xlf

    exchange = connect()
    write(exchange, {"type": "hello", "team": "GIZA"})
    hello_from_exchange = read(exchange)

    #print("The exchange replied:", hello_from_exchange, file=sys.stderr)   
    while(1):
        exch_book = read(exchange)
        # if ('symbol' in exch_book and exch_book['symbol'] == 'BOND'):
        #     #print("Book: ", exch_book, file=sys.stderr)
        #     bondTrader(exchange)
        #     time.sleep(0.1)
        #     print ("testing")
        if (exch_book["type"] == "book" and exch_book['symbol'] == "BOND"):
            XLFCalculate(exch_book)
        if (exch_book["type"] == "book" and exch_book['symbol'] == "GS"):
            XLFCalculate(exch_book)
        if (exch_book["type"] == "book" and exch_book['symbol'] == "MS"):
            XLFCalculate(exch_book)
        if (exch_book["type"] == "book" and exch_book['symbol'] == "WFC"):
            XLFCalculate(exch_book)
        if (exch_book["type"] == "book" and exch_book['symbol'] == "XLF"):
            if len(exch_book['sell']) != 0:
                sell_price = exch_book['sell'][0][0]
                calculated_xlf_value = 0

                for value in exch_book_basket.keys():
                    calculated_xlf_value += (exch_book_basket[value])

                exch_book_basket = {"BOND": 0, "GS": 0, "MS": 0, "WFC": 0}
                    
                print(calculated_xlf_value)
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
            if (exch_book['dir'] == 'buy'):
                num_xlf += 1
            elif (exch_book["dir"] == "sell"):
                num_xlf -= 1
        if num_xlf % 10 == 0:
            rand_num = randint(0, 99999999)
            write(exchange, {"type": "convert", "order_id": rand_num, "symbol": "XLF", "dir": "SELL", "size": 10})
            num_xlf = 0
            
if __name__ == "__main__":
    main()

