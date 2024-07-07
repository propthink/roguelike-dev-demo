# import dependencies
from __future__ import annotations

import copy
from typing import Tuple, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from game_map import GameMap

#
T = TypeVar( "T", bound="Entity" )

# generic object to represent player, enemy, item, etc.
class Entity:

    # initialize object with location, glyph, and color
    def __init__(
        self,
        x: int=0,
        y: int=0,
        char: str="?",
        color: Tuple[ int, int, int ] = ( 255, 255, 255 ),
        name: str="<unnamed>",
        blocks_movement: bool = False
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks_movement = blocks_movement

    # spawn a copy of this instance at the given location
    def spawn( self: T, gamemap: GameMap, x: int, y: int ) -> T:

        clone = copy.deepcopy( self )
        clone.x = x
        clone.y = y
        gamemap.entities.add( clone )
        return clone

    # move the entity by the given amount
    def move( self, dx: int, dy:int ) -> None:

        self.x += dx
        self.y += dy