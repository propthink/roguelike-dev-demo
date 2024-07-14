# import dependencies
from __future__ import annotations

import os

from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union
import tcod.event # type: ignore
from tcod import libtcodpy # type: ignore
import actions # type: ignore
from actions import Action, PickupAction, BumpAction, WaitAction  # type: ignore
import color # type: ignore
import exceptions # type: ignore

if TYPE_CHECKING:
    from engine import Engine # type: ignore
    from entity import Item # type: ignore

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

#
CONFIRM_KEYS = {
    tcod.event.KeySym.RETURN,
    tcod.event.KeySym.KP_ENTER
}

# an event handler return value which can trigger an action or switch active handlers.
# if a handler is returned then it will become the active handler for future events.
# if an action is returned it will be attempted and if it is valid then
# MainGameEventHandler will become the active handler
ActionOrHandler = Union[ Action, "BaseEventHandler" ]

#
class BaseEventHandler( tcod.event.EventDispatch[ ActionOrHandler ] ):

    def handle_events( self, event: tcod.event.Event ) -> BaseEventHandler:

        # handle an event and return the next active event handler
        state = self.dispatch( event )

        if isinstance( state, BaseEventHandler ):

            return state
        
        assert not isinstance( state, Action ), f"{self!r} can not handle actions."

        return self
    
    def on_render( self, console: tcod.console.Console ) -> None:

        raise NotImplementedError()
    
    def ev_quit( self, event: tcod.event.Quit ) -> Optional[ Action ]:

        raise SystemExit()
    
# display a pop-up text window
class PopupMessage( BaseEventHandler ):

    def __init__( self, parent_handler: BaseEventHandler, text: str ):

        self.parent = parent_handler
        self.text = text

    def on_render( self, console: tcod.console.Console ) -> None:

        # render the parent and dim the result, then print the message on top
        self.parent.on_render( console )
        console.rgb["fg"] //= 8
        console.rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg=color.white,
            bg=color.black,
            alignment = libtcodpy.CENTER
        )

    # any key returns to the parent handler
    def ev_keydown( self, event: tcod.event.KeyDown ) -> Optional[ BaseEventHandler ]:

        return self.parent

# used to dispatch events to specific methods
class EventHandler( BaseEventHandler ):

    def __init__( self, engine: Engine ):

        self.engine = engine

    def handle_events( self, event: tcod.event.Event ) -> BaseEventHandler:

        # handle events for input handlers with an engine
        action_or_state = self.dispatch( event )

        if isinstance( action_or_state, BaseEventHandler ):

            return action_or_state
        
        if self.handle_action( action_or_state ):

            # a valid action was performed
            if not self.engine.player.is_alive:

                # the player was killed some time during or after the action
                return GameOverEventHandler( self.engine )
            
            return MainGameEventHandler( self.engine ) # return the main handler
        
        return self

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
    
    def on_render( self, console: tcod.Console ) -> None:

        self.engine.render( console )

# handles user input for actions which require special input
class AskUserEventHandler( EventHandler ):
    
    # by default, any key exits this input handler
    def ev_keydown( self, event: tcod.event.KeyDown ) -> Optional[ ActionOrHandler ]:

        if event.sym in { # ignore modifier keys
            tcod.event.KeySym.LSHIFT,
            tcod.event.KeySym.RSHIFT,
            tcod.event.KeySym.LCTRL,
            tcod.event.KeySym.RCTRL,
            tcod.event.KeySym.LALT,
            tcod.event.KeySym.RALT
        }:
            return None
        return self.on_exit()
    
    # by default any mouse click exists this input handler
    def ev_mousebuttondown( self, event: tcod.event.MouseButtonDown ) -> Optional[ ActionOrHandler ]:

        return self.on_exit()
    
    # called when the user is trying to exit or cancel an action,
    # by default this returns to the main event handler
    def on_exit( self ) -> Optional[ ActionOrHandler ]:

        return MainGameEventHandler( self.engine )
    
# this handler lets the user select an item,
# what happens then depends on the subclass
class InventoryEventHandler( AskUserEventHandler ):

    TITLE = "<missing title>"

    # render an inventory menu, which displays the items in the inventory,
    # and the letter to select them. will move to a different position based
    # on where the player is located, so the player can always see where they are
    def on_render( self, console: tcod.console.Console ) -> None:

        super().on_render( console )

        number_of_items_in_inventory = len( self.engine.player.inventory.items )

        height = number_of_items_in_inventory + 2

        if height <= 3:
            height = 3

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0
        y = 0

        width = len( self.TITLE ) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255 ),
            bg=(0, 0, 0 )
        )
        if number_of_items_in_inventory > 0:

            for i, item in enumerate( self.engine.player.inventory.items ):

                item_key = chr( ord("a") + i )

                console.print( x + 1, y + i + 1, f"({item_key}) {item.name}")

        else:

            console.print( x + 1, y + 1, "(Empty)" )

    #
    def ev_keydown( self, event: tcod.event.KeyDown ) -> Optional[ ActionOrHandler ]:

        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 26:

            try:

                selected_item = player.inventory.items[ index ]

            except IndexError:

                self.engine.message_log.add_message("Invalid entry.", color.invalid)

                return None
            
            return self.on_item_selected( selected_item )
        
        return super().ev_keydown( event )
    
    # called when the user selects a valid item
    def on_item_selected( self, item: Item ) -> Optional[ ActionOrHandler ]:

        raise NotImplementedError()
    
