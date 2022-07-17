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

url = "ws://localhost:3003"

async def listenAndRing():
    
    async with websockets.connect(url) as ws:
        while True:

            # Get received data from websocket
            JSONIncomingFromVirtual = await ws.recv()
            DictIncomingFromVirtual = eval(JSONIncomingFromVirtual)
            flagIncomingFromVirtual = DictIncomingFromVirtual["event"]
            print("flagIncomingFromVirtual type: " + str(type(flagIncomingFromVirtual)))
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
            #return flagIncomingFromVirtual

# Der Teil hier hat bei in der Browser-Konsole grundsätzlich funktioniert. 
# Problem: der Return funktioniert nicht so richtig. Die Flag zum Verglechen des Status für ein
# Event kommt noch nicht so an, dass saubere Events gesendet werden.
""" async def server(websocket, path):
    readResult = board.analog[0].read() 
    #print(readResult)
    if readResult <= 0.2:
        flagHoererObenNow = False
    else:
        flagHoererObenNow = True
    print(flagHoererObenNow)

    await asyncio.sleep(0.1)

    # Send response back to client to acknowledge receiving message
    if flagHoererObenNow != flagHoererOben:
        if flagHoererObenNow == True:
            flagHoererObenJSON =  json.dumps({"event":"RevieverPicketUp"})
            #print(type(flagHoererObenJSON))
            print(flagHoererObenJSON)
        #else:
        elif flagHoererObenNow == False:
            flagHoererObenJSON = json.dumps({"event":"RevieverPutDown"})
            print(flagHoererObenJSON)
        await websocket.send(flagHoererObenJSON)
        #await asyncio.sleep(0.2)
    
    flagHoererObenNow = flagHoererOben
    return flagHoererOben """

# Create websocket server
#start_server = websockets.serve(server, "localhost", 3003)

# Start and run websocket server forever
# Server has to be running before browser ist loaded
#asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_until_complete(listenAndRing)
asyncio.get_event_loop().run_forever()