#!/usr/bin/python
from __future__ import print_function

import sys
import socket
import json

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
    tradingCentral("BOND", "BUY", fairPrice -1 , 100, exchange)
    tradingCentral("BOND", "SELL", fairPrice + 1, 100, exchange)


def tradingCentral(symbol, direction, price, amount, exchange):
    N = str(randint(1, 2000000000))
    orders.append(N)
    json_string = '{"type": "add", "order_id": '+N+',"symbol": "' + symbol +'", "dir": "' +  direction + '", "price": ' + str(price) + ', "size" : ' + str(amount) + '}'
    print(json_string, file=sys.stderr)
    print(json_string, file=exchange)

def main():
    exchange = connect()
    write(exchange, {"type": "hello", "team": "GIZA"})
    hello_from_exchange = read(exchange)

    #print("The exchange replied:", hello_from_exchange, file=sys.stderr)   
    while(1):
        exch_book = read(exchange)
        if ('symbol' in exch_book and exch_book['symbol'] == 'BOND'):
            #print("Book: ", exch_book, file=sys.stderr)
            bondTrader(exchange)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
