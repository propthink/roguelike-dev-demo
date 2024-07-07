# import dependencies
import copy
import tcod

from engine import Engine # type: ignore
import entity_factories
from input_handlers import EventHandler # type: ignore
from proc_gen import generate_dungeon # type: ignore

# define main
def main():

    # screen dimensions (in tiles)
    screen_width = 80
    screen_height = 50

    # map dimensions (in tiles)
    map_width = 80
    map_height = 45

    # room dimensions
    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    # monster limit
    max_monsters_per_room = 2

    # initialize tileset
    # (path, columns, rows, charmap)
    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD )

    # initialize event handler
    event_handler = EventHandler()

    # initialize player
    player = copy.deepcopy( entity_factories.player )

    # initialize game map
    game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        max_monsters_per_room=max_monsters_per_room,
        player=player
    )

    # initialize engine
    engine = Engine( event_handler=event_handler, game_map=game_map, player=player )
    
    # initialize tcod context
    # (columns, rows, tileset, title, vsync)
    with tcod.context.new_terminal(
        screen_width,
        screen_height,
        tileset=tileset,
        title="roguelike-dev-demo",
        vsync = True
    ) as context:
        
        # initialize root console
        # (width, height, order)
        root_console = tcod.console.Console( screen_width, screen_height, order="F" )

        # initialize main loop
        while True:

            # render the current frame to the screen
            engine.render( console=root_console, context=context )

            # generate the event queue
            events = tcod.event.wait()

            # engine handles events
            engine.handle_events( events )

# execute main
if __name__ == "__main__":

    main()