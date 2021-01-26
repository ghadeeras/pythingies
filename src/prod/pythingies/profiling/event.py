class Event:

    ENTER = 'enter'
    LEAVE = 'leave'

    def __init__(self, kind: str, name: str, time: int, thread: str):
        self.kind = kind
        self.name = name
        self.time = time
        self.thread = thread

    def __str__(self):
        return f"Event(kind : {self.kind}, name: {self.name}, time: {self.time}, thread: {self.thread})"

    @staticmethod
    def enter(name: str, time: int, thread: str):
        return Event(Event.ENTER, name, time, thread)

    @staticmethod
    def leave(name: str, time: int, thread: str):
        return Event(Event.LEAVE, name, time, thread)
