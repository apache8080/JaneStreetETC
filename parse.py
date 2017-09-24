import socket
import json
import random

# CLIENT MESSAGES
def hello():
    return {"type": "hello", "team": "GIZA"}

def placeOrder(symbol, order_id, buy_sell, price, size):
    symbol = symbol.upper()
    buy_sell = buy_sell.upper()
    return {"type": "add", "order_id": order_id, "symbol": symbol, "dir": buy_sell, "price": price, "size": size}

def convert(symbol, order_id, buy_sell, size):
    symbol = symbol.upper()
    buy_sell = buy_sell.upper()

    if (symbol != "VALBZ" and symbol != "VALE" and symbol != "XLF"):
        print "Not a valid symbol for conversion."

    if (symbol == "XLF" and size % 10 != 0):
        print "Cannot convert. Size must be a multiple of 10."

    return {"type": "convert", "order_id": order_id, "symbol": symbol, "dir": buy_sell, "size": size}

def cancel(order_id):
    return {"type": "cancel", "order_id": order_id}

# SERVER MESSAGES
def connect():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(("test-exch-giza", 25001))
    return s.makefile('rw', 1)

def write(exchange, obj):
    json.dump(obj, exchange)
    exchange.write("\n")

def read(exchange):
    return json.loads(exchange.readline())

server_begin = "SERVER: "

orders = []
def serverResponse():
    exchange = connect()
    write(exchange, hello())

    response = read(exchange)
    responseType = response["type"]
    while (responseType != "book"):
        response = read(exchange)
        responseType = response["type"]

    best_sell_price = response["sell"][0][0]

    order_id = random.randint(0, 9999999)
    orders.append(order_id)

    print best_sell_price
    write(exchange, placeOrder("WFC", order_id, "BUY", best_sell_price - 1, 1))

    print "ok"

    order_waiting = True
    while (order_waiting):
        response = read(exchange)
        responseType = response["type"]
        if (responseType == "fill" and response["order_id"] == orders[0]):
            order_waiting = False
        else:
            print "not filled yet"

    print "Order filled"

    order_id = random.randint(0, 99999)
    orders.append(order_id)
    write(exchange, placeOrder("WFC", order_id, "sell", best_sell_price + 1, 1))

    order_waiting = True
    while (order_waiting):
        response = read(exchange)
        responseType = response["type"]
        if (responseType == "fill" and response["order_id"] == orders[1]):
            order_waiting = False

    print "Order filled"
        # if responseType == "book" and response["symbol"] == "WFC":
            # symbol = response["symbol"]
            # print symbol
            # print "Buy:"
            # for order in response["buy"]:
            #     print "\t" + str(order)

            # print "Sell:"
            # for order in response["sell"]:
            #     print "\t" + str(order)

serverResponse()
