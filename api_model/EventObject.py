"""
    Expectation: {
        "event": "RingingStart"|"RingingStop",
        "subscribe_to_hoerer": "now"|"onChange"
    }
"""
class EventObject:
    def __init__(self, data: dict):
        if type(data) == dict:
            self.event: str = data.get("event")
            self.subscribe_to_hoerer: str = data.get("subscribeToHoerer")
        else:
            self.event = None
