# import dependencies
from __future__ import annotations
import random
from typing import Iterator, List, Tuple, TYPE_CHECKING
import tcod

from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from entity import Entity

#
class RectangularRoom:

    # initialize with the x,y coordinates of the top-left corner
    def __init__( self, x: int, y: int, width: int, height: int ):

        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    # the x,y coordinates of the center of a room
    @property
    def center( self ) -> Tuple[ int, int ]:

        center_x = int( ( self.x1 + self.x2 ) / 2 )
        center_y = int( ( self.y1 + self.y2 ) / 2 )

        return center_x, center_y
    
    # the area that represents the inner portion of the room
    @property
    def inner( self ) -> Tuple[ slice, slice ]:

        return slice( self.x1 + 1, self.x2 ), slice( self.y1 + 1, self.y2 )
    
    # return true if this room overlaps with another RectangularRoom
    def intersects( self, other: RectangularRoom ) -> bool:

        return(

            self.x1 <= other.x2
            and self.x2 >= other.x1
            and self.y1 <= other.y2
            and self.y2 >= other.y1
        )
    
# builds an L-shaped tunnel between two points
def tunnel_between( 
    start: Tuple[ int, int ], end: Tuple[ int, int ]
) -> Iterator[ Tuple[ int, int ] ]:
    
    x1, y1 = start
    x2, y2 = end

    if random.random() < 0.5: # 50% chance

        # move horizontally, then vertically
        corner_x, corner_y = x2, y1

    else:

        # move vertically, then horizontally
        corner_x, corner_y = x1, y2

    # generate the coordinates for this tunnel
    for x, y in tcod.los.bresenham( ( x1, y1 ), ( corner_x, corner_y ) ).tolist():
        yield x, y
        
    for x, y in tcod.los.bresenham( ( corner_x, corner_y ), ( x2, y2 ) ).tolist():
        yield x, y

# procedural generation for dungeon maps
def generate_dungeon(
    max_rooms: int,
    room_min_size: int,
    room_max_size: int,
    map_width: int,
    map_height: int,
    player: Entity
) -> GameMap:
    
    # initialize empty game map
    dungeon = GameMap( map_width, map_height, entities=[ player ] )

    # initialize a container for generated rooms
    rooms: List[ RectangularRoom ] = []

    # step through each possible room
    for r in range( max_rooms ):

        # generate room dimensions
        room_width = random.randint( room_min_size, room_max_size )
        room_height = random.randint( room_min_size, room_max_size )

        # generate room location
        x = random.randint( 0, dungeon.width - room_width - 1 )
        y = random.randint( 0, dungeon.height - room_height - 1 )

        # RectangularRoom class makes rectangles easier to work with
        new_room = RectangularRoom( x, y, room_width, room_height )

        # run through the other rooms and see if they intersect with this one
        if any( new_room.intersects( other_room ) for other_room in rooms ):

            continue # if this room intersects, go to the next attempt

        # if there are no intersections then this room is valid
        # dig out the inner area of the current room
        dungeon.tiles[ new_room.inner ] = tile_types.floor

        # if this is the first room, where the player starts...
        if len( rooms ) == 0:

            player.x, player.y = new_room.center

        else: # all rooms after the first room

            # dig out a tunnel between this room and the previous one
            for x, y in tunnel_between( rooms[ -1 ].center, new_room.center ):

                dungeon.tiles[ x, y ] = tile_types.floor

        # finally, append the new room to the list
        rooms.append( new_room )

    # return the generated map
    return dungeon