# import dependencies
from typing import Tuple

import numpy as np

# tile graphics structured type compatible with Console.tiles_rgb
graphic_dt = np.dtype(
    [
        ( "ch", np.int32 ), # unicode codepoint
        ( "fg", "3B" ), # 3 unsigned bytes for RGB colors
        ( "bg", "3B" )
    ]
)

# tile struct used for statically defined tile data
tile_dt = np.dtype(
    [
        ( "walkable", np.bool ), # true if this tile can be walked over
        ( "transparent", np.bool ), # true if this tile does not block FOV
        ( "dark", graphic_dt ), # graphics for when this tile is not in FOV
        ( "light", graphic_dt ) # graphics for when this tile is in FOV
    ]
)

# helper function for defining individual tile types
def new_tile( 
    walkable: int, 
    transparent: int, 
    dark: Tuple[ int, Tuple[ int, int, int ], Tuple[ int, int, int ] ],
    light: Tuple[ int, Tuple[ int, int, int ], Tuple[ int, int, int ] ]     
) -> np.ndarray:

        return np.array( ( walkable, transparent, dark, light ), dtype=tile_dt )

# SHROUD represents unexplored, unseen tiles
SHROUD = np.array( ( ord(" "), ( 255, 255, 255 ), ( 0, 0, 0 ) ), dtype=graphic_dt )

# floor tile
floor = new_tile(
    walkable=True,
    transparent=True,
    dark=( ord(" "), ( 255, 255, 255 ), ( 50, 50, 150 ) ),
    light=( ord(" "), ( 255, 255, 255 ), ( 200, 180, 50 ) )
)

# wall tile
wall = new_tile(
    walkable=False,
    transparent=False,
    dark=( ord(" "), ( 255, 255, 255 ), ( 0, 0, 100 ) ),
    light=( ord(" "), ( 255, 255, 255 ), ( 130, 110, 50 ) )
)

# stairs
down_stairs = new_tile(
    walkable=True,
    transparent=True,
    dark=( ord(">"), ( 255, 255, 255 ), ( 200, 180, 50 ) ),
    light=( ord(">"), ( 255, 255, 255 ), ( 200, 180, 50 ) )
)