import asyncio
import os
import sys
import threading
from typing import Optional

import websockets

import json

# from pyfirmata import Arduino, util
from time import sleep

from websockets.exceptions import ConnectionClosedOK

from api_model.EventObject import EventObject, EventType

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

DialToneStopEvent = threading.Event()
DialToneLock = threading.Lock()

PhysicalHoererUpEvent = threading.Event()
DigitalHoererUpEvent = threading.Event()


async def main() -> None:
    async with websockets.serve(handler, WsDomain, WsPort):
        print("starting server, awaiting connections")
        # python -m websockets ws://localhost:3003
        await asyncio.Future()  # run forever


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
        elif flag_incoming_from_virtual == "DigitalUp":
            DigitalHoererUpEvent.set()
            handle_hoerer_change(False)
        elif flag_incoming_from_virtual == "DigitalDown":
            DigitalHoererUpEvent.clear()
            handle_hoerer_change(False)

        else:
            pass  # war als event gedacht, will so aber nicht so richtig

        flag_subscribe_to_hoerer = incoming.subscribe_to_hoerer
        print(f'subscribe flag: "{flag_subscribe_to_hoerer}" ({type(flag_subscribe_to_hoerer).__name__})')
        if type(flag_subscribe_to_hoerer) == str and flag_subscribe_to_hoerer.lower() == "now":
            await send_hoerer_state(websocket, get_hoerer_up())

        if type(flag_subscribe_to_hoerer) == str and flag_subscribe_to_hoerer.lower() == "onchange":
            # TODO: do not block
            # ✓alternatively: make browser.html open a separate ws for ringing
            await send_hoerer_change(websocket)

            # doesn't block, but websocket will be expired.
            # change_task = asyncio.create_task(send_hoerer_change(websocket))


async def send_hoerer_change(websocket):
    state = await get_hoerer_change()
    await send_hoerer_state(websocket, state)


async def send_hoerer_state(websocket, hoerer_up: bool):
    event_value: EventType = "PhysicalUp" if hoerer_up else "PhysicalDown"
    response = dict(event=event_value)
    await websocket.send(json.dumps(response))


def get_hoerer_up() -> bool:
    if board is None:
        result = PhysicalHoererUpEvent.is_set()
    else:
        read_result = board.analog[0].read()
        # print(read_result)
        if read_result <= 0.2:
            hoerer_up = True
        else:
            hoerer_up = False
            sleep(0.2)
        print("hoerer_up = " + str(hoerer_up))
        result = hoerer_up

    handle_hoerer_state(result)
    return result


def handle_hoerer_state(hoerer_up):
    if hoerer_up:
        PhysicalHoererUpEvent.set()
        RingStopEvent.set()
    else:
        PhysicalHoererUpEvent.clear()
        DialToneStopEvent.set()


async def get_hoerer_change() -> bool:
    result: Optional[bool]

    if board is None:
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: sys.stdout.write("is the hoerer Up? [yN]"))
        response: str = await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline)

        result = response.strip().lower().startswith("y")
        handle_hoerer_state(result)

    else:
        last_value = PhysicalHoererUpEvent.is_set()
        result = None
        while result is None:
            current_value = get_hoerer_up()
            if last_value is not current_value:
                result = current_value
            else:
                sleep(.02)

    # TODO: ensure that hoerer was down >1s to debounce
    handle_hoerer_change(True)
    return result


def handle_hoerer_change(play_connecting_first: bool):
    get_hoerer_up()
    if play_connecting_first and PhysicalHoererUpEvent.is_set() and not DigitalHoererUpEvent.is_set():
        print("physical hoerer went up - play connecting to digital")
        # TODO: can not prematurely end playback
        # put every playback into its own thread with its own lock
        os.system('omxplayer ./AddOnSounds/ConnectingToDigital_NowRings.mp3 &')
        sleep(6)

    if DigitalHoererUpEvent.is_set():
        if PhysicalHoererUpEvent.is_set():
            DialToneStopEvent.set()
            print("digital hoerer went up (and physical already was) - play connected to digital")
            os.system('omxplayer ./AddOnSounds/NowConnected_toVirtual.mp3 &')
        else:
            RingStopEvent.clear()
            ring_thread = threading.Thread(target=ring, name="Ringer")
            ring_thread.start()
    else:
        if PhysicalHoererUpEvent.is_set():
            DialToneStopEvent.clear()
            print("digital hoerer went down (with physical up) - play dial tone")
            dial_tone_thread = threading.Thread(target=dial_tone, name="DialTonePlayer")
            dial_tone_thread.start()
        else:
            RingStopEvent.set()


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
        print("Another thread is already ringing.")


def dial_tone() -> None:
    print("dial tone init")
    if DialToneLock.acquire(blocking=False):
        while not DialToneStopEvent.is_set():  # when run as "event based" subprocess
            print("dial tone beep")
            os.system('omxplayer ./AddOnSounds/Ring1x.mp3 &')
            sleep(3.5)

        DialToneLock.release()
    else:
        print("Another thread is already playing the dial tone.")


if __name__ == "__main__":
    asyncio.run(main())
