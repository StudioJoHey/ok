"""
    Expectation: {
        "event": "DigitalUp"|"DigitalDown"|"PhysicalUp"|"PhysicalDown",
        "subscribe_to_hoerer": "now"|"onChange"
    }
"""
from typing import Literal, Union, Optional

EventType = Union[Literal["DigitalUp", "DigitalDown", "PhysicalUp", "PhysicalDown"], str, None]
SubscribeType = Union[Literal["now", "onChange"], str, None]


class EventObject:
    event: EventType
    subscribe_to_hoerer: SubscribeType

    def __init__(self, data: dict):
        if type(data) == dict:
            self.event = data.get("event")
            self.subscribe_to_hoerer = data.get("subscribeToHoerer")
        else:
            self.event = None
