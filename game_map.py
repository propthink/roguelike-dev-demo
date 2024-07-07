# import dependencies
from __future__ import annotations

from typing import Iterable, TYPE_CHECKING

import numpy as np
from tcod.console import Console

import tile_types  # type: ignore

if TYPE_CHECKING:
    from entity import Entities

#
class GameMap:

    # initialize game map and fill with wall tiles
    def __init__( self, width: int, height: int, entities: Iterable[ Entity ] = () ):  # type: ignore

        self.width, self.height = width, height

        self.entities = set( entities )

        self.tiles = np.full( ( width, height ), fill_value=tile_types.wall, order="F" )

        # tiles the player can currently see
        self.visible = np.full( ( width, height ), fill_value=False, order="F" )

        # tiles the player has seen before
        self.explored = np.full( ( width, height ), fill_value=False, order="F" )

    # return true if x and y are inside of the bounds of this map
    def in_bounds( self, x: int, y: int ) -> bool:

        return 0 <= x < self.width and 0 <= y < self.height
    
    # render the entire map using the console class's tile_rgb method
    def render( self, console: Console ) -> None:

        # if a tile is in the "visible array", then draw it with the "light" color
        # if it is not visible, but it is in the explored array, then draw it with the "dark" color
        # otherwise, the default is "SHROUD"
        console.rgb[ 0:self.width, 0:self.height ] = np.select(
            condlist=[ self.visible, self.explored ],
            choicelist=[ self.tiles[ "light" ], self.tiles[ "dark" ] ],
            default=tile_types.SHROUD
        )
        # only print entities that are in the FOV
        for entity in self.entities:

            if self.visible[ entity.x, entity.y ]:

                console.print( x=entity.x, y=entity.y, string=entity.char, fg=entity.color )