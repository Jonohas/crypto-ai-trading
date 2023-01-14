from enum import Enum

class ActionSpace(Enum):
    BUY = 0
    HOLD = 1
    SELL = 2

class Positions(Enum):
    CLOSED = 0
    OPEN = 1