# import dependencies
from typing import Tuple

# generic object to represent player, enemy, item, etc.
class Entity:

    # initialize object with location, glyph, and color
    def __init__( self, x: int, y: int, char: str, color: Tuple[ int, int, int ] ):

        self.x = x
        self.y = y
        self.char = char
        self.color = color

    # move the entity by the given amount
    def move( self, dx: int, dy:int ) -> None:

        self.x += dx
        self.y += dy