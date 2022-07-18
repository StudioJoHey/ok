#Expectation: {"event": "RingingStart"|"RingingStop"}
class EventObject:
    def __init__(self, data: dict):
        if type(data) == dict:
            self.event: str = data.get("event")
        else:
            self.event = None
