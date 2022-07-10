from pyfirmata import Arduino, util 
from time import sleep
import asyncio
from websockets import connect

board = Arduino("/dev/ttyACM0", baudrate=57600)

#print(board.get_firmata_version()) 
# #checks generell woking connection

flagIncomingFromVirtual = 0
flagHoererOben = 0

# Start iterator to receive input data
it = util.Iterator(board)
it.start()
board.analog[0].enable_reporting()

async def communicateVirtual(uri):
    async with connect(uri) as websocket:
        await websocket.send("flagHoererOben = " + str(flagHoererOben))
        await websocket.recv()

while True:
    sleep(0.01)
    it = util.Iterator(board)
    it.start()
    board.analog[0].enable_reporting()
    readResult = board.analog[0].read()
    #print(readResult)
    if readResult <= 0.2:
        flagHoererOben = 1
    else:
        flagHoererOben = 0
    sleep(0.2)

    print("flagHoererOben = " + str(flagHoererOben))

while flagIncomingFromVirtual == 1:

    for x in range(10):
        board.digital[2].write(1)
        sleep(0.03)
        board.digital[2].write(0)
        board.digital[3].write(1)
        sleep(0.03)
        board.digital[3].write(0)

    sleep(2)

asyncio.run(communicateVirtual("https://virtual.obejtkleina.com:8765"))