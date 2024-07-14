# import dependencies
import traceback
import tcod

import color
import exceptions
import input_handlers
import setup_game

# define main
def main() -> None:

    # screen dimensions (in tiles)
    screen_width = 80
    screen_height = 50

    # initialize tileset
    # (path, columns, rows, charmap)
    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD )

    # initialize event handler
    handler: input_handlers.BaseEventHandler = setup_game.MainMenu()
    
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
        try:
            while True:

                root_console.clear()
                handler.on_render( console=root_console )
                context.present( root_console )

                try:
                    for event in tcod.event.wait():
                        context.convert_event( event )
                        handler = handler.handle_events( event )
                except Exception: # handle exceptions in game
                    traceback.print_exc() # print the error to stderr
                    # then print the error to the message log
                    if isinstance( handler, input_handlers.EventHandler ):
                        handler.engine.message_log.add_message(
                            traceback.format_exc(), color.error
                        )
        except exceptions.QuitWithoutSaving:
            raise
        except SystemExit: # save and quit
            # TODO: add the save function here
            raise
        except BaseException: # save on any other unexpected exception
            # TODO: add the save function here
            raise

# execute main
if __name__ == "__main__":

    main()