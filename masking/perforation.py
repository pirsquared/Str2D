from enum import Enum


class Perforation(Enum):
    """represents the state of a position in a `Mask`, `SOLID` or `PUNCHED`"""

    SOLID = 0
    PUNCHED = 1

    def toggle(self) -> "Perforation":
        """returns PUNCHED if SOLID, SOLID if PUNCHED"""
        return (Perforation.PUNCHED, Perforation.SOLID)[self.value]


SOLID = Perforation.SOLID
PUNCHED = Perforation.PUNCHED
