import asyncio
import sys
import threading
from typing import Optional

import websockets

import json

#from pyfirmata import Arduino, util
from time import sleep

from websockets.exceptions import ConnectionClosedOK

from api_model.EventObject import EventObject


# board = Arduino("/dev/ttyACM0", baudrate=57600)
board = None

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

RingStopEvent = threading.Event()
RingLock = threading.Lock()


# switches the pysical phone bell on by alternating the current
def ring() -> None:
    print("ring init")
    if RingLock.acquire(blocking=False):
        while not RingStopEvent.is_set():  # when run as "event based" subprocess
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
        RingLock.release()
    else:
        print("Another tread is already ringing.")


def get_hoerer_up() -> bool:
    return True


async def get_hoerer_change() -> bool:
    await asyncio.get_event_loop().run_in_executor(
        None, lambda: sys.stdout.write("is the hoerer Up? [yN]"))
    response: str = await asyncio.get_event_loop().run_in_executor(
        None, sys.stdin.readline)

    return response.strip().lower() == "y"


async def handler(websocket: websockets.WebSocketServerProtocol) -> None:
    # loop = asyncio.get_running_loop() #für ThreadPoolExecutor
    ring_thread: threading.Thread

    while True:
        print("client connected, awaiting input")
        try:
            json_incoming_from_virtual = await websocket.recv()
        except:
            print("connection failed.")
            break
        try:
            incoming: EventObject = json.loads(
                json_incoming_from_virtual, object_hook=lambda e: EventObject(e))
        except json.decoder.JSONDecodeError:
            incoming = json_incoming_from_virtual

        if type(incoming) != EventObject:
            print("Event isn't a json object: ")
            print(json_incoming_from_virtual)
            continue

        flag_incoming_from_virtual = incoming.event
        print(f'event flag: "{flag_incoming_from_virtual}" ({type(flag_incoming_from_virtual).__name__})')

        # ring the bell
        if flag_incoming_from_virtual is None:
            print("json key 'event' missing; can't decide what to do.")
        if flag_incoming_from_virtual == "RingingStart":
            RingStopEvent.clear()
            ring_thread = threading.Thread(target=ring, name="Ringer")
            ring_thread.start()
        if flag_incoming_from_virtual == "RingingStop":
            RingStopEvent.set()
        else:
            pass  # war als event gedacht, will so aber nicht so richtig

        flag_subscribe_to_hoerer = incoming.subscribe_to_hoerer
        print(f'subscribe flag: "{flag_subscribe_to_hoerer}" ({type(flag_subscribe_to_hoerer).__name__})')
        if type(flag_subscribe_to_hoerer) == str and flag_subscribe_to_hoerer.lower() == "now":
            await send_hoerer_state(websocket, get_hoerer_up())

        if type(flag_subscribe_to_hoerer) == str and flag_subscribe_to_hoerer.lower() == "onchange":
            # TODO: do not block
            # alternatively: make browser.html open a separate ws for ringing
            await send_hoerer_change(websocket)

            #doesn't block, but websocket will be expired.
            # change_task = asyncio.create_task(send_hoerer_change(websocket))


async def send_hoerer_change(websocket):
    state = await get_hoerer_change()
    await send_hoerer_state(websocket, state)


async def send_hoerer_state(websocket, hoerer_up: bool):
    response = dict(hoerer_state=hoerer_up)
    await websocket.send(json.dumps(response))


async def main() -> None:
    async with websockets.serve(handler, WsDomain, WsPort):
        print("starting server, awaiting connections")
        # python -m websockets ws://localhost:3003
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
