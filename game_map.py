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

    # return true if x and y are inside of the bounds of this map
    def in_bounds( self, x: int, y: int ) -> bool:

        return 0 <= x < self.width and 0 <= y < self.height
    
    # render the entire map using the console class's tile_rgb method
    def render( self, console: Console ) -> None:

        console.tiles_rgb[ 0:self.width, 0:self.height ] = self.tiles[ "dark" ]