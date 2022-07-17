#!/usr/bin/env python3

import asyncio
import websockets

import json
from types import SimpleNamespace

from pyfirmata import Arduino, util 
from time import sleep

board = Arduino("/dev/ttyACM0", baudrate=57600)

#print(board.get_firmata_version()) 
# #checks generell woking connection

flagIncomingFromVirtual = False
flagHoererOben = False
data = '{"event": "RingsMaybe"}'

# Start iterator to receive input data
it = util.Iterator(board)
it.start() 
board.analog[0].enable_reporting()

async def server(websocket, path):
    # Get received data from websocket
    JSONIncomingFromVirtual = await websocket.recv()
    DictIncomingFromVirtual = eval(JSONIncomingFromVirtual)
    flagIncomingFromVirtual = DictIncomingFromVirtual["event"]
    print("flagIncomingFromVirtual type: " + type(flagIncomingFromVirtual))
    print(flagIncomingFromVirtual)

    #ring the bell
    if flagIncomingFromVirtual == "RingingStart":

        for x in range(10):
            board.digital[2].write(1)
            sleep(0.03)
            board.digital[2].write(0)
            board.digital[3].write(1)
            sleep(0.03)
            board.digital[3].write(0)
        
        print("ring")
        sleep(2)
    else:
        pass

    await asyncio.sleep(0.05)

    """ readResult = board.analog[0].read()
    print(readResult)
    if readResult <= 0.2:
        flagHoererOben = 1
    else:
        flagHoererOben = 0
    await asyncio.sleep(0.2)

    #if different stat: build JSON 
    flagHoererObenJSON = 

    # Send response back to client to acknowledge receiving message
    await websocket.send(flagHoererObenJSON) """

# Create websocket server
start_server = websockets.serve(server, "localhost", 3003)

# Start and run websocket server forever
# Server has to be running before browser ist loaded
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()