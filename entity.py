# import dependencies
from __future__ import annotations

import copy
from typing import Optional, Tuple, TypeVar, TYPE_CHECKING

if TYPE_CHECKING:
    from game_map import GameMap

#
T = TypeVar( "T", bound="Entity" )

# generic object to represent player, enemy, item, etc.
class Entity:

    #
    gamemap: GameMap

    # initialize object with location, glyph, and color
    def __init__(
        self,
        gamemap: Optional[ GameMap ] = None,
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
        
        # if gamemap is not provided now then it will be set later
        if gamemap:

            self.gamemap = gamemap
            gamemap.entities.add( self )

    # spawn a copy of this instance at the given location
    def spawn( self: T, gamemap: GameMap, x: int, y: int ) -> T:

        clone = copy.deepcopy( self )
        clone.x = x
        clone.y = y
        clone.gamemap = gamemap
        gamemap.entities.add( clone )
        return clone
    
    # place this entity at a new location, handles moving across GameMaps
    def place( self, x: int, y: int, gamemap: Optional[ GameMap ] = None ) -> None:

        self.x = x
        self.y = y

        if gamemap:

            if hasattr( self, "gamemap" ): # possibly uninitialized

                self.gamemap.entities.remove( self )

            self.gamemap = gamemap

            gamemap.entities.add( self )

    # move the entity by the given amount
    def move( self, dx: int, dy:int ) -> None:

        self.x += dx
        self.y += dy