from pyfirmata import Arduino, util 
from time import sleep
#from threading import Thread 
import multiprocessing
import asyncio
from websockets import connect

board = Arduino("/dev/ttyACM0", baudrate=57600)

#print(board.get_firmata_version()) 
# #checks generell woking connection

flagIncomingFromVirtual = False
flagHoererOben = False

# Start iterator to receive input data
it = util.Iterator(board)
it.start() 
board.analog[0].enable_reporting()

def handleCheck():
    while True:
        sleep(0.02)
        """ it = util.Iterator(board)
        it.start()
        board.analog[0].enable_reporting() """
        readResult = board.analog[0].read()
        print(readResult)
        if readResult <= 0.2:
            flagHoererOben = True
        else:
            flagHoererOben = False
        sleep(0.2)
        print("flagHoererOben = " + str(flagHoererOben))
        return flagHoererOben

def ringTheBell(ringingFlag):
    while True:
        if ringingFlag == True:

            for x in range(10):
                board.digital[2].write(1)
                sleep(0.03)
                board.digital[2].write(0)
                board.digital[3].write(1)
                sleep(0.03)
                board.digital[3].write(0)

            sleep(2)
        else:
            pass

""" async def communicateVirtual(uri):
    async with connect(uri) as websocket:
        await websocket.send("flagHoererOben = " + str(flagHoererOben))
        await websocket.recv() """

""" thread_Handle = Thread(target=handleCheck)
thread_Bell = Thread(target=ringTheBell(flagHoererOben)) """

process_Handle = multiprocessing.Process(target=handleCheck, args=[])
process_Bell = multiprocessing.Process(target=ringTheBell, args=[flagHoererOben])


""" thread_Handle.start()
thread_Bell.start() """

if __name__ == '__main__':
    process_Handle.start()
    process_Bell.start()

#asyncio.run(communicateVirtual("https://virtual.obejtkleina.com:8765"))