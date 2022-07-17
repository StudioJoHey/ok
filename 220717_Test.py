import asyncio
import websockets
import subprocess

import json
from types import SimpleNamespace

from pyfirmata import Arduino, util
from time import sleep

# board = Arduino("/dev/ttyACM0", baudrate=57600)

# print(board.get_firmata_version())
# #checks generell woking connection

flagIncomingFromVirtual = False
flagHoererOben = False
data = '{"event": "RingsMaybe"}'

# Start iterator to receive input data from Arduino
# it = util.Iterator(board)
# it.start()
# board.analog[0].enable_reporting()

# url = "ws://localhost:3003"
WsDomain = "localhost"
WsPort = 3003


# switches the pysical phone bell on by alternating the current
# def Ring(): #to run with ThreadPoolExecutor or regular subprocess
def ring():
    # while True: #when run as "event based" subrpocess
    print("ring")
    for x in range(10):
        print("board.digital[2].write(1)")
        sleep(0.03)
        print("board.digital[2].write(0)")
        print("board.digital[3].write(1)")
        sleep(0.03)
        print("board.digital[3].write(0)")

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


# return flagIncomingFromVirtual = "RingingStart"

async def handler(websocket: websockets.WebSocketServerProtocol):
    # loop = asyncio.get_running_loop() #für ThreadPoolExecutor
    ring_sub_process = None
    while True:
        print("running")
        json_incoming_from_virtual = await websocket.recv()
        dict_incoming_from_virtual = eval(json_incoming_from_virtual)
        flag_incoming_from_virtual = dict_incoming_from_virtual["event"]
        print("flag_incoming_from_virtual type: " + str(type(flag_incoming_from_virtual)))
        print(flag_incoming_from_virtual)

        # ring the bell
        if flag_incoming_from_virtual == "RingingStart":
            # ring_sub_process = asyncio.create_subprocess_exec (Ring, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE) #will auch "await" und damit warten bis der Loop in der Function fertig ist. Nicht für Event zu gebrauchen
            ring_sub_process = subprocess.run(ring, capture_output=True)  # bleibt auch an dieser Stelle im Loop hängen, wenn die Function while True enthällt
            # await Ring() #lässt den gesamten handle while loop nur einmal laufen ... KEINE AHNUNG WARUM, AUCH WENN "running" bei gleicher Flag schon wieder geprintet wird
            # flag_incoming_from_virtual = await Ring() #Versuch, die Varable zu pipen, das scheint aber nicht das Problem des nicht weitergehenden Loops
            # ring_sub_process = await asyncio.to_thread(Ring) # functioniert nicht, weil der Loop nie weiter geht als hier
            # with concurrent.futures.ThreadPoolExecutor() as pool: ring_sub_process = await loop.run_in_executor(pool, Ring)
        if ring_sub_process is not None and flag_incoming_from_virtual == "RingingStop":
            ring_sub_process.terminate()
        else:
            pass  # war als event gedacht, will so aber nicht so richtig


async def main():
    async with websockets.serve(handler, WsDomain, WsPort):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())