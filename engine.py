# import dependencies
from __future__ import annotations

from typing import TYPE_CHECKING

from tcod.context import Context
from tcod.console import Console
from tcod.map import compute_fov

from entity import Entity # type: ignore
from game_map import GameMap # type: ignore
from input_handlers import MainGameEventHandler
from render_functions import render_bar # type: ignore

if TYPE_CHECKING:
    from entity import Actor # type: ignore
    from game_map import GameMap
    from input_handlers import EventHandler

# manages the current state of the game
class Engine:

    #
    game_map: GameMap

    # initialize engine with a set of entities, an event handler, and the player entity
    def __init__( self, player: Actor ):

        self.event_handler: EventHandler = MainGameEventHandler( self )
        self.player = player

    # handle moves for enemy entities
    def handle_enemy_turns( self ) -> None:

        for entity in set( self.game_map.actors ) - { self.player }:
    
            if entity.ai:

                entity.ai.perform()

    # recompute the visible area based on the player's point of view
    def update_fov( self ) -> None:

        self.game_map.visible[:] = compute_fov(

            self.game_map.tiles[ "transparent" ],
            ( self.player.x, self.player.y ),
            radius = 8
        )
        # if a tile is "visible" it should be added to "explored"
        self.game_map.explored |= self.game_map.visible
            
    # render the current frame to the screen
    def render( self, console: Console, context: Context ) -> None:

        # render the game map
        self.game_map.render( console )

        # render health bar
        render_bar(
            console=console,
            current_value=self.player.fighter.hp,
            maximum_value=self.player.fighter.max_hp,
            total_width=20
        )

        # present context
        context.present( console )

        # clear console
        console.clear()