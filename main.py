# import dependencies
import copy
import traceback
import tcod

import color
from engine import Engine # type: ignore
import entity_factories
from proc_gen import generate_dungeon # type: ignore

# define main
def main():

    # screen dimensions (in tiles)
    screen_width = 80
    screen_height = 50

    # map dimensions (in tiles)
    map_width = 80
    map_height = 43

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

    # initialize player
    player = copy.deepcopy( entity_factories.player )

    # initialize engine
    engine = Engine( player=player )

    # initialize game map
    engine.game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        max_monsters_per_room=max_monsters_per_room,
        engine=engine
    )
    engine.update_fov()

    # welcome message
    engine.message_log.add_message(
        "I used to be an adventurer like you. Then I took an arrow in the knee...", color.welcome_text
    )
    
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

            root_console.clear()

            engine.event_handler.on_render( console=root_console )

            context.present( root_console )

            try:
                
                for event in tcod.event.wait():

                    context.convert_event( event )
                    engine.event_handler.handle_events( event )

            except Exception: # handle exceptions in game

                traceback.print_exc() # print error to stderr

                # then print the error to the message log
                engine.message_log.add_message( traceback.format_exc(), color.error )

# execute main
if __name__ == "__main__":

    main()