# import dependencies
import numpy as np
from tcod.console import Console

import tile_types  # type: ignore

#
class GameMap:

    # initialize game map and fill with wall tiles
    def __init__( self, width: int, height: int ):

        self.width, self.height = width, height

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