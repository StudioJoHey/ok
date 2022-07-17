import asyncio
import threading

import websockets
import subprocess

import json
from types import SimpleNamespace

from pyfirmata import Arduino, util
from time import sleep

# board = Arduino("/dev/ttyACM0", baudrate=57600)
board: Arduino = None

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

StopEvent = threading.Event()


# switches the pysical phone bell on by alternating the current
def ring() -> None:
    print("ring init")
    while not StopEvent.is_set():  # when run as "event based" subprocess
        print("ring")
        if board is not None:
            for x in range(10):
                board.digital[2].write(1)
                sleep(0.03)
                board.digital[2].write(0)
                board.digital[3].write(1)
                sleep(0.03)
                board.digital[3].write(0)

        sleep(1)


# return flagIncomingFromVirtual = "RingingStart"

async def handler(websocket: websockets.WebSocketServerProtocol) -> None:
    # loop = asyncio.get_running_loop() #für ThreadPoolExecutor
    ring_thread: threading.Thread
    while True:
        print("client connected, awaiting input")
        json_incoming_from_virtual = await websocket.recv()
        # expects {"event": "RingingStart"}
        # TODO: create type for parsing
        # TODO: use boolean for the flags?
        dict_incoming_from_virtual = eval(json_incoming_from_virtual)
        flag_incoming_from_virtual = dict_incoming_from_virtual["event"]
        print("flag_incoming_from_virtual type: " + str(type(flag_incoming_from_virtual)))
        print(flag_incoming_from_virtual)

        # ring the bell
        if flag_incoming_from_virtual == "RingingStart":
            StopEvent.clear()
            ring_thread = threading.Thread(target=ring, name="Ringer")
            ring_thread.start()
        if flag_incoming_from_virtual == "RingingStop":
            StopEvent.set()
        else:
            pass  # war als event gedacht, will so aber nicht so richtig


async def main() -> None:
    async with websockets.serve(handler, WsDomain, WsPort):
        print("starting server, awaiting inputs")
        # python -m websockets ws://localhost:3003
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())