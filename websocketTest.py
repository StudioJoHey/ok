#!/usr/bin/env python3

import asyncio
import websockets

from pyfirmata import Arduino, util 
from time import sleep

board = Arduino("/dev/ttyACM0", baudrate=57600)

#print(board.get_firmata_version()) 
# #checks generell woking connection

flagIncomingFromVirtual = 0
flagHoererOben = 0

# Start iterator to receive input data
it = util.Iterator(board)
it.start() 
board.analog[0].enable_reporting()

async def server(websocket, path):
    # Get received data from websocket
    data = await websocket.recv()

    # Send response back to client to acknowledge receiving message
    await websocket.send("Thanks for your message: " + data)

    while True:
        await asyncio.sleep(0.05)

        readResult = board.analog[0].read()
        print(readResult)
        if readResult <= 0.2:
            flagHoererOben = 1
        else:
            flagHoererOben = 0
        await asyncio.sleep(0.2)

        #await websocket.send("flagHoererOben = " + str(flagHoererOben))
        --> Send event: PhoneServerMessag: event : "RecieverPicketUp" / "RecieverPutDown"
        Listen to: PhoneClientMessage event : "RingingStart" / "Ringing Stop"

# Create websocket server
start_server = websockets.serve(server, "localhost", 3003)

# Start and run websocket server forever
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()