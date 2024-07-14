from __future__ import annotations

import copy
from typing import Optional

import tcod
from tcod import libtcodpy

import color
from engine import Engine
import entity_factories
import input_handlers
from proc_gen import generate_dungeon

# load the background image and remove the alpha channel
background_image = tcod.image.load( "menu_background.png")[:, :, :3]

# return a brand new game session as an engine instance
def new_game():

    map_width = 80
    map_height = 43

    room_max_size = 10
    room_min_size = 6
    max_rooms = 30

    max_monsters_per_room = 2
    max_items_per_room = 2

    player = copy.deepcopy(entity_factories.player)

    engine = Engine(player=player)

    engine.game_map = generate_dungeon(
        max_rooms=max_rooms,
        room_min_size=room_min_size,
        room_max_size=room_max_size,
        map_width=map_width,
        map_height=map_height,
        max_monsters_per_room=max_monsters_per_room,
        max_items_per_room=max_items_per_room,
        engine=engine
    )
    engine.update_fov()

    engine.message_log.add_message(
        "I used to be an adventurer like you. Then I took an arrow in the knee...", color.welcome_text
    )
    return engine

# handles the main menu rendering and input
class MainMenu( input_handlers.BaseEventHandler ):

    def on_render( self, console: tcod.console.Console ) -> None:

        # render the main menu on a background image
        console.draw_semigraphics( background_image, 0, 0 )

        console.print(
            console.width // 2,
            console.height // 2 - 4,
            "TOMBS OF THE ANCIENT KINGS",
            fg=color.menu_title,
            alignment=libtcodpy.CENTER
        )
        console.print(
            console.width // 2,
            console.height - 2,
            "by propthink (Joe Fanelli)",
            fg=color.menu_title,
            alignment=libtcodpy.CENTER
        )
        menu_width = 24

        for i, text in enumerate(
            ["[N] New Game", "[C] Continue", "[Q] Quit"]
        ):
            console.print(
                console.width // 2,
                console.height // 2 - 2 + i,
                text.ljust( menu_width ),
                fg=color.menu_text,
                bg=color.black,
                alignment=libtcodpy.CENTER,
                bg_blend=libtcodpy.BKGND_ALPHA(64)
            )

    def ev_keydown(
        self, event: tcod.event.KeyDown
    ) -> Optional[ input_handlers.BaseEventHandler ]:
        
        if event.sym in ( tcod.event.KeySym.q, tcod.event.KeySym.ESCAPE ):
            raise SystemExit()
        elif event.sym == tcod.event.KeySym.c:
            # TODO: load the game here
            pass
        elif event.sym == tcod.event.KeySym.n:
            return input_handlers.MainGameEventHandler( new_game() )
        return None