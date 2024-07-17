# import dependencies
from __future__ import annotations
import random
from typing import Iterator, List, Tuple, TYPE_CHECKING
import tcod

import entity_factories
from game_map import GameMap
import tile_types

if TYPE_CHECKING:
    from engine import Engine
    from entity import Entity

#
max_items_by_floor = [
    ( 1, 1 ),
    ( 4, 2 )
]

#
max_monsters_by_floor = [
    ( 1, 2 ),
    ( 4, 3 ),
    ( 6, 5 )
]

#
def get_max_value_for_floor(
    max_value_by_floor: List[Tuple[int, int]], floor: int
) -> int:
    
    current_value = 0

    for floor_minimum, value in max_value_by_floor:

        if floor_minimum > floor:

            break

        else:

            current_value = value

    return current_value

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
    
# populate a room with enemies
def place_entities( room: RectangularRoom, dungeon: GameMap, floor_number: int ) -> None:

    number_of_monsters = random.randint(
        0, get_max_value_for_floor( max_monsters_by_floor, floor_number )
    )
    number_of_items = random.randint(
        0, get_max_value_for_floor( max_items_by_floor, floor_number )
    )

    # step through each possible monster
    for i in range( number_of_monsters ):

        # generate the location of the monster in the current room
        x = random.randint( room.x1 + 1, room.x2 - 1 )
        y = random.randint( room.y1 + 1, room.y2 - 1 )

        # only place a new entity if the current tile is empty
        if not any( entity.x == x and entity.y == y for entity in dungeon.entities ):

            if random.random() < 0.8:

                # generate an orc
                entity_factories.orc.spawn( dungeon, x, y )

            else:

                # generate a troll
                entity_factories.troll.spawn( dungeon, x, y )

        # step through each item
        for i in range( number_of_items ):
            x = random.randint( room.x1 + 1, room.x2 - 1 )
            y = random.randint( room.y1 + 1, room.y2 - 1 )

            if not any( entity.x == x and entity.y == y for entity in dungeon.entities ):
                item_chance = random.random()

                if item_chance < 0.7:
                    entity_factories.health_potion.spawn( dungeon, x, y )
                elif item_chance < 0.8:
                    entity_factories.fireball_scroll.spawn( dungeon, x, y )
                elif item_chance < 0.9:
                    entity_factories.confusion_scroll.spawn( dungeon, x, y )
                else:
                    entity_factories.lightning_scroll.spawn( dungeon, x, y )
    
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
    engine: Engine
) -> GameMap:
    
    # grab the player from the engine
    player = engine.player
    
    # initialize empty game map
    dungeon = GameMap( engine, map_width, map_height, entities=[ player ] )

    # initialize a container for generated rooms
    rooms: List[ RectangularRoom ] = []

    #
    center_of_last_room = (0, 0)

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

            player.place( *new_room.center, dungeon )

        else: # all rooms after the first room

            # dig out a tunnel between this room and the previous one
            for x, y in tunnel_between( rooms[ -1 ].center, new_room.center ):

                dungeon.tiles[ x, y ] = tile_types.floor

            #
            center_of_last_room = new_room.center

        # populate the room with enemies
        place_entities( new_room, dungeon, engine.game_world.current_floor )

        #
        dungeon.tiles[ center_of_last_room ] = tile_types.down_stairs
        dungeon.downstairs_location = center_of_last_room

        # finally, append the new room to the list
        rooms.append( new_room )

    # return the generated map
    return dungeon