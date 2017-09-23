#!/usr/bin/python
from __future__ import print_function

import sys
import socket
import json

def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("test-exch-giza", 25000))
    return s.makefile('rw', 1)

def write(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read(exchange):
    return json.loads(exchange.readline())



def parseTradingData(market_response):
    datum = json.load(market_response)
    


def main():
    exchange = connect()
    write(exchange, {"type": "hello", "team": "GIZA"})
    hello_from_exchange = read(exchange)
    
    #print("The exchange replied:", hello_from_exchange, file=sys.stderr)   
    while(1):
        exch_book = read(exchange)
        if ('symbol' in exch_book and exch_book['symbol'] == 'BOND'):
            print("Book: ", exch_book, file=sys.stderr)

    

    

if __name__ == "__main__":
    main()



