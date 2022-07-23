import asyncio
import threading
from typing import Optional

import websockets

import json

#from pyfirmata import Arduino, util
from time import sleep
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
UpdateStopEvent = threading.Event()


# switches the pysical phone bell on by alternating the current
def ring() -> None:
    print("ring init")
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


# switches the pysical phone bell on by alternating the current
async def continous_update(websocket: websockets.WebSocketServerProtocol) -> None:
    
    while not UpdateStopEvent.is_set():  # when run as "event based" subprocess
        print("updating hoerer state")
        await websocket.send("abc")

        sleep(1)


# return flagIncomingFromVirtual = "RingingStart"

def get_hoerer_raised() -> bool:
    return True;

async def handler(websocket: websockets.WebSocketServerProtocol) -> None:
    # loop = asyncio.get_running_loop() #für ThreadPoolExecutor
    ring_thread: threading.Thread

    #update_thread = threading.Thread(target=lambda: continous_update(websocket), name="")

    i=0
    while True:
        print("client connected, awaiting input")
        json_incoming_from_virtual = await websocket.recv()
        try:
            incoming: EventObject = json.loads(
                json_incoming_from_virtual, object_hook=lambda e: EventObject(e))
        except json.decoder.JSONDecodeError:
            incoming = json_incoming_from_virtual

        print("updating hoerer state")
        i+=1
        send_future = websocket.send(str(i))

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

        flag_subscribte_to_hoerer = incoming.subscribe_to_hoerer
        print(f'subscribe flag: "{flag_subscribte_to_hoerer}" ({type(flag_subscribte_to_hoerer).__name__})')
        if flag_subscribte_to_hoerer is True:
            response = dict(hoerer_state=True)

            await websocket.send(json.dumps(response))

async def main() -> None:
    async with websockets.serve(handler, WsDomain, WsPort):
        print("starting server, awaiting connections")
        # python -m websockets ws://localhost:3003
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
