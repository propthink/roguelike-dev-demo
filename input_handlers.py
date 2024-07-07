# import dependencies
from typing import Optional
import tcod.event
from actions import Action, EscapeAction, BumpAction  # type: ignore

# used to dispatch events to specific methods
class EventHandler( tcod.event.EventDispatch[ Action ] ):

    # exit on user request
    def ev_quit( self, event: tcod.event.Quit ) -> Optional[ Action ]:

        raise SystemExit()
    
    # return the appropriate Action object based on event input
    def ev_keydown( self, event: tcod.event.KeyDown ) -> Optional[ Action ]:

        # initialize Action object
        action: Optional[ Action ] = None

        # capture key press
        key = event.sym

        # user presses up
        if key == tcod.event.KeySym.UP:

            action = BumpAction( dx=0, dy=-1 )

        # user presses down
        elif key == tcod.event.KeySym.DOWN:

            action = BumpAction( dx=0, dy=1 )

        # user presses left
        elif key == tcod.event.KeySym.LEFT:

            action = BumpAction( dx=-1, dy=0 )

        # user presses right
        elif key == tcod.event.KeySym.RIGHT:

            action = BumpAction( dx=1, dy=0 )

        # user presses escape
        elif key == tcod.event.KeySym.ESCAPE:

            action = EscapeAction()

        # return Action object, or none if no relevant key press was detected
        return action