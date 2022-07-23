#Expectation: {"event": "RingingStart"|"RingingStop"}
class EventObject:
    def __init__(self, data: dict):
        if type(data) == dict:
            self.event: str = data.get("event")
            self.subscribe_to_hoerer = data.get("subscribeToHoerer")
        else:
            self.event = None
