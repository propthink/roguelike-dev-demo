# import dependencies
import tcod
from actions import EscapeAction, MovementAction  # type: ignore
from input_handlers import EventHandler # type: ignore

# define main
def main():

    # screen dimensions (in tiles)
    screen_width = 80
    screen_height = 50

    # player position
    player_x = int( screen_width / 2 )
    player_y = int( screen_height / 2 )

    # initialize event handler
    event_handler = EventHandler()

    # initialize tileset
    # (path, columns, rows, charmap)
    tileset = tcod.tileset.load_tilesheet(
        "dejavu10x10_gs_tc.png", 32, 8, tcod.tileset.CHARMAP_TCOD )
    
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
        root_console = tcod.Console( screen_width, screen_height, order="F" )

        # initialize main loop
        while True:

            # insert char
            root_console.print( x=player_x, y=player_y, string="@" )

            # present context
            context.present( root_console )

            # clear console
            root_console.clear()

            # event loop
            for event in tcod.event.wait():
                
                #
                action = event_handler.dispatch( event )

                #
                if action is None:

                    continue

                #
                if isinstance( action, MovementAction ):

                    player_x += action.dx
                    player_y += action.dy

                #
                elif isinstance( action, EscapeAction ):

                    raise SystemExit()


# execute main
if __name__ == "__main__":

    main()