# import dependencies
from __future__ import annotations

from typing import Optional, TYPE_CHECKING
import tcod.event # type: ignore
from tcod import libtcodpy # type: ignore
from actions import Action, EscapeAction, BumpAction, WaitAction  # type: ignore
import color # type: ignore
import exceptions # type: ignore

if TYPE_CHECKING:
    from engine import Engine

#
MOVE_KEYS = {
    # arrow keys
    tcod.event.KeySym.UP: ( 0, -1 ),
    tcod.event.KeySym.DOWN: ( 0, 1 ),
    tcod.event.KeySym.LEFT: ( -1, 0 ),
    tcod.event.KeySym.RIGHT: ( 1, 0 ),
    tcod.event.KeySym.HOME: ( -1, 1 ),
    tcod.event.KeySym.END: ( 1, 1 ),
    tcod.event.KeySym.PAGEUP: ( -1, -1 ),
    tcod.event.KeySym.PAGEDOWN: ( 1, -1 ),
    # numpad keys
    tcod.event.KeySym.KP_1: ( -1, 1 ),
    tcod.event.KeySym.KP_2: ( 0, 1 ),
    tcod.event.KeySym.KP_3: ( 1, 1 ),
    tcod.event.KeySym.KP_4: ( -1, 0 ),
    tcod.event.KeySym.KP_6: ( 1, 0 ),
    tcod.event.KeySym.KP_7: ( -1, -1 ),
    tcod.event.KeySym.KP_8: ( 0, -1 ),
    tcod.event.KeySym.KP_9: ( 1, -1 )
}

#
WAIT_KEYS = {
    tcod.event.KeySym.KP_PERIOD,
    tcod.event.KeySym.KP_5,
    tcod.event.KeySym.KP_CLEAR
}

# used to dispatch events to specific methods
class EventHandler( tcod.event.EventDispatch[ Action ] ):

    def __init__( self, engine: Engine ):

        self.engine = engine

    def handle_events( self, event: tcod.event.Event ) -> None:

        self.handle_action( self.dispatch( event ) )

    # handle actions returned from event methods
    # returns true if the action will advance a turn
    def handle_action( self, action: Optional[ Action ] ) -> bool:

        if action is None:

            return False
        
        try:

            action.perform()

        except exceptions.Impossible as exc:

            self.engine.message_log.add_message( exc.args[0], color.impossible )

            return False # skip enemy turn on exception
        
        self.engine.handle_enemy_turns()

        self.engine.update_fov()

        return True

    def ev_mousemotion( self, event: tcod.event.MouseMotion ) -> None:

        if self.engine.game_map.in_bounds( event.tile.x, event.tile.y ):

            self.engine.mouse_location = event.tile.x, event.tile.y
    
    def ev_quit( self, event: tcod.event.quit ) -> Optional[ Action ]:

        raise SystemExit()
    
    def on_render( self, console: tcod.Console ) -> None:

        self.engine.render( console )

#
class MainGameEventHandler( EventHandler ):
    
    # return the appropriate Action object based on event input
    def ev_keydown( self, event: tcod.event.KeyDown ) -> Optional[ Action ]:

        # initialize Action object
        action: Optional[ Action ] = None

        # capture key press
        key = event.sym

        # grab the player from the engine
        player = self.engine.player

        # user attempts to move
        if key in MOVE_KEYS:

            dx, dy = MOVE_KEYS[ key ]

            action = BumpAction( player, dx, dy )

        # user attempts to wait
        elif key in WAIT_KEYS:

            action = WaitAction( player )

        # user presses escape
        elif key == tcod.event.KeySym.ESCAPE:

            action = EscapeAction( player )

        # user accesses message log history
        elif key == tcod.event.KeySym.v:

            self.engine.event_handler = HistoryViewer( self.engine )

        # return Action object, or none if no relevant key press was detected
        return action
    
#
class GameOverEventHandler( EventHandler ):

    # return the appropriate Action object based on event input
    def ev_keydown( self, event: tcod.event.KeyDown ) -> Optional[ Action ]:

        if event.sym == tcod.event.KeySym.ESCAPE:

            raise SystemExit()
    
#
CURSOR_Y_KEYS = {
    tcod.event.KeySym.UP: -1,
    tcod.event.KeySym.DOWN: 1,
    tcod.event.KeySym.PAGEUP: -10,
    tcod.event.KeySym.PAGEDOWN: 10
}

# print the history on a larger window which can be navigated
class HistoryViewer( EventHandler ):

    def __init__( self, engine: Engine ):

        super().__init__( engine )

        self.log_length = len( engine.message_log.messages )

        self.cursor = self.log_length - 1

    #
    def on_render( self, console: tcod.Console ) -> None:

        # draw the main state as the background
        super().on_render( console )

        # initialize the log console
        log_console = tcod.console.Console( console.width - 6, console.height - 6 )

        # draw a frame with a custom banner title
        log_console.draw_frame( 0, 0, log_console.width, log_console.height )

        log_console.print_box(
            0, 0, log_console.width, 1, "|Message History|", alignment=libtcodpy.CENTER
        )
        # render the mesage log using the cursor parameter
        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height -2,
            self.engine.message_log.messages[ : self.cursor + 1 ]
        )
        log_console.blit( console, 3, 3 )

    # fancy conditional movement to make it feel right
    def ev_keydown( self, event: tcod.event.KeyDown ) -> None:

        if event.sym in CURSOR_Y_KEYS:

            adjust = CURSOR_Y_KEYS[ event.sym ]

            if adjust < 0 and self.cursor == 0:

                # only move from the top to the bottom when you're on the edge
                self.cursor = self.log_length - 1

            elif adjust > 0 and self.cursor == self.log_length - 1:

                # same with bottom to top movement
                self.cursor = 0

            else:

                # otherwise move while staying clamped to the bounds of the history log
                self.cursor = max( 0, min( self.cursor + adjust, self.log_length - 1 ) )

        elif event.sym == tcod.event.KeySym.HOME:

            self.cursor = 0 # move directly to the top message

        elif event.sym == tcod.event.KeySym.END:

            self.cursor = self.log_length - 1 # move directly to the last message

        else: # any other key moves back to the main game state

            self.engine.event_handler = MainGameEventHandler( self.engine )