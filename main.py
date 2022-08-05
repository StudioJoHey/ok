import math
from time import time
from typing import Literal, Union
import asyncio
import websockets
import json
import os
import sys
import signal

# exit gracefully on CTRL-c
signal.signal(signal.SIGINT, lambda x, y: sys.exit(0))

# from pyfirmata import Arduino, util
# board = Arduino("/dev/ttyACM0", baudrate=57600)


class MockAnalogPin:
    def read(_):
        return math.sin(time())


class MockDigitalPin:
    def write(_0, _1):
        return 1


class MockArduino:
    analog = [MockAnalogPin() for _ in range(8)]
    digital = [MockDigitalPin() for _ in range(8)]


board = MockArduino()

# checks for working connection
# print(board.get_firmata_version())

# Start iterator to receive input data from Arduino
# it = util.Iterator(board)
# it.start()
# board.analog[0].enable_reporting()

# url = "ws://localhost:3003"
domain = "localhost"
port = 3003


Event = Union[Literal["DigitalUp", "DigitalDown",
                      "PhysicalUp", "PhysicalDown"], str, None]


class Message:
    event: Event

    def __init__(self, data: dict):
        self.event = data.get("event")


class State:
    physical_up = False
    digital_up = False

    def get_state(self):
        if not self.physical_up and not self.digital_up:
            return "Idle"
        elif self.physical_up and not self.digital_up:
            return "Calling"
        elif not self.physical_up and self.digital_up:
            return "Ringing"
        else:
            return "Connected"


state = State()

# 4 actors, ring loop, dialtone loop, check loop and message loop


async def main() -> None:
    async with websockets.serve(handler, domain, port):
        print(f"[info] listening on {domain}:{port}")
        await asyncio.Future()  # run forever


async def handler(websocket):
    print("[debug] client connected")
    updated = asyncio.Event()
    consumer_task = asyncio.create_task(consumer_handler(websocket, updated))
    producer_task = asyncio.create_task(producer_handler(websocket, updated))
    printer_task = asyncio.create_task(printer(updated))
    ringer_task = asyncio.create_task(ringer(updated))
    dialer_task = asyncio.create_task(dialer(updated))
    updated.set()
    done, pending = await asyncio.wait(
        [consumer_task, producer_task, ringer_task, dialer_task, printer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()


async def consumer_handler(websocket, updated):
    async for message in websocket:
        try:
            incoming = json.loads(message, object_hook=Message)

        except json.decoder.JSONDecodeError:
            print(f"[error] event is not a json object: {message}")
            continue

        if incoming.event == "DigitalUp":
            state.digital_up = True
            updated.set()
        elif incoming.event == "DigitalDown":
            state.digital_up = False
            updated.set()
        else:
            print(f"[error] message had invalid event value: {incoming.event}")


async def producer_handler(websocket, updated):
    while True:
        next_physical_up = check_physical_up()
        if next_physical_up != state.physical_up:
            state.physical_up = next_physical_up
            await send_physical_state(websocket, state.physical_up)
            updated.set()
        await asyncio.sleep(0.2)


async def send_physical_state(websocket, physical_up: bool):
    event_value: Event = "PhysicalUp" if physical_up else "PhysicalDown"
    response = dict(event=event_value)
    await websocket.send(json.dumps(response))


def check_physical_up() -> bool:
    return board.analog[0].read() <= 0.2


async def printer(updated):
    while True:
        await updated.wait()
        print(f"[state] {state.get_state()}")
        updated.clear()


async def ringer(updated):
    while True:
        await updated.wait()
        while state.get_state() == "Ringing":
            print("[debug] ringing...")
            for x in range(10):
                board.digital[2].write(1)
                await asyncio.sleep(0.03)
                board.digital[2].write(0)
                board.digital[3].write(1)
                await asyncio.sleep(0.03)
                board.digital[3].write(0)
                if state.get_state() != "Ringing":
                    break
            await asyncio.sleep(1)


async def dialer(updated):
    while True:
        await updated.wait()
        while state.get_state() == "Calling":
            print("[debug] playing sound")
            # with Popen, this could probably be canceled
            os.system('omxplayer ./Sounds/Ring1x.mp3')
            for _ in range(14):
                await asyncio.sleep(0.25)
                if state.get_state() != "Calling":
                    break


if __name__ == "__main__":
    asyncio.run(main())