# handle using an inventory item
class InventoryActivateHandler( InventoryEventHandler ):

    TITLE = "Select an item to use"

    # return the action for the selected item
    def on_item_selected( self, item: Item ) -> Optional[ ActionOrHandler ]:

        return item.consumable.get_action( self.engine.player )
    
# handle dropping an inventory item
class InventoryDropHandler( InventoryEventHandler ):

    TITLE = "Select an item to drop"

    # drop this item
    def on_item_selected( self, item: Item ) -> Optional[ ActionOrHandler ]:

        return actions.DropItem( self.engine.player, item )
    
# handles asking the user for an index on the map
class SelectIndexHandler( AskUserEventHandler ):

    def __init__( self, engine: Engine ):

        # sets the cursor to the player when the handler is constructed
        super().__init__( engine )
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render( self, console: tcod.console.Console ) -> None:

        # highlight the tile under the cursor
        super().on_render( console )
        x, y = self.engine.mouse_location
        console.rgb["bg"][x, y] = color.white
        console.rgb["fg"][x, y] = color.black

    def ev_keydown( self, event: tcod.event.KeyDown ) -> Optional[ ActionOrHandler ]:

        # check for key movement or confirm. keys
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1 # holding modifier keys will speed up movement
            if event.mod & ( tcod.event.KeySym.LSHIFT | tcod.event.KeySym.RSHIFT ):
                modifier *= 5
            if event.mod & ( tcod.event.KeySym.LCTRL | tcod.event.KeySym.RCTRL ):
                modifier *= 10
            if event.mod & ( tcod.event.KeySym.LALT | tcod.event.KeySym.RALT ):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[ key ]
            x += dx * modifier
            y += dy * modifier
            # clamp the cursor to the map size
            x = max( 0, min( x, self.engine.game_map.width - 1 ) )
            y = max( 0, min ( y, self.engine.game_map.height - 1 ) )
            self.engine.mouse_location = x, y
            return None
        
        elif key in CONFIRM_KEYS:
            return self.on_index_selected( *self.engine.mouse_location )
        return super().ev_keydown( event )
    
    def ev_mousebuttondown( self, event: tcod.event.MouseButtonDown ) -> Optional[ ActionOrHandler ]:

        # left click confirms a selection
        if self.engine.game_map.in_bounds( *event.tile ):
            if event.button == 1:
                return self.on_index_selected( *event.tile )
        return super().ev_mousebuttondown( event )
    
    def on_index_selected( self, x: int, y: int ) -> Optional[ ActionOrHandler ]:

        # called when an index is selected
        raise NotImplementedError()
    
#
class LookHandler( SelectIndexHandler ):

    # lets the player look around using the keyboard
    def on_index_selected( self, x: int, y: int ) -> MainGameEventHandler:

        # return to main handler
        return MainGameEventHandler( self.engine )

# handles targeting a single enemy, only the enemy selected will be affected
class SingleRangedAttackHandler( SelectIndexHandler ):

    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action] ]
    ):
        super().__init__( engine )
        self.callback = callback

    def on_index_selected( self, x: int, y: int ) -> Optional[Action]:
        return self.callback((x, y))
    
# handles targeting an area within a given radius,
# any entity within the area will be affected
class AreaRangedAttackHandler( SelectIndexHandler ):

    def __init__(
            self,
            engine: Engine,
            radius: int,
            callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__( engine )
        self.radius = radius
        self.callback = callback

    # highlight the tile under the cursor
    def on_render( self, console: tcod.console.Console ) -> None:

        super().on_render( console )

        x, y = self.engine.mouse_location

        # draw a rect around the targeted area, so the player can see affected tiles
        console.draw_frame(
            x=x - self.radius - 1,
            y=y - self.radius - 1,
            width=self.radius ** 2,
            height=self.radius ** 2,
            fg=color.red,
            clear=False
        )

    def on_index_selected( self, x: int, y: int ) -> Optional[Action]:

        return self.callback((x, y))

#
class MainGameEventHandler( EventHandler ):
    
    # return the appropriate Action object based on event input
    def ev_keydown( self, event: tcod.event.KeyDown ) -> Optional[ ActionOrHandler ]:

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

            raise SystemExit()

        # user accesses message log history
        elif key == tcod.event.KeySym.v:

            return HistoryViewer( self.engine )

        # user attempts to pick up an item
        elif key == tcod.event.KeySym.g:

            action = PickupAction( player )

        #
        elif key == tcod.event.KeySym.i:
            
            return InventoryActivateHandler( self.engine )

        #
        elif key == tcod.event.KeySym.d:

            return InventoryDropHandler( self.engine )

        #
        elif key == tcod.event.KeySym.SLASH:

            return LookHandler( self.engine )

        # return Action object, or none if no relevant key press was detected
        return action
    
#
class GameOverEventHandler( EventHandler ):

    # handle exiting out of a finished game
    def on_quit( self ) -> None:

        if os.path.exists( "savegame.sav" ):

            os.remove( "savegame.sav" ) # deletes the active save file

        raise exceptions.QuitWithoutSaving() # avoid saving a finished game
    
    def ev_quit( self, event: tcod.event.Quit ) -> None:

        self.on_quit()
    
    # return the appropriate Action object based on event input
    def ev_keydown( self, event: tcod.event.KeyDown ) -> Optional[ Action ]:

        if event.sym == tcod.event.KeySym.ESCAPE:

            self.on_quit()
    
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
    def ev_keydown( self, event: tcod.event.KeyDown ) -> Optional[ MainGameEventHandler ]:

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

            return MainGameEventHandler( self.engine )
        
        return None