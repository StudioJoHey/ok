import asyncio
import websockets
from time import sleep
import concurrent.futures
import subprocess

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

# Start iterator to receive input data from Arduino
it = util.Iterator(board)
it.start() 
board.analog[0].enable_reporting()

#url = "ws://localhost:3003"
WsDomain = "localhost"
WsPort = 3003

#switches the pysical phone bell on by alternating the current
#def Ring(): #to run with ThreadPoolExecutor or regular subprocess
def Ring(): 
    #while True: #when run as "event based" subrpocess
    print("ring")
    for x in range(10):
        board.digital[2].write(1)
        sleep(0.03)
        board.digital[2].write(0)
        board.digital[3].write(1)
        sleep(0.03)
        board.digital[3].write(0)

    sleep(1)
    return

""" async def Ring(): 
    while True: #when run as "event based" subrpocess
        print("ring")
        for x in range(10):
            board.digital[2].write(1)
            await asyncio.sleep(0.03)
            board.digital[2].write(0)
            board.digital[3].write(1)
            await asyncio.sleep(0.03)
            board.digital[3].write(0)

        await asyncio.sleep(1) """
    #return flagIncomingFromVirtual = "RingingStart"

async def handler(websocket):
    #loop = asyncio.get_running_loop() #für ThreadPoolExecutor
    RingSubProcess = None
    while True:
        print("running")
        JSONIncomingFromVirtual = await websocket.recv()
        DictIncomingFromVirtual = eval(JSONIncomingFromVirtual)
        flagIncomingFromVirtual = DictIncomingFromVirtual["event"]
        print("flagIncomingFromVirtual type: " + str(type(flagIncomingFromVirtual)))
        print(flagIncomingFromVirtual)

        #ring the bell
        if flagIncomingFromVirtual == "RingingStart":
            #RingSubProcess = asyncio.create_subprocess_exec (Ring, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE) #will auch "await" und damit warten bis der Loop in der Function fertig ist. Nicht für Event zu gebrauchen
            RingSubProcess = subprocess.run(Ring(), capture_output = True) #bleibt auch an dieser Stelle im Loop hängen, wenn die Function while True enthällt
            #await Ring() #lässt den gesamten handle while loop nur einmal laufen ... KEINE AHNUNG WARUM, AUCH WENN "running" bei gleicher Flag schon wieder geprintet wird
            #flagIncomingFromVirtual = await Ring() #Versuch, die Varable zu pipen, das scheint aber nicht das Problem des nicht weitergehenden Loops
            #RingSubProcess = await asyncio.to_thread(Ring) # functioniert nicht, weil der Loop nie weiter geht als hier
            #with concurrent.futures.ThreadPoolExecutor() as pool: RingSubProcess = await loop.run_in_executor(pool, Ring)
        if RingSubProcess != None and flagIncomingFromVirtual == "RingingStop":
            RingSubProcess.terminate() 
        else:
            pass #war als event gedacht, will so aber nicht so richtig
        

async def main():
    async with websockets.serve(handler, WsDomain, WsPort):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())